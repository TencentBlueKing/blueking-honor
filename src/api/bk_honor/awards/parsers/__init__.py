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
from dataclasses import asdict, dataclass, field
from typing import TYPE_CHECKING, ClassVar, List, Type

from dacite import from_dict
from django.conf import settings

from bk_honor.account.constants import GroupType
from bk_honor.account.models import UserGroup
from bk_honor.awards.constants import FixedUserGroup, StageStatus

if TYPE_CHECKING:
    from bk_honor.awards.models import Step

logger = logging.getLogger(__name__)


@dataclass
class Policy:
    """步骤解析策略"""

    auto_execute: bool = field(default=settings.DEFAULT_STEP_AUTO_EXECUTE)

    @classmethod
    def from_dict(cls, data: dict) -> 'Policy':
        return from_dict(cls, data)

    def get_user_groups(self) -> List[str]:
        """获取步骤所属用户组"""
        raise NotImplementedError


@dataclass
class StepParser:
    """步骤解析基类"""

    name: str
    type: str
    _db_ins: 'Step'
    _policy: Policy

    _policy_cls: ClassVar[Type[Policy]] = Policy

    def __post_init__(self):
        if isinstance(self._policy, dict):
            _policy = dict(self._policy)
            _policy.pop("name", None)
            _policy.pop("type", None)
            self._policy = from_dict(self._policy_cls, _policy)  # type: ignore

    @property
    def auto_execute(self) -> bool:
        return self._policy.auto_execute

    @classmethod
    def load_from_db(cls, instance: "Step"):
        """从数据库加载步骤解析器"""
        return cls(
            name=instance.name,
            type=instance.type,
            _db_ins=instance,
            _policy=instance.policy,
            **instance.details,  # type: ignore
        )

    def _load_users_from_fixed_group(self, group: UserGroup):
        """从固定用户组中加载绑定用户"""
        if group.id == FixedUserGroup.APPLICANT.value:
            return self._db_ins.stage.application.applicants

        if group.id == FixedUserGroup.APPLICATION_LIAISON.value:
            return self._db_ins.stage.application.liaisons

        if group.id == FixedUserGroup.AWARD_LIAISON.value:
            return self._db_ins.stage.application.award.policy.liaisons

        raise ValueError(f"未知的固定用户组: {group.id}")

    def load_users_from_groups(self):
        """从用户组中加载绑定用户"""
        all_usernames = []
        for group in UserGroup.objects.filter(id__in=self._policy.get_user_groups()):
            if group.type == GroupType.SYSTEM.value:
                all_usernames.extend(group.bindings)
                continue

            if group.type == GroupType.FIXED.value:
                all_usernames.extend(self._load_users_from_fixed_group(group))
                continue

            application = self._db_ins.stage.application
            if not application.user_groups.get(group.id):
                all_usernames.extend(application.award.user_groups.get(group.id) or [])
            else:
                all_usernames.extend(application.user_groups.get(group.id) or [])
        return list(set(all_usernames))

    def sync_to_db(self) -> 'StepParser':
        """将 details 的改动同步回数据库"""

        self._db_ins.details = self.to_dict(with_id=False)
        self._db_ins.save(update_fields=["details", "updated_at"])

        return self.load_from_db(self._db_ins)

    def to_dict(self, with_policy: bool = False, with_id: bool = True) -> dict:
        dict_ = asdict(self)
        if not with_policy:
            dict_.pop("_policy")

        if not with_id:
            dict_.pop("name")
            dict_.pop("type")

        dict_.pop("_db_ins")

        return dict_

    def enter(self):
        raise NotImplementedError

    def exit(self):
        raise NotImplementedError

    def check_condition(self) -> StageStatus:
        """检查步骤是否满足流转条件"""
        raise NotImplementedError

    def operate(self, operation: str, **kwargs):
        """操作步骤"""
        raise NotImplementedError


@dataclass
class GlobalConfig:
    default_notify_methods: List[str]
    default_broadcast_receiver_groups: List[str]
    default_approval_allow_operations: List[str]


_parsers = {}
_policies = {}


def register_policy(name: str, policy_cls: Type[Policy]):
    """注册策略类"""
    _policies[name] = policy_cls


def get_policy_cls(type_: str) -> Type[Policy]:
    """获取策略类"""
    return _policies[type_]


def register_parser(type_: str, parser: Type[StepParser]):
    """注册步骤解析器"""
    _parsers[type_] = parser


def get_parser(type_: str) -> Type[StepParser]:
    """获取步骤解析器"""
    return _parsers[type_]


def load_from_db(instance: "Step") -> StepParser:
    """从数据库加载步骤"""
    return get_parser(instance.type).load_from_db(instance=instance)


def operate_step(instance: "Step", operation: str, **kwargs) -> "Step":
    """操作步骤"""
    step_parser = load_from_db(instance)

    step_parser.operate(operation, **kwargs)
    step_parser.sync_to_db()

    return instance


def check_user_in_target_users(instance: "Step", username: str) -> bool:
    """判断当前用户与当前步骤用户组是否匹配"""

    step_parser = load_from_db(instance)
    return username in step_parser.target_users  # type: ignore
