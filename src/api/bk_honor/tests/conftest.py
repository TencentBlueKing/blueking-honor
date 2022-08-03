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
from typing import Optional

import pytest
from django.utils.timezone import now

from bk_honor.awards.models import Application, Award, Level, Policy

pytestmark = pytest.mark.django_db


@pytest.fixture
def levels():
    levels = []
    for i in range(1, 6):
        levels.append(Level.objects.create(key=f'level_{i}', name=f"等级 {i}", sort=i))

    return levels


def make_policy_by_data(levels, policy_data: list, policy_params: Optional[dict] = None):
    return Policy.objects.create(name="test_policy", stages=policy_data, level=levels[0], **policy_params or {})


def make_application_by_policy(
    policy: Policy, award_params: Optional[dict] = None, application_params: Optional[dict] = None
):
    now_time = now()
    award = Award.objects.create(
        name="test_award",
        policy=policy,
        quarter=1,
        started_at=now_time,
        ended_at=now_time,
        **award_params or {},
    )
    application = Application.objects.create(award=award, **application_params or {})
    application.generate_stages()
    return application
