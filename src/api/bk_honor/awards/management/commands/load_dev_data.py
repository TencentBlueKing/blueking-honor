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
import random
from datetime import datetime
from typing import Any

from django.core.management.base import BaseCommand, CommandParser
from django.db.transaction import atomic
from django.utils.timezone import now

from bk_honor.awards.models import Application, Award, Policy, Summary

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "load fake fixtures(awards, applications), please run after load_policies_from_yaml"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--applicants", type=str, help="申请人池，填写 username 列表，形如：foo,bar")
        parser.add_argument("--liaisons", type=str, help="奖项接口人池，填写 username 列表，形如：foo,bar")
        parser.add_argument("--staffs", type=str, help="团队成员池，填写 username 列表，形如：foo,bar")

        parser.add_argument("--material_title", type=str, help="奖项沉淀标题，填写 username 列表，形如：foo,bar")
        parser.add_argument("--winning_team_name", type=str, help="奖项沉淀获胜团队，填写 username 列表，形如：foo,bar")
        parser.add_argument("--deeds_introduction", type=str, help="奖项沉淀描述，填写 username 列表，形如：foo,bar")
        parser.add_argument("--team_members", type=str, help="奖项沉淀团队成员，填写 username 列表，形如：foo,bar")
        parser.add_argument("--funding_sys_name", type=str, help="奖项沉淀经费系统名称，填写 username 列表，形如：foo,bar")

    def handle(self, *args: Any, **options: Any):
        """从已有的策略中创建假数据, 仅供开发测试使用"""
        applicants = options["applicants"].split(",")
        liaisons = options["liaisons"].split(",")
        staffs = options["staffs"].split(",")

        material_title = options["material_title"].split(",")
        winning_team_name = options["winning_team_name"].split(",")
        deeds_introduction = options["deeds_introduction"].split(",")
        team_members = options["team_members"].split(",")
        funding_sys_name = options["funding_sys_name"].split(",")

        now_time = now()
        award_per_policy = 3
        application_per_award = 3
        award_created_count = application_created_count = summary_created_count = 0

        with atomic():
            for p in Policy.objects.filter(enabled=True):
                for year in range(now_time.year - award_per_policy, now_time.year + 1):
                    quarter = random.randint(1, 4)
                    started_at = datetime(year, quarter * 3 - 2, 1)
                    ended_at = datetime(year, quarter * 3, 1)

                    award, _ = Award.objects.get_or_create(
                        name=f"{year} Q{quarter} {p.name}",
                        year=year,
                        description=f"请大家踊跃申报 {year}年 Q{quarter} {p.name}",
                        quarter=quarter,
                        policy=p,
                        started_at=started_at,
                        ended_at=ended_at,
                    )
                    award_created_count += 1

                    for i in range(random.randint(1, application_per_award)):
                        application = Application.objects.apply(
                            award,
                            {
                                'applicants': random.choices(applicants),
                                'liaisons': random.choices(liaisons),
                                'staffs': random.choices(staffs),
                            },
                        )
                        # 注释3行运行后成申报数据，不注释后运行即生成申报完成奖项，可以进行奖项沉淀创建
                        for a in range(application.stages.all().count()):
                            application.next()
                        application.finish()

                        application_created_count += 1
                    summary, _ = Summary.objects.get_or_create(
                        award=award,
                        material_title=random.choice(material_title),
                        winning_team_name=random.choice(winning_team_name),
                        deeds_introduction=random.choice(deeds_introduction),
                        team_members=random.choice(team_members),
                        funding_sys_name=random.choice(funding_sys_name),
                    )
                    summary_created_count += 1

                logger.info(
                    "Award created: %s, Application created: %s, summary_created_count: %s",
                    award_created_count,
                    application_created_count,
                    summary_created_count,
                )
