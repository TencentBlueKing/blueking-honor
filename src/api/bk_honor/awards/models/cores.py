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
import datetime
import functools
import logging
from typing import Tuple

from django.db import models
from django.db.transaction import atomic
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from bk_honor.account.constants import GroupType
from bk_honor.account.models import UserGroup
from bk_honor.awards.constants import ApplicationStatus, AwardStatus, Quarter, StageStatus, StepType, SummaryStatus
from bk_honor.awards.exceptions import AlreadyLastStageError, AlreadyLastStepError, StepConditionNotMeetError
from bk_honor.awards.models.managers import (
    ApplicationManager,
    AwardManager,
    StageGenerator,
    StepGenerator,
    SummaryManager,
)
from bk_honor.awards.parsers import get_policy_cls, load_from_db
from bk_honor.common.model import TimestampedModelMixin, UuidModel

logger = logging.getLogger(__name__)


class Level(models.Model):
    """奖项级别"""

    key = models.CharField("标识", max_length=32, unique=True)
    name = models.CharField("名称", max_length=32, unique=True)
    sort = models.IntegerField("排序", unique=True)

    class Meta:
        db_table = "award_level"


class Policy(UuidModel, TimestampedModelMixin):
    """奖项策略"""

    name = models.CharField("名称", max_length=128, unique=True)
    description = models.TextField("描述", default="")
    level = models.ForeignKey(Level, verbose_name="奖项级别", on_delete=models.CASCADE)
    liaisons = models.JSONField("联系人列表", default=list)
    # Q: 为什么使用 JSON 字段，而不是对其中的字段进行建模？
    # A: 考虑到项目初期，很多字段无法固定，使用 JSON 内存对象解析能够提供灵活度，后续需求沉淀后，可以转换为 DB 字段
    periods = models.JSONField("奖项周期列表", default=list)
    stages = models.JSONField("阶段策略列表", default=list)
    raw_application_info = models.JSONField("申报策略列表", default=list)
    summary_info = models.JSONField("奖项策略字段列表", default=list)
    global_config = models.JSONField("全局配置", default=dict)
    scope = models.JSONField("组织范围", default=list, help_text="组织 ID 列表")
    logo = models.URLField("logo", null=True, blank=True)
    addons = models.JSONField("附件", null=True, blank=True, default=list)

    def __str__(self):
        return f"Policy <{self.name}-{self.pk.hex[:8]}>"

    @property
    def get_user_groups_from_steps(self):
        """从 policy steps获取动态用户组列表"""
        groups = []
        for stage in self.stages:
            for step in stage["steps"]:
                policy = get_policy_cls(step["type"]).from_dict(step)
                groups.extend(policy.get_user_groups())
        group_objs = UserGroup.objects.filter(id__in=list(set(groups)), type=GroupType.DYNAMIC.value)
        return group_objs

    @property
    def get_user_groups_from_applications(self):
        """从raw_app_info 获取动态用户组列表"""
        user_groups = self.raw_application_info["user_groups"]
        groups = [user["key"] for user in user_groups]
        group_objs = UserGroup.objects.filter(id__in=list(set(groups)), type=GroupType.SPECIFIC.value)
        return group_objs

    class Meta:
        db_table = "award_policy"
        ordering = ("-created_at",)


class Award(UuidModel, TimestampedModelMixin):
    """奖项"""

    name = models.CharField("奖项名称", max_length=128)
    description = models.TextField("奖项描述")
    year = models.IntegerField("年份", default=0)
    quarter = models.IntegerField("季度", choices=Quarter.get_choices())

    status = models.CharField(
        "状态", max_length=32, choices=AwardStatus.get_choices(), default=AwardStatus.PENDING.value
    )
    started_at = models.DateTimeField("开始时间")
    ended_at = models.DateTimeField("截止时间")

    liaisons = models.JSONField("联系人列表", default=list)
    orgs = models.JSONField("关联组织 ID 列表", default=list)

    user_groups = models.JSONField("用户组绑定", default=dict)

    policy = models.ForeignKey(Policy, verbose_name="奖项策略", on_delete=models.CASCADE, related_name="awards")
    addons = models.JSONField("附件", null=True, blank=True, default=list)
    award_slideshow = models.JSONField("奖项轮播图", null=True, blank=True, default=list)

    objects = AwardManager()

    class Meta:
        db_table = "award_award"
        ordering = ("-created_at",)

    @property
    def full_name(self) -> str:
        return f'{str(self.year)}年 {self.name}'

    def save(self, *args, **kwargs) -> None:
        if not self.started_at <= self.ended_at:
            raise ValueError("开始时间必须小于截止时间")

        super().save(*args, **kwargs)

    def next_quarter(self):
        """推进到下一季度"""
        if self.quarter == len(self.policy.periods):
            return self.year + 1, 1
        return self.year, self.quarter + 1

    def get_one_period(self) -> int:
        """获取一个周期"""
        periods = self.policy.periods
        if len(periods) == 0:
            few_months_from_next_period = 1
        elif self.quarter == len(periods):
            few_months_from_next_period = periods[0] + 12 - periods[self.quarter - 1]
        else:
            few_months_from_next_period = periods[self.quarter] - periods[self.quarter - 1]
        return few_months_from_next_period

    def __str__(self):
        return f"{self.name}-{self.status}"


class Application(UuidModel, TimestampedModelMixin):
    """申报"""

    award = models.ForeignKey(Award, verbose_name="奖项", on_delete=models.CASCADE, related_name="applications")
    applicants = models.JSONField("申请人或团队列表", default=list)
    status = models.CharField(
        "状态",
        max_length=32,
        choices=ApplicationStatus.get_choices(),
        default=ApplicationStatus.STARTED.value,
    )
    liaisons = models.JSONField("申报接口人列表", default=list)
    staffs = models.JSONField("项目成员", default=list)
    details = models.JSONField("申报详情", default=dict)

    current_step = models.ForeignKey(
        "Step", verbose_name="当前阶段", on_delete=models.SET_NULL, null=True, blank=True, related_name="applications"
    )

    user_groups = models.JSONField("用户组绑定", default=dict)

    addons = models.JSONField("附件", null=True, blank=True, default=list)
    objects = ApplicationManager()

    class Meta:
        db_table = "award_application"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Application<{self.award.name}:{self.pk.hex[:8]}>"

    @property
    def current_stage_info(self) -> str:
        """当前所处环节"""
        if self.current_step is None:
            raise ValueError("当前申报尚未开始")
        return _("%s - %s") % (self.current_step.stage.name, self.current_step.name)

    @property
    def current_stage(self) -> "Stage":
        """当前所处阶段"""
        if self.current_step is None:
            raise ValueError("当前申报尚未开始")
        return self.current_step.stage

    @functools.cached_property
    def steps(self):
        """当前申报所有阶段"""
        return Step.generator.filter(stage__in=self.stages.filter(enabled=True), enabled=True).order_by("index")

    @atomic
    def generate_stages(self):
        """生成各申报阶段"""
        for stage, policy in Stage.generator.generate(self):
            _ = list(Step.generator.generate(stage, policy["steps"]))

    @atomic
    def start(self):
        """申报流程开始"""
        if self.current_step is not None:
            raise ValueError("申报已开始")

        now_time = now()
        stage = self.stages.filter(enabled=True).order_by("created_at").first()
        step = stage.steps.filter(enabled=True).order_by("created_at").first()

        stage.start(now_time)
        step.start(now_time)

        self.current_step = step
        self.save(update_fields=["current_step", "updated_at"])

    def get_next_step(self) -> Tuple["Step", bool]:
        """获取下一个阶段"""
        if self.current_step is None:
            raise ValueError("当前申报尚未开始")

        try:
            return self.current_step.get_next_step(), False
        except AlreadyLastStepError:
            try:
                stage = self.current_step.stage.get_next_stage()
            except AlreadyLastStageError:
                raise

            return stage.steps.filter(enabled=True).order_by("created_at").first(), True  # type: ignore

    @atomic
    def next(self):
        """流转到下一阶段"""
        current_step = self.current_step
        if current_step.status == StageStatus.FINISHED.value:
            raise StepConditionNotMeetError("已完成的步骤不能再次流转")
        current_step_parser = load_from_db(current_step)
        try:
            status = current_step_parser.check_condition()
        except StepConditionNotMeetError:
            logger.exception(f"当前所处环节[{self.current_stage_info}]条件不满足")
            raise

        current_stage = current_step.stage
        now_time = now()

        # 尝试更新当前步骤状态
        current_step.end_with_status(status, now_time)

        try:
            next_step, over_stages = self.get_next_step()
        except AlreadyLastStageError:
            raise

        # 当步骤已处于阶段的最后，将同时流转 Stage
        if over_stages:
            current_stage.end_with_status(status, now_time)
            next_stage = next_step.stage
            next_stage.start(now_time)

        # 开启下一阶段
        next_step.start(now_time)
        self.current_step = next_step
        self.save(update_fields=["current_step"])

    @atomic
    def abort(self):
        """中止申报"""
        if self.current_step is None:
            raise ValueError("申报尚未开始")

        now_time = now()

        self.current_step.end_with_status(StageStatus.ABORTED.value, now_time)
        self.current_step.stage.end_with_status(StageStatus.ABORTED.value, now_time)

        self.status = ApplicationStatus.FAILED.value
        self.save(update_fields=["status", "updated_at"])

    @atomic
    def finish(self):
        """结束申报 通知获奖"""
        if self.current_step is None:
            raise ValueError("申报尚未开始")
        now_time = now()
        self.current_step.end_with_status(StageStatus.FINISHED.value, now_time)
        self.current_step.stage.end_with_status(StageStatus.FINISHED.value, now_time)
        self.status = ApplicationStatus.SUCCEED.value
        self.save(update_fields=["status", "updated_at"])

    @atomic
    def succeed(self):
        """标记申报成功"""
        self.status = ApplicationStatus.SUCCEED.value
        self.save(update_fields=["status", "updated_at"])

    @atomic
    def promote(self, validated_data: dict):
        """填写获奖宣导材料"""
        self.details = validated_data.get("promotion")
        self.save(update_fields=["details", "updated_at"])

    def update_status(self):
        """更新申报状态"""
        # 由于 application 对象在 step 更新前拿到了内存，其外键关联实例并未同步更新
        # 我们需要额外手动刷新一次
        self.current_step = Step.generator.get(pk=self.current_step.pk)
        current_step_parser = load_from_db(self.current_step)
        try:
            status = current_step_parser.check_condition()
        except StepConditionNotMeetError:
            logger.debug("当前所处环节[%s]不满足向下流转条件", self.current_step)
            return

        # 任意步骤满足中止条件时，中止申报
        if status == StageStatus.ABORTED.value:
            self.abort()
            return

        # 决定性审批步骤满足完成通过条件，申报成功
        if (
            self.current_step.type == StepType.APPROVAL.value
            and current_step_parser.decisive  # noqa
            and status == StageStatus.FINISHED.value
        ):
            try:
                # 决定性审批步骤不一定是最后一步，尝试向下进行，即使没有配置 auto_execute
                self.next()
            finally:
                # 无论是否为最后一步，只要决定性审批通过，即申报成功
                self.succeed()

            return

        # 其他普通步骤完成时，尝试判断自动流转配置
        if not current_step_parser.auto_execute:
            return

        try:
            self.next()
        except AlreadyLastStageError:
            logger.debug("Step[%s] is last step of application, skipping", current_step_parser.name)
            self.current_step.end_with_status(StageStatus.FINISHED.value, now())


class Summary(UuidModel, TimestampedModelMixin):
    """奖项沉淀"""

    details = models.JSONField("奖项沉淀详细信息", null=True, blank=True, default=dict)

    year = models.IntegerField("年份", default=0)

    status = models.CharField(
        "状态", max_length=32, choices=SummaryStatus.get_choices(), default=SummaryStatus.STARTED.value
    )

    award = models.ForeignKey(
        Award, verbose_name="奖项", null=True, blank=True, on_delete=models.CASCADE, related_name="summaries"
    )
    application = models.OneToOneField(
        Application, verbose_name="奖项申报", null=True, blank=True, on_delete=models.CASCADE, related_name="summary"
    )
    policy = models.ForeignKey(
        Policy, verbose_name="奖项策略", null=True, blank=True, on_delete=models.CASCADE, related_name="summaries"
    )

    objects = SummaryManager()

    def __str__(self):
        return f"{self.award.name}-{self.id}-Summary" if self.award else f"{self.id}-Summary"

    class Meta:
        db_table = "award_summary"
        ordering = ("-created_at",)

    @atomic
    def update_steps(self):
        """更新当前沉淀关联步骤状态"""
        if self.application.current_step.type != StepType.SUMMARY_COLLECTION.value:
            raise ValueError(f"申报<{self.application}>所处步骤[{self.application.current_step}]不是沉淀收集步骤")

        parser = load_from_db(self.application.current_step)
        parser.mark_collected()  # type: ignore

    def is_last(self) -> bool:
        """申报步骤是否是最后一步"""
        return self.application.current_step.index == self.application.steps.count() - 1  # type: ignore

    @atomic
    def update_status(self):
        """更新当前沉淀状态"""
        # TODO: 目前是根据所有流程最后一个步骤判断，后续根据类型判断会更精确
        if self.is_last():
            if self.status == SummaryStatus.STARTED.value:
                self.status = SummaryStatus.SUCCEED.value
                self.save()


class Stage(UuidModel, TimestampedModelMixin):
    """奖项阶段"""

    application = models.ForeignKey(Application, verbose_name="申请", on_delete=models.CASCADE, related_name="stages")

    name = models.CharField("名称", max_length=128)
    status = models.CharField(
        "状态",
        max_length=32,
        choices=StageStatus.get_choices(),
        default=StageStatus.PENDING.value,
    )
    details = models.JSONField("阶段详情", default=dict)
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    ended_at = models.DateTimeField("结束时间", null=True, blank=True)

    index = models.IntegerField("阶段序号")

    generator = StageGenerator()

    class Meta:
        db_table = "award_stage"
        ordering = ["index"]

    def __str__(self):
        return f"Stage<{self.name}>(<{self.application.award.name}>-App<{self.application.id.hex[:8]}>)"

    def start(self, now_time: datetime.datetime):
        """开启该阶段"""
        self.status = StageStatus.STARTED.value
        self.started_at = now_time
        self.save(update_fields=["status", "started_at", "updated_at"])
        self.save()

    def end_with_status(self, status: StageStatus, now_time: datetime.datetime):
        """结束该阶段"""
        self.status = status
        self.ended_at = now_time
        logger.info("Stage[%s] is ended with status[%s]", self.name, status)
        self.save(update_fields=["status", "updated_at", "ended_at"])
        self.save()

    def get_next_stage(self) -> "Stage":
        """获取下一个阶段"""
        if self.index >= self.application.stages.count() - 1:  # type: ignore
            # 试图扭转到下一个阶段
            now_time = now()
            self.end_with_status(StageStatus.FINISHED.value, now_time)
            logger.exception("流转申报失败，当前申报到最后一个阶段")
            raise AlreadyLastStageError()

        return self.application.stages.get(index=self.index + 1, enabled=True)  # type: ignore


class Step(UuidModel, TimestampedModelMixin):
    """奖项阶段步骤"""

    name = models.CharField("名称", max_length=128)
    stage = models.ForeignKey(Stage, verbose_name="阶段", on_delete=models.CASCADE, related_name="steps")

    type = models.CharField("类型", max_length=32, choices=StepType.get_choices())
    policy = models.JSONField("策略", default=dict)
    # 当前将不同类型的步骤字段放入 JSON，以便后续扩展
    details = models.JSONField("详情", default=dict)
    status = models.CharField(
        "状态", max_length=32, choices=StageStatus.get_choices(), default=StageStatus.PENDING.value
    )
    started_at = models.DateTimeField("开始时间", null=True, blank=True)
    ended_at = models.DateTimeField("结束时间", null=True, blank=True)

    index = models.IntegerField("步骤序号")

    generator = StepGenerator()

    def __str__(self):
        return f"Step<{self.name}>(<{self.stage.application.award.name}>-App<{self.stage.application.id.hex[:8]}>)"

    @property
    def is_last(self) -> bool:
        """是否是最后一步"""
        application = self.stage.application
        return self.index == application.steps.count() - 1

    @property
    def is_first(self) -> bool:
        """是否是第一步"""
        return self.index == 0

    @functools.cached_property
    def is_final_approval(self):
        """是否为最终审批步骤"""
        return getattr(load_from_db(self), "decisive", False)

    def start(self, now_time: datetime.datetime):
        self.status = StageStatus.STARTED.value
        self.started_at = now_time
        self.save(update_fields=["status", "started_at", "updated_at"])
        self.save()

        parser = load_from_db(self)
        parser.enter()

    def end_with_status(self, status: StageStatus, now_time: datetime.datetime):
        logger.debug(f"Step<{self.name}> end with status: {status}")
        self.status = status
        self.ended_at = now_time
        self.save(update_fields=["status", "updated_at", "ended_at"])
        self.save()

        parser = load_from_db(self)
        parser.exit()

    def get_next_step(self) -> "Step":
        """获取下一步骤"""
        if self.index >= self.stage.steps.order_by("index").last().index:  # type: ignore
            self.stage.end_with_status(StageStatus.FINISHED.value, now())
            raise AlreadyLastStepError()

        return self.stage.steps.get(enabled=True, index=self.index + 1)  # type: ignore

    class Meta:
        db_table = "award_step"
        ordering = ["index"]
