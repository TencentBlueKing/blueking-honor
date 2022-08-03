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

from bk_honor.account.models import UserGroup
from bk_honor.awards.models import Step
from bk_honor.awards.parsers import load_from_db
from bk_honor.tests.conftest import make_application_by_policy, make_policy_by_data

pytestmark = pytest.mark.django_db


def get_stage(levels):
    policy_data = [{"name": "test", "steps": []}]
    application = make_application_by_policy(make_policy_by_data(levels, policy_data))
    return application.stages.first()


def get_step_parser(levels, policy):
    for step in Step.generator.generate(get_stage(levels), [policy]):
        return load_from_db(step)


class TestApproval:
    @pytest.mark.parametrize(
        "samples,expected",
        [
            (
                {
                    "type": "approval",
                    "name": "评选资格审批",
                    "approver_groups": ["group_manager"],
                    "allow_operations": ["approve", "reject", "cancel"],
                },
                {
                    "type": "approval",
                    "name": "评选资格审批",
                    "approvers": [],
                    "approved_users": [],
                    "rejected_users": [],
                    "comment": "",
                    "broadcast_sent": False,
                    "reminder_sent": False,
                },
            ),
            (
                {
                    "type": "approval",
                    "name": "评选资格审批",
                    "approver_groups": ["group_manager"],
                    "allow_operations": ["approve", "reject", "cancel"],
                },
                {
                    "type": "approval",
                    "name": "评选资格审批",
                    "approvers": [],
                    "approved_users": [],
                    "rejected_users": [],
                    "comment": "",
                    "broadcast_sent": False,
                    "reminder_sent": False,
                },
            ),
        ],
    )
    def test_generate_by_policy(self, levels, samples, expected):
        """测试生成审批步骤"""
        assert get_step_parser(levels, samples).to_dict() == expected

    @pytest.mark.parametrize(
        "with_policy,with_id,expected",
        [
            (
                True,
                True,
                {
                    "type": "approval",
                    "name": "评选资格审批",
                    "approvers": [],
                    "approved_users": [],
                    "rejected_users": [],
                    "broadcast_sent": False,
                    "reminder_sent": False,
                    "comment": "",
                    "_policy": {
                        "approver_groups": ["group_manager"],
                        "allow_operations": ["approve", "reject", "cancel"],
                        "pass_ratio": 1.0,
                        "auto_execute": False,
                        "decisive": True,
                        "broadcast": {
                            "receiver_groups": [],
                            "methods": [],
                            "content_tmpl": {"default": ""},
                            "auto_execute": False,
                        },
                        "reminder": {
                            "content_tmpl": {"default": ""},
                            "receiver_groups": ["gm"],
                            "methods": ["sms"],
                            "auto_execute": False,
                        },
                    },
                },
            ),
            (
                False,
                True,
                {
                    "type": "approval",
                    "name": "评选资格审批",
                    "approvers": [],
                    "approved_users": [],
                    "rejected_users": [],
                    "comment": "",
                    "broadcast_sent": False,
                    "reminder_sent": False,
                },
            ),
            (
                False,
                False,
                {
                    "approvers": [],
                    "approved_users": [],
                    "rejected_users": [],
                    "comment": "",
                    "broadcast_sent": False,
                    "reminder_sent": False,
                },
            ),
        ],
    )
    def test_to_dict(self, levels, with_policy, with_id, expected):
        sample = {
            "type": "approval",
            "name": "评选资格审批",
            "approver_groups": ["group_manager"],
            "allow_operations": ["approve", "reject", "cancel"],
            "decisive": True,
            "reminder": {
                "content_tmpl": {"default": ""},
                "receiver_groups": ["gm"],
                "methods": ["sms"],
                "auto_execute": False,
            },
            "broadcast": {
                "content_tmpl": {"default": ""},
                "auto_execute": False,
            },
            "auto_execute": False,
        }
        parser = get_step_parser(levels, sample)
        assert parser.to_dict(with_policy, with_id) == expected

    @pytest.mark.parametrize(
        "bindings_a, bindings_b",
        [
            (["foo"], ["bar", "baz"]),
            (["foo", "bar"], ["bar"]),
            ([], ["bar"]),
            (["foo"], []),
        ],
    )
    def test_get_approvers(self, levels, bindings_a, bindings_b):
        """测试从角色获取审批人"""
        UserGroup.objects.create(id="group_manager", name="组长")
        UserGroup.objects.create(id="gm", name="组长")
        sample = {
            "type": "approval",
            "name": "评选资格审批",
            "approver_groups": ["group_manager", "gm"],
            "allow_operations": ["approve", "reject", "cancel"],
            "reminder": {"content_tmpl": {"default": ""}, "receiver_groups": ["gm"]},
            "broadcast": {"content_tmpl": {"default": ""}, "methods": ["sms"]},
        }
        parser = get_step_parser(levels, sample)

        award = parser._db_ins.stage.application.award
        award.user_groups["group_manager"] = bindings_a
        award.user_groups["gm"] = bindings_b
        award.save()

        assert set(load_from_db(Step.generator.get(pk=parser._db_ins.pk)).approvers) == set(
            list({*bindings_a, *bindings_b})
        )
