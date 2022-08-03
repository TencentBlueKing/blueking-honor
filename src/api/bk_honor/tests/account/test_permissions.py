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
import pytest

from bk_honor.account.models import BkUser
from bk_honor.account.permissions.base import ProtectedResource, SystemRole
from bk_honor.account.permissions.system import role_has_perm, system_roles
from bk_honor.awards.models import Policy

pytestmark = pytest.mark.django_db


@pytest.fixture
def policy(levels):
    return Policy.objects.create(name="test", description="test", level=levels[0])


@pytest.fixture
def fake_policy_res_obj():
    fake_policy_res = type("FakePolicyRes", (ProtectedResource,), {})
    fake_policy_res.bind_obj_class = Policy

    return fake_policy_res()


class TestProtectedResource:
    """测试资源保护"""

    @pytest.mark.parametrize(
        "permissions",
        [
            [("test1", "测试权限1"), ("test2", "测试权限2")],
        ],
    )
    def test_add_permissions(self, fake_policy_res_obj, permissions):
        fake_policy_res_obj.add_permissions(permissions)
        for index, permission in enumerate(fake_policy_res_obj.permissions):
            assert permission.codename == permissions[index][0]
            assert permission.description == permissions[index][1]

    @pytest.mark.parametrize(
        "permissions,role",
        [
            [
                [("test1", "测试权限1"), ("test2", "测试权限2")],
                ("liaison", ["test1", "test2"]),
            ],
            pytest.param(
                [("test1", "测试权限1"), ("test2", "测试权限2")],
                ("liaison", ["test3", "test2"]),
                marks=pytest.mark.xfail(raises=ValueError),
            ),
        ],
    )
    def test_add_role(self, fake_policy_res_obj, permissions, role):
        fake_policy_res_obj.add_permissions(permissions)
        fake_policy_res_obj.add_role(role[0], role[1])

        assert fake_policy_res_obj.get_role(role[0]).owned_permission_names == role[1]


class TestPermissions:
    @pytest.fixture
    def foo_user(self):
        return BkUser.objects.create(username="foo", system_role="user")

    def fake_get_role_of_user(self, user, obj):
        if user.username in obj.liaisons:
            return "liaison"

        return "nobody"

    @pytest.mark.parametrize(
        "liaisons,system_role,expected",
        [
            (["bar"], "user", False),
            # 平台管理员拥有所有资源权限
            (["bar"], "admin", True),
            (["foo", "bar"], "user", True),
        ],
    )
    def test_res_has_permission(self, policy, fake_policy_res_obj, foo_user, liaisons, system_role, expected):
        """测试用户是否拥有资源权限"""
        policy.liaisons = liaisons
        policy.save()

        foo_user.system_role = system_role
        foo_user.save()

        fake_policy_res_obj._get_role_of_user = self.fake_get_role_of_user
        fake_policy_res_obj.add_permissions([("read", "读取"), ("write", "写入")])
        fake_policy_res_obj.add_role("liaison", ["read"])

        assert fake_policy_res_obj.user_has_permission(foo_user, "read", policy) == expected

    @pytest.mark.parametrize(
        "system_role,bind_permissions,sample,expected",
        [
            ("fake", ["test1", "test2"], "test1", True),
            ("fake", ["test1", "test2"], "test3", False),
        ],
    )
    def test_role_has_perm(self, system_role, bind_permissions, sample, expected):
        """测试系统角色是否拥有功能权限"""
        system_roles[system_role] = SystemRole(system_role, bind_permissions)

        assert role_has_perm(system_role, sample) == expected
