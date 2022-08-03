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
from django.db import models
from django.db.transaction import atomic

from bk_honor.awards.constants import ApplicationStatus, StepType
from bk_honor.awards.models.managers import AvailablePeriodManager, SummaryLikeManager
from bk_honor.awards.parsers import load_from_db
from bk_honor.common.model import TimestampedModelMixin, UuidModel

from .cores import Award, Summary


class SummaryLike(UuidModel, TimestampedModelMixin):
    """奖项点赞"""

    username = models.CharField("用户名", max_length=128)
    summary = models.ForeignKey(Summary, verbose_name="奖项沉淀", on_delete=models.CASCADE, related_name="likes")

    objects = SummaryLikeManager()

    class Meta:
        db_table = "award_summary_like"
        ordering = ("-created_at",)


class Period(UuidModel, TimestampedModelMixin):
    """抽象时间段"""

    started_at = models.DateTimeField("开始时间", db_index=True)
    ended_at = models.DateTimeField("结束时间", db_index=True)

    award = models.ForeignKey(Award, verbose_name="奖项", on_delete=models.CASCADE)
    # 当前同一个奖项只存在一个需要确认时间，预留 index
    step_index = models.IntegerField("步骤索引")

    class Meta:
        abstract = True


class AvailablePeriod(Period):
    """可用时间段"""

    award = models.ForeignKey(Award, verbose_name="奖项", on_delete=models.CASCADE, related_name="available_periods")
    # Q: 为什么不直接关联 User ？
    # A: 考虑到有可能请求用户和关联用户不是同一个人，使用用户名会更灵活
    username = models.CharField("用户名", max_length=64, db_index=True)

    objects = AvailablePeriodManager()

    def __str__(self):
        return f"{self.username}-AvailablePeriod[{self.started_at}->{self.ended_at}]-{self.award.name}"

    class Meta:
        db_table = "award_available_period"


class ApprovalPeriod(Period):
    """评审时间段"""

    award = models.ForeignKey(Award, verbose_name="奖项", on_delete=models.CASCADE, related_name="approval_periods")

    def __str__(self):
        return f"ApprovalPeriod[{self.started_at}->{self.ended_at}]:[{self.award.name}-{self.step_index}]"

    class Meta:
        db_table = "award_approval_period"

    @atomic
    def update_steps(self):
        """更新所有相关联的步骤"""

        for application in self.award.applications.filter(status=ApplicationStatus.STARTED.value):
            if not application.current_step.type == StepType.APPROVAL_TIME_COLLECTION.value:
                raise ValueError(f"当前步骤[{application.current_step}]不是评审时间收集步骤")

            parser = load_from_db(application.current_step)
            parser.mark_collected()  # type: ignore
