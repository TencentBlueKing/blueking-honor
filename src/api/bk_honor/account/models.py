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
from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from bk_honor.account.constants import GroupType, SystemRole
from bk_honor.account.managers import UserGroupManager


class BkUser(AbstractBaseUser):
    """用户账号"""

    username = models.CharField("用户名", max_length=128, unique=True)
    chinese_name = models.CharField("中文名", max_length=128, blank=True, null=True)
    system_role = models.CharField(
        "系统角色", max_length=32, choices=SystemRole.get_choices(), default=SystemRole.USER.value  # type: ignore
    )

    date_joined = models.DateTimeField("首次登录时间", auto_now_add=True)

    USERNAME_FIELD = "username"

    class Meta:
        db_table = "account_user"


class UserGroup(models.Model):
    """用户组"""

    id = models.CharField("组 ID", max_length=128, primary_key=True)
    name = models.CharField("组名称", max_length=128)
    bindings = models.JSONField("绑定人员", default=list)
    type = models.CharField("组类型", max_length=32, choices=GroupType.get_choices(), default=GroupType.DYNAMIC.value)

    objects = UserGroupManager()

    def __str__(self):
        return f"{self.id}-{self.name}"

    class Meta:
        db_table = "account_user_group"
