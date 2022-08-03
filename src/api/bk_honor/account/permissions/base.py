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
from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, ClassVar, List, Tuple

from django.conf import settings
from typing_extensions import Type

from bk_honor.account.constants import ResourceRole
from bk_honor.account.constants import SystemRole as SystemRoleEnum
from bk_honor.account.models import BkUser


@dataclass
class Permission:
    codename: str
    description: str

    def __str__(self):
        return f'<Permission {self.codename}>'


@dataclass
class ObjectRole:
    """针对资源实例的角色"""

    resource: 'ProtectedResource'
    name: str
    owned_permission_names: List[str]

    def has_perm(self, perm_name: str):
        return perm_name in self.owned_permission_names


@dataclass
class SystemRole:
    """系统角色"""

    name: str
    owned_permission_names: List[str]

    def has_perm(self, perm_name: str):
        return perm_name in self.owned_permission_names


@dataclass
class ProtectedResource:
    """被权限保护的资源（实例纬度）"""

    bind_obj_class: ClassVar[Type]

    permissions: List[Permission] = field(default_factory=list)
    roles: dict = field(default_factory=dict)

    def __str__(self):
        return f"<ProtectedRes {self.bind_obj_class}>"

    def __post_init__(self):
        self._permissions_map = OrderedDict()

        # 无角色分配时，资源权限常闭
        self.add_role(ResourceRole.NOBODY.value, [])

    def user_has_permission(self, user: BkUser, perm_name: str, obj: Any) -> bool:
        """检查用户是否具有某个权限"""
        if perm_name not in self._permissions_map:
            raise ValueError(f"资源 {self} 不支持权限 {perm_name}")

        # 平台管理员可能会需要操作任意资源
        if settings.SYSTEM_ADMIN_SHOULD_OWN_ALL_RES and user.system_role == SystemRoleEnum.ADMIN.value:  # type: ignore
            return True

        role = self.get_role_of_user(user, obj)
        return role.has_perm(perm_name)

    def get_permission(self, codename: str) -> Permission:
        """获取权限"""
        return self._permissions_map[codename]

    def add_permissions(self, permissions: List[Tuple[str, str]]):
        """为资源添加权限"""
        for codename, description in permissions:
            p = Permission(codename, description)
            self.permissions.append(p)
            self._permissions_map[codename] = p

    def add_role(self, name: str, owned_permission_names: List[str]):
        """为资源添加角色"""
        for p in owned_permission_names:
            if p not in self._permissions_map:
                raise ValueError(f"资源 {self} 不支持权限 {p}")

        self.roles[name] = ObjectRole(self, name, owned_permission_names)

    def get_role(self, name: str) -> ObjectRole:
        """获取资源绑定的某个角色"""
        return self.roles[name]

    def get_role_of_user(self, user: BkUser, obj: Any) -> ObjectRole:
        """获取用户对资源的角色"""
        return self.get_role(self._get_role_of_user(user, obj))

    def _get_role_of_user(self, user: BkUser, obj: Any) -> str:
        raise NotImplementedError
