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
from typing import Dict, List, Optional

from bk_honor.awards.constants import StageStatus, StepType
from bk_honor.awards.exceptions import AlreadyNotifiedError, NotSupportStepOperation, StepConditionNotMeetError
from bk_honor.awards.parsers import Policy, StepParser, register_parser, register_policy
from bk_honor.common.notifier import get_notifier

logger = logging.getLogger(__name__)

notifier = get_notifier()


@dataclass
class NotificationPolicy(Policy):
    content_tmpl: Dict[str, str] = field(default_factory=dict)
    methods: List[str] = field(default_factory=list)
    receiver_groups: List[str] = field(default_factory=list)

    def get_user_groups(self) -> List[str]:
        return self.receiver_groups


@dataclass
class Notification(StepParser):
    """通知步骤解析器"""

    _policy: NotificationPolicy
    _policy_cls = NotificationPolicy

    receivers: List[str] = field(default_factory=list)
    contents: dict = field(default_factory=dict)
    sent: bool = False

    def __post_init__(self):
        super().__post_init__()

        self.receivers = self.load_users_from_groups()

    def enter(self):
        """前置钩子"""

    def exit(self):
        """后置钩子"""

    def operate(self, operation: str, **kwargs):
        """发送通知"""
        supported_operations = ["notify"]
        if operation not in supported_operations:
            raise NotSupportStepOperation(operation, supported_operations)

        logger.debug("going to notify with kwargs %s", kwargs)
        self.notify(**kwargs)

    def load_content_by_operation(self, operation: str) -> str:
        return self.contents[operation]

    def notify(self, force_message: Optional[str] = None, force_receivers: Optional[List[str]] = None):
        """调用发送通知方法 发送通知"""

        # TODO: 确认是否无需重复发送
        if self.sent:
            raise AlreadyNotifiedError("该步骤已通知过")

        notifier.notify(
            # TODO: content_tmpl 需要额外建模处理
            message=force_message or self._policy.content_tmpl["default"],
            methods=self._policy.methods,
            receivers=force_receivers or self.receivers,
        )

        self.sent = True
        self.sync_to_db()

    def check_condition(self) -> StageStatus:
        """检查是否能够流转到下一阶段"""
        # FIXME: 发送一次就可以退出？

        if self.sent:
            return StageStatus.FINISHED.value
        else:
            raise StepConditionNotMeetError()


register_parser(StepType.NOTIFICATION.value, Notification)
register_policy(StepType.NOTIFICATION.value, NotificationPolicy)
