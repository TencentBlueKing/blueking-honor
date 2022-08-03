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
from pathlib import Path

import pytest
from django.conf import settings

from bk_honor.awards.constants import StageStatus
from bk_honor.awards.exceptions import AlreadyLastStageError
from bk_honor.awards.parsers import load_from_db
from bk_honor.awards.presets import load_data_from_path
from bk_honor.tests.conftest import make_application_by_policy, make_policy_by_data

pytestmark = pytest.mark.django_db


class TestStage:
    @pytest.mark.parametrize(
        "policy_data,expected",
        [
            (
                [
                    {
                        "name": "预审",
                        "steps": [
                            {
                                "type": "approval",
                                "name": "评选资格审批",
                                "approver_groups": ["gm"],
                            },
                        ],
                    },
                    {
                        "name": "初审",
                        "steps": [
                            {
                                "type": "approval",
                                "name": "奖项接口人审批",
                                "approver_groups": ["liaison"],
                                "allow_operations": ["approve", "reject", "recommend"],
                            },
                            {
                                "type": "notification",
                                "name": "通知审批结果",
                                "receiver_groups": ["liaison"],
                                "methods": ["email"],
                            },
                        ],
                    },
                ],
                [
                    [
                        {
                            "name": "评选资格审批",
                            "type": "approval",
                            "approved_users": [],
                            "rejected_users": [],
                            "approvers": [],
                            "comment": "",
                            "broadcast_sent": False,
                            "reminder_sent": False,
                        }
                    ],
                    [
                        {
                            "name": "奖项接口人审批",
                            "type": "approval",
                            "approved_users": [],
                            "rejected_users": [],
                            "approvers": [],
                            "comment": "",
                            "broadcast_sent": False,
                            "reminder_sent": False,
                        },
                        {"name": "通知审批结果", "type": "notification", "receivers": [], "contents": {}, "sent": False},
                    ],
                ],
            ),
        ],
    )
    def test_stages_generate(self, levels, policy_data, expected):
        """测试从 policy 生成 stage"""
        application = make_application_by_policy(make_policy_by_data(levels, policy_data))
        # 检查 Stage
        assert application.stages.all().count() == len(policy_data)
        # 检查 Step
        for index, stage in enumerate(application.stages.all().order_by("created_at")):
            steps_data = [load_from_db(step).to_dict() for step in stage.steps.all().order_by("created_at")]
            assert steps_data == expected[index]

    @pytest.mark.parametrize(
        "policy_data,expected",
        [
            # 同一个阶段内流转
            (
                [
                    {
                        "name": "stage1",
                        "steps": [
                            {"type": "approval", "name": "step1", "approver_groups": ["gm"]},
                            {
                                "type": "notification",
                                "name": "step2",
                                "receiver_groups": ["liaison"],
                                "methods": ["email"],
                            },
                        ],
                    },
                ],
                [
                    # 第一进入时
                    {
                        "stage": {"name": "stage1", "status": StageStatus.STARTED.value},
                        "step": {"name": "step1", "status": StageStatus.STARTED.value},
                    },
                    # 进入下一步骤，但未切换 Stage
                    {
                        "stage": {"name": "stage1", "status": StageStatus.STARTED.value},
                        "step": {"name": "step2", "status": StageStatus.STARTED.value},
                    },
                ],
            ),
            # 跨阶段流转
            (
                [
                    {
                        "name": "stage1",
                        "steps": [{"type": "approval", "name": "step1", "approver_groups": ["gm"]}],
                    },
                    {
                        "name": "stage2",
                        "steps": [
                            {
                                "type": "approval",
                                "name": "step1",
                                "approver_groups": ["liaison"],
                                "allow_operations": ["approve", "reject", "recommend"],
                            },
                        ],
                    },
                ],
                [
                    # 第一进入时
                    {
                        "stage": {"name": "stage1", "status": StageStatus.STARTED.value},
                        "step": {"name": "step1", "status": StageStatus.STARTED.value},
                    },
                    # 进入下一步骤，但未切换 Stage
                    {
                        "stage": {"name": "stage2", "status": StageStatus.STARTED.value},
                        "step": {"name": "step1", "status": StageStatus.STARTED.value},
                    },
                ],
            ),
            # 已流转到最后一个步骤
            pytest.param(
                [
                    {
                        "name": "stage1",
                        "steps": [{"type": "approval", "name": "step1", "approver_groups": ["gm"]}],
                    },
                ],
                [
                    {
                        "stage": {"name": "stage1", "status": StageStatus.STARTED.value},
                        "step": {"name": "step1", "status": StageStatus.STARTED.value},
                    },
                ],
                marks=pytest.mark.xfail(raises=AlreadyLastStageError),
            ),
        ],
    )
    def test_stage_next(self, levels, policy_data, expected):
        """测试 stage 流转"""
        application = make_application_by_policy(make_policy_by_data(levels, policy_data))
        application.start()
        assert application.current_step.name == expected[0]["step"]["name"]
        assert application.current_step.status == expected[0]["step"]["status"]
        assert application.current_stage.name == expected[0]["stage"]["name"]
        assert application.current_stage.status == expected[0]["stage"]["status"]

        application.next()
        assert application.current_step.name == expected[1]["step"]["name"]
        assert application.current_step.status == expected[1]["step"]["status"]
        assert application.current_stage.name == expected[1]["stage"]["name"]
        assert application.current_stage.status == expected[1]["stage"]["status"]

    def test_presets_load(self):
        """测试 presets 加载"""
        data = load_data_from_path(settings.BASE_DIR / Path("awards/presets/*.yaml"))
        for policy in data["policies"]:
            make_application_by_policy(policy)
