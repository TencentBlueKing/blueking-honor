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
from typing import Dict

from bk_honor.account.constants import SystemRole as SystemRoleEnum
from bk_honor.account.permissions.base import Permission, SystemRole

system_permissions_info = [
    ("manage_policies", "管理奖项策略"),
    ("manage_awards", "管理奖项"),
    ("create_application", "创建申报"),
]

system_permissions = {x[0]: Permission(x[0], x[1]) for x in system_permissions_info}

admin_role = SystemRole(
    SystemRoleEnum.ADMIN.value, ["manage_policies", "manage_awards", "create_application"]  # type: ignore
)
normal_user_role = SystemRole(SystemRoleEnum.USER.value, ["create_application"])  # type: ignore

system_roles: Dict[str, SystemRole] = {x.name: x for x in [admin_role, normal_user_role]}


def role_has_perm(role_name: str, perm_name: str) -> bool:
    """判断某种角色是否具备某种权限"""
    role = system_roles[role_name]
    if not role:
        return False

    return perm_name in role.owned_permission_names
