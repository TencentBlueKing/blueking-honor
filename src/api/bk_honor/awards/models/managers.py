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
import itertools
import logging
import re
from typing import TYPE_CHECKING, List, Optional

import intervaltree
from django.db import models
from django.db.transaction import atomic

from bk_honor.account.constants import SystemRole
from bk_honor.awards.constants import ApplicationStatus, StageStatus, StepType
from bk_honor.awards.parsers import check_user_in_target_users, load_from_db
from bk_honor.common.error_codes import error_codes
from bk_honor.common.intervaltree import EnhancedIntervalTree

if TYPE_CHECKING:
    from bk_honor.awards.models import Application, Award, Stage, Step, Summary

logger = logging.getLogger(__name__)


class StepGenerator(models.Manager):
    """步骤生成器"""

    def generate(self, stage: "Stage", step_policies: list):
        """通过 Stage 信息生成步骤"""

        for policy in step_policies:
            existed_steps_count = stage.application.steps.count()

            step, _ = self.get_or_create(
                stage=stage, type=policy["type"], name=policy["name"], policy=policy, index=existed_steps_count
            )

            step.details = load_from_db(step).to_dict(with_id=False)
            step.save(update_fields=["details"])
            yield step

    def check_step_status(self, step: "Step"):
        """检查步骤状态"""

        if step.type != StepType.APPROVAL.value:
            raise error_codes.OPERATION_NOT_SUPPORTED.format(f"当前步骤类型 {step.type} 不支持审批")

        if step.status != StageStatus.STARTED.value:
            raise error_codes.APPLICATION_STEP_NOT_STARTED


class StageGenerator(models.Manager):
    """阶段生成器"""

    def generate(self, application: "Application"):
        """通过 Application 信息生成阶段"""

        for index, policy in enumerate(application.award.policy.stages):
            # TODO: add global config
            stage, _ = self.get_or_create(application=application, index=index, name=policy["name"])
            yield stage, policy


class ApplicationManager(models.Manager):
    """申报奖项 管理"""

    def apply(self, award: "Award", validated_data: dict):
        """发起申报"""

        # TODO: 同步奖项的用户组到申报信息中， 目前是区分部门gm审批所以发起申报时同步更新到用户组中

        user_groups_info = {}
        user_groups = award.policy.get_user_groups_from_applications
        for group in user_groups:
            if group.id in validated_data["details"]:
                user_groups_info[group.id] = validated_data["details"][group.id]
        validated_data["user_groups"] = user_groups_info

        application = self.create(award=award, **validated_data)
        application.generate_stages()
        application.start()
        return application

    def check_application_steps_type(self, award: "Award", type: str):
        # 判断某个奖项申报的所有团队申报均处于同一个阶段类型 type
        applications = award.applications.filter(enabled=True, status=ApplicationStatus.STARTED.value)
        if not applications:
            return False
        if all(application.current_step.type == type for application in applications):  # type: ignore
            return True
        return False


class AwardManager(models.Manager):
    """奖项 管理"""

    def create_award(self, **kwargs):
        """创建奖项"""
        started_at = kwargs.get("started_at", None)
        policy = kwargs["policy"]
        kwargs["year"] = started_at.year
        kwargs["name"] = f'{started_at.year}年 Q{kwargs["quarter"]} {kwargs["name"]}'
        creating_user_groups = kwargs["user_groups"]
        user_groups_in_policy = policy.get_user_groups_from_steps
        if not len(creating_user_groups) == user_groups_in_policy.count():
            raise ValueError("用户组数量不匹配")

        if set(creating_user_groups.keys()).difference(set(user_groups_in_policy.values_list("id", flat=True))):
            raise ValueError("用户组内容不匹配")

        obj = super().create(**kwargs)
        return obj

    def bulk_copy(self, pks: list):
        """批量复制"""

        copied_awards = []
        for pk in pks:
            copied_awards.append(self.copy(pk))

        return copied_awards

    def get_next_period(self, award):
        """获取下一个阶段"""
        next_period = {}
        next_year, next_quarter = award.next_quarter()
        few_months_from_next_period = award.get_one_period()

        new_started_at = award.ended_at
        new_ended_at = award.ended_at + datetime.timedelta(days=few_months_from_next_period * 30)
        new_name = award.name.replace(str(award.year), str(next_year))
        pattern = re.compile(r'Q\d')
        new_name = pattern.sub(f"Q{next_quarter}", new_name)
        if not self.filter(name=new_name).exists():
            next_period["name"] = new_name
            next_period["year"] = next_year
            next_period["quarter"] = next_quarter
            next_period["started_at"] = new_started_at
            next_period["ended_at"] = new_ended_at
            return next_period
        return self.get_next_period(self.filter(name=new_name, enabled=True).first())

    def copy(self, pk):
        """复制 并新建奖项"""
        award = self.get(pk=pk)
        next_period = self.get_next_period(award)

        return self.create(
            status=award.status,
            description=award.description,
            liaisons=award.liaisons,
            orgs=award.orgs,
            addons=award.addons,
            policy=award.policy,
            award_slideshow=award.award_slideshow,
            user_groups=award.user_groups,
            **next_period,
        )

    def get_approval_awards(self, award_queryset, request):
        """获取待反馈评审时间的奖项列表"""
        award_ids = []
        for award in award_queryset:
            if request.user.system_role == SystemRole.ADMIN.value:  # type: ignore
                if award.applications.check_application_steps_type(award, StepType.APPROVAL_TIME_COLLECTION.value):
                    award_ids.append(award.id)
            elif request.user.system_role == SystemRole.USER.value:  # type: ignore
                applications = award.applications.filter(enabled=True, status=ApplicationStatus.STARTED.value)
                if award.applications.check_application_steps_type(award, StepType.APPROVAL_TIME_COLLECTION.value):
                    if check_user_in_target_users(applications.first().current_step, request.user.username):
                        award_ids.append(award.id)
            else:
                raise error_codes.APPLICATION_USER_PERMISSION_ERROR
        return award_ids


class SummaryManager(models.Manager):
    """奖项汇总 管理"""

    def create_summary(self, award: "Award", application: "Application", validated_data: dict):
        """创建奖项沉淀"""
        if self.filter(award=validated_data["award_id"], application=application, enabled=True).exists():
            raise error_codes.AWARD_SUMMARY_ALREADY_EXISTS
        summary = self.create(award=award, application=application, **validated_data)
        return summary

    def create_annual_summary(self, validated_data: dict):
        """创建年度奖项沉淀"""
        summary = self.create(**validated_data)
        return summary


class SummaryLikeManager(models.Manager):
    """奖项沉淀点赞 管理"""

    def update_summary_like(self, summary: "Summary", username: str):
        """更新奖项沉淀点赞"""
        obj = self.filter(summary=summary, username=username)
        if obj.exists():
            obj.delete()
        else:
            obj = self.create(summary=summary, username=username)
        return obj


class AvailablePeriodManager(models.Manager):
    """可用时间段 管理"""

    @staticmethod
    def _merge_periods(periods: list) -> intervaltree.IntervalTree:
        """合并时间段"""
        intervals = [[int(period["started_at"]), int(period["ended_at"])] for period in periods]
        tree = intervaltree.IntervalTree.from_tuples(intervals)
        tree.merge_overlaps(strict=True)
        return tree

    @staticmethod
    def _intersection_periods(groups) -> intervaltree.IntervalTree:
        """求多个时间段组的交集"""

        intersection_tree: Optional[EnhancedIntervalTree] = None
        for group in groups:
            # 按照用户划分的时间组

            intervals = [[int(period.started_at.timestamp()), int(period.ended_at.timestamp())] for period in group[1]]
            if intersection_tree is None:
                intersection_tree = EnhancedIntervalTree.from_tuples(intervals)
                continue

            intersection_tree = intersection_tree.range_intersection(EnhancedIntervalTree.from_tuples(intervals))

        return intersection_tree

    @atomic
    def create_by_periods(self, award: "Award", username: str, periods: List):
        """创建可用时间段"""

        # 0. 尝试合并有交集时间段
        intervals = self._merge_periods(periods)

        # 1. 创建时间段
        period_objs = []
        for interval in intervals:

            period, created = self.get_or_create(
                award=award,
                started_at=datetime.datetime.fromtimestamp(interval.begin),
                ended_at=datetime.datetime.fromtimestamp(interval.end),
                username=username,
                # 使用 -1 标记该审批时间未关联具体的步骤顺序
                step_index=-1,
            )
            if created:
                logger.debug("创建可用时间段: %s", period)

            period_objs.append(period)

        return period_objs

    def get_intersection(self, award: "Award", step_index: int, last_minutes: int):
        """获取当前奖项可用时间的交集"""
        grouped_periods = self.group_by_user(award, step_index) or []

        results = []
        for p in self._intersection_periods(grouped_periods) or []:
            if p.length() / 60 >= last_minutes:
                results.append(
                    {
                        "started_at": datetime.datetime.fromtimestamp(p.begin),
                        "ended_at": datetime.datetime.fromtimestamp(p.end),
                    }
                )

        return results

    def group_by_user(self, award: "Award", step_index: int):
        """根据用户分组"""
        return itertools.groupby(
            self.filter(award=award, step_index=step_index).order_by("username"), key=lambda x: x.username
        )
