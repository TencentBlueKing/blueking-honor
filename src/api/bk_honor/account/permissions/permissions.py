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
from functools import wraps
from typing import Optional, Type

from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from bk_honor.account.permissions.resources import get_res_by_obj
from bk_honor.account.permissions.system import role_has_perm, system_permissions


def res_perm_required(perm_name, obj_cls: Optional[Type] = None, pk_from: str = 'pk'):
    """判断用户在某个资源上是否具备某种权限[views 装饰器]"""

    def decorated(func):
        @wraps(func)
        def view_func(self, request, *args, **kwargs):
            if not obj_cls:
                obj = self.get_object()
            else:
                obj = get_object_or_404(obj_cls, pk=kwargs[pk_from])
            res = get_res_by_obj(obj)
            if not res.user_has_permission(request.user, perm_name, obj):
                raise PermissionDenied(
                    f'用户[{request.user}] 在资源 {obj} 上没有[{res.get_permission(perm_name).description}]权限'
                )

            return func(self, request, *args, **kwargs)

        return view_func

    return decorated


def sys_perm_required(perm_name: str):
    """判断用户是否具备某种功能权限[views 装饰器]"""

    def decorated(func):
        @wraps(func)
        def view_func(self, request, *args, **kwargs):
            if not role_has_perm(request.user.system_role, perm_name):
                raise PermissionDenied(
                    f'用户[{request.user} - '
                    f'{request.user.system_role}] 没有[{system_permissions[perm_name].description}]权限'
                )

            return func(self, request, *args, **kwargs)

        return view_func

    return decorated
