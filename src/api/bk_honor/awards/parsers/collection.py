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

from bk_honor.awards.constants import StageStatus
from bk_honor.awards.exceptions import NotSupportStepOperation, StepConditionNotMeetError
from bk_honor.common.notifier import get_notifier

from . import Policy, StepParser
from .notification import NotificationPolicy

logger = logging.getLogger(__name__)

notifier = get_notifier()


@dataclass
class CollectionPolicy(Policy):
    """收集信息策略"""

    target_groups: List[str] = field(default_factory=list)
    # 收集信息默认自动流转
    auto_execute: bool = True

    # 提醒内容提供者
    reminder: Optional[NotificationPolicy] = None

    schemas: Optional[dict] = None
    # 和前端约定的表单生成
    # TODO: 增加中间层处理 bk_schemas -> schemas 转换
    bk_schemas: Optional[List[dict]] = None

    def get_user_groups(self) -> List[str]:
        return self.target_groups


@dataclass
class Collection(StepParser):
    """收集信息步骤解析器"""

    _policy: CollectionPolicy
    _policy_cls = CollectionPolicy

    target_users: List[str] = field(default_factory=list)
    reminder_sent: bool = False

    # 收集信息表单
    collected: bool = False
    info: dict = field(default_factory=dict)

    def __post_init__(self):
        super().__post_init__()

        self.target_users = self.load_users_from_groups()

    def exit(self):
        pass

    def enter(self):
        """步骤前置钩子"""
        if not self.enable_reminder:
            logger.debug("步骤[%s]没有指定提醒策略，跳过", self.name)
            return

        if not self.reminder_sent:
            notifier.notify(
                # TODO: content 改为支持模板
                message=self._policy.reminder.content_tmpl["default"],
                methods=self._policy.reminder.methods,
                receivers=self.target_users,
            )

            self.reminder_sent = True
            self.sync_to_db()

    @property
    def enable_reminder(self) -> bool:
        return self._policy.reminder is not None

    def check_condition(self) -> StageStatus:
        if self.collected:
            return StageStatus.FINISHED.value

        raise StepConditionNotMeetError("收集信息步骤没有收集到信息")

    def operate(self, operation: str, **kwargs):
        supported_operations = ["collect"]
        if operation not in supported_operations:
            raise NotSupportStepOperation(operation, supported_operations)

        logger.debug("going to notify with kwargs %s", kwargs)
        self.collect(**kwargs)

    def collect(self, data: dict):
        """收集"""
        # TODO: 校验收集信息的各个字段是否和策略中定义一致，由于当前使用了 bk_schemas，缺少一层抽象，暂时先不做校验
        self.info = data
        self.collected = True

    def mark_collected(self):
        """标记已收集"""
        self.collected = True
        self.sync_to_db()
