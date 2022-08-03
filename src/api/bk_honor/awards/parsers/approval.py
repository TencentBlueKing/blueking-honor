"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from django.conf import settings

from bk_honor.awards.constants import ApprovalOperation, StageStatus, StepType
from bk_honor.awards.exceptions import NotSupportStepOperation, StepConditionNotMeetError
from bk_honor.awards.parsers import Policy, StepParser, register_parser, register_policy
from bk_honor.common.notifier import get_notifier

from .notification import NotificationPolicy

logger = logging.getLogger(__name__)

notifier = get_notifier()


@dataclass
class ApprovalPolicy(Policy):
    approver_groups: List[str] = field(default_factory=list)
    allow_operations: List[str] = field(default_factory=list)
    # 审批通过人数比例，默认需要全部审批通过
    pass_ratio: float = 1.0
    # 针对评委的提醒
    reminder: Optional[NotificationPolicy] = None
    # 针对申报人的通知
    broadcast: Optional[NotificationPolicy] = None

    # 是否是决定性的审批，如果是，则在审批过后，将切换申报至 "获奖" 状态
    decisive: bool = False

    def get_user_groups(self) -> List[str]:
        return self.approver_groups


@dataclass
class Approval(StepParser):
    """审批步骤解析器"""

    _policy: ApprovalPolicy
    _policy_cls = ApprovalPolicy

    approvers: List[str] = field(default_factory=list)
    approved_users: List[str] = field(default_factory=list)
    rejected_users: List[str] = field(default_factory=list)
    comment: str = ""

    broadcast_sent: bool = False
    reminder_sent: bool = False

    def __post_init__(self):
        super().__post_init__()

        self.approvers = self.load_users_from_groups()

    @property
    def enable_broadcast(self) -> bool:
        return self._policy.broadcast is not None

    @property
    def enable_reminder(self) -> bool:
        return self._policy.reminder is not None

    @property
    def decisive(self) -> bool:
        return self._policy.decisive

    def enter(self):
        """步骤前置钩子"""
        if not self.enable_reminder:
            logger.debug("步骤[%s]没有指定提醒策略，跳过", self.name)
            return

        if not self.reminder_sent:
            notifier.notify(
                message=self._policy.reminder.content_tmpl["default"],
                methods=self._policy.reminder.methods,
                receivers=self.approvers,
            )

            self.reminder_sent = True
            self.sync_to_db()

    def exit(self):
        """步骤后置钩子"""
        if not self.enable_broadcast:
            logger.info("步骤[%s]没有指定通知策略，跳过", self.name)
            return

        try:
            status = self.check_condition()
        except NotSupportStepOperation:
            logger.warning("步骤[%s]退出时未满足完成条件", self.name)
            return

        if not self.broadcast_sent:

            notifier.notify(
                # TODO: content_tmpl 需要额外建模处理
                message=self._policy.broadcast.content_tmpl.get(self._get_content_by_status(status)),
                methods=self._policy.broadcast.methods,
                receivers=self.approvers,
            )

            self.broadcast_sent = True
            self.sync_to_db()

    @staticmethod
    def _get_content_by_status(status: StageStatus) -> str:
        _map = {
            StageStatus.FINISHED.value: ApprovalOperation.APPROVE.value,
            StageStatus.ABORTED.value: ApprovalOperation.REJECT.value,
        }

        return _map[status]

    def check_condition(self) -> StageStatus:
        """检查审批步骤是否完成"""

        # TODO: 根据配置，允许一人审批即通过  or 允许满足人数审批即通过
        if settings.ANY_PASS and self.approved_users:
            return StageStatus.FINISHED.value

        if self.approved_users and len(self.approved_users) >= len(self.approvers) * self._policy.pass_ratio:
            return StageStatus.FINISHED.value

        if self.rejected_users and len(self.rejected_users) >= (1 - self._policy.pass_ratio) * len(self.approvers):
            return StageStatus.ABORTED.value

        raise StepConditionNotMeetError()

    def _check_if_operated(self, operator: str) -> bool:
        return operator in self.approved_users or operator in self.rejected_users

    def approve(self, approver: str, comment: Optional[str] = None):
        """通过"""
        comment = comment or settings.DEFAULT_APPROVED_COMMENT
        if ":" in comment and comment.count(":") == 1:
            comment = comment.split(":")[1]
        if self._check_if_operated(approver):
            logger.warning("步骤[%s]审批人：%s 已操作过该审批, 此次操作忽略", self.name, approver)
            return

        self.approved_users.append(approver)
        self.comment += f"{approver}: {comment}\n"

    def reject(self, rejecter: str, comment: str):
        """驳回"""
        if self._check_if_operated(rejecter):
            logger.warning("步骤[%s]审批人：%s 已操作过该审批, 此次操作忽略", self.name, rejecter)
            return

        self.rejected_users.append(rejecter)
        self.comment += f"{rejecter}: {comment}\n"

    def recommend(self, details: dict):
        """转推荐"""

    def operate(self, operation: str, **kwargs):
        """操作"""
        allow_operations = self._policy.allow_operations or ApprovalOperation.get_values()

        if not hasattr(self, operation):
            raise NotSupportStepOperation(operation, allow_operations)

        if operation not in allow_operations:
            raise NotSupportStepOperation(operation, allow_operations)

        return getattr(self, operation)(**kwargs)


register_parser(StepType.APPROVAL.value, Approval)
register_policy(StepType.APPROVAL.value, ApprovalPolicy)
