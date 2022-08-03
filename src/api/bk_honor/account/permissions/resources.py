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
from typing import Any

from bk_honor.account.constants import ResourceRole
from bk_honor.account.models import BkUser
from bk_honor.account.permissions.base import ProtectedResource
from bk_honor.awards.models import Application, Award, Policy, Step
from bk_honor.awards.parsers import load_from_db
from bk_honor.awards.parsers.approval import Approval


class PolicyRes(ProtectedResource):
    """策略资源"""

    bind_obj_class = Policy

    def _get_role_of_user(self, user: BkUser, obj: Policy) -> str:
        if user.username in obj.liaisons:
            return ResourceRole.LIAISON.value

        return ResourceRole.NOBODY.value


policy_res = PolicyRes()
policy_res.add_permissions(
    [
        ("read", "读取策略"),
        ("create", "创建策略"),
        ("update", "修改策略"),
        ("delete", "删除策略"),
    ]
)
policy_res.add_role(ResourceRole.LIAISON.value, ["read", "create", "update", "delete"])


class AwardRes(ProtectedResource):
    """奖项资源"""

    bind_obj_class = Award

    def _get_role_of_user(self, user: BkUser, obj: Award) -> str:
        liaisons_group = [obj.liaisons, obj.policy.liaisons]
        if any(user.username in x for x in liaisons_group):
            return ResourceRole.LIAISON.value

        # TODO: 将角色与权限配置放入 yaml 文件配置，可以由用户自定义
        # 当前临时作为 liaison 存在
        if any(user.username in names for _, names in obj.user_groups.items()):
            return ResourceRole.LIAISON.value

        return ResourceRole.NOBODY.value


award_res = AwardRes()
award_res.add_permissions(
    [
        ("read", "读取奖项"),
        ("update", "修改奖项"),
        ("copy", "复制奖项"),
        ("delete", "删除奖项"),
        ("apply", "申请奖项"),
        ("promote", "宣导奖项"),
    ]
)
award_res.add_role(ResourceRole.LIAISON.value, ["read", "update", "copy", "delete", "apply", "promote"])
award_res.add_role(ResourceRole.NOBODY.value, ["read"])


class ApplicationRes(ProtectedResource):
    """申报资源"""

    bind_obj_class = Application

    def _get_role_of_user(self, user: BkUser, obj: Application) -> str:
        username = user.get_username()
        liaisons_group = [obj.liaisons, obj.award.liaisons, obj.award.policy.liaisons]
        if any(username in x for x in liaisons_group):
            return ResourceRole.LIAISON.value

        # TODO: 将角色与权限配置放入 yaml 文件配置，可以由用户自定义
        # 当前临时作为 liaison 存在
        if any(user.username in names for _, names in obj.user_groups.items()):
            return ResourceRole.LIAISON.value

        if any(user.username in names for _, names in obj.award.user_groups.items()):
            return ResourceRole.LIAISON.value

        if username in obj.staffs:
            return ResourceRole.STAFF.value

        if username in obj.applicants:
            return ResourceRole.APPLICANT.value

        return ResourceRole.NOBODY.value


application_res = ApplicationRes()
application_res.add_permissions(
    [
        ("read", "读取申报"),
        ("update", "修改申报"),
        ("delete", "删除申报"),
        ("export", "导出申报"),
        ("next", "流转奖项申报到下一阶段"),
        ("abort", "中止申报"),
        ("finish", "结束申报"),
    ]
)
application_res.add_role(ResourceRole.LIAISON.value, ["read", "update", "delete", "export", "next", "abort", "finish"])
application_res.add_role(ResourceRole.APPLICANT.value, ["read", "update", "delete", "export"])
application_res.add_role(ResourceRole.STAFF.value, ["read"])


class StepRes(ProtectedResource):

    bind_obj_class = Step

    def _get_role_of_user(self, user: BkUser, obj: Step) -> str:
        parser = load_from_db(obj)
        username = user.get_username()

        # TODO: 确定接口人是否能够审批
        # application = obj.stage.application
        # liaisons_group = [application.liaisons, application.award.liaisons, application.award.policy.liaisons]
        # if any(username in x for x in liaisons_group):
        #     return "liaison"

        if not isinstance(parser, Approval):
            return ResourceRole.NOBODY.value

        if username in parser.approvers:
            return ResourceRole.APPROVER.value

        return ResourceRole.NOBODY.value


step_res = StepRes()
step_res.add_permissions(
    [
        ("update", "通过审批"),
        ("approve", "通过审批"),
        ("reject", "驳回审批"),
    ]
)
step_res.add_role(ResourceRole.LIAISON.value, ["approve", "reject", "update"])
step_res.add_role(ResourceRole.APPROVER.value, ["approve", "reject", "update"])


res_map = {x.bind_obj_class: x for x in [policy_res, award_res, application_res, step_res]}


def get_res_by_obj(obj: Any) -> ProtectedResource:
    """根据对象获取资源"""
    try:
        return res_map[type(obj)]
    except KeyError:
        raise ValueError(f"不存在权限资源类型: {type(obj)}")
