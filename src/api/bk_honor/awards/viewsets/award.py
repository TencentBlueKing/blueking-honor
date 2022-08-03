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
import logging

from blue_krill.web.drf_utils import ResponseParams, inject_serializer
from django.conf import settings
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action

from bk_honor.account.permissions.permissions import res_perm_required, sys_perm_required
from bk_honor.awards import serializers
from bk_honor.awards.constants import ApplicationStatus, AwardStatus, StepType, SummaryStatus
from bk_honor.awards.models import Application, ApprovalPeriod, AvailablePeriod, Award, Summary
from bk_honor.common.error_codes import error_codes
from bk_honor.common.views import NoPatchModelViewSet

logger = logging.getLogger(__name__)


class AwardViewSet(NoPatchModelViewSet):

    serializer_class = serializers.AwardSLZ
    queryset = Award.objects.filter(enabled=True)

    @inject_serializer(
        query_in=serializers.SearchSerializer,
        out=serializers.SearchOutSLZ,
        tags=["奖项 award"],
        operation_summary="首页搜索 奖项、奖项沉淀",
    )
    @action(detail=False, methods=["GET"])
    def search(self, request, validated_data: dict):
        keyword = validated_data.get("keyword", "")
        queryset = self.get_queryset()
        award_queryset = queryset.filter(name__contains=keyword, enabled=True, status=AwardStatus.STARTED.value)
        summary_queryset = Summary.objects.filter(
            policy__name__contains=keyword, enabled=True, status=SummaryStatus.SUCCEED.value
        ).distinct()
        summary_policy_set = set()  # type: ignore
        summary_list = []
        for summary in summary_queryset:
            if summary.policy not in summary_policy_set:
                if summary.policy not in summary_policy_set:
                    summary_list.append(summary)
                    summary_policy_set.add(summary.policy)
        summary_queryset = summary_list  # type: ignore
        return {
            "search_data": {
                "awards": self.paginate_queryset(award_queryset),
                "summaries": self.paginate_queryset(summary_queryset),
            }
        }

    @inject_serializer(out=serializers.DetailAwardSLZ, tags=["奖项 award"], operation_summary="查询奖项详情")
    @res_perm_required("read")
    def retrieve(self, request, pk: str):
        """查询奖项详情"""
        return self.get_object()

    @inject_serializer(tags=["奖项 award"], operation_summary="删除奖项")
    @res_perm_required("update")
    def destroy(self, request, pk: str):
        return super().destroy(request, pk)

    @atomic
    @inject_serializer(
        body_in=serializers.CreateAwardSLZ, out=serializers.AwardSLZ, tags=["奖项 award"], operation_summary="创建奖项"
    )
    @sys_perm_required("manage_awards")
    def create(self, request, validated_data: dict):
        """创建奖项"""
        try:
            award = Award.objects.create_award(**validated_data)
        except ValueError as e:
            raise error_codes.AWARD_CANNOT_BE_CREATED.format(str(e))
        except Exception:
            logger.exception('创建奖项失败，创建参数: %s', validated_data)
            raise error_codes.AWARD_CANNOT_BE_CREATED
        return award

    @inject_serializer(
        query_in=serializers.QueryAwardSLZ,
        out=serializers.PaginatedAwardSerializer,
        tags=["奖项 award"],
        operation_summary="获取奖项列表",
    )
    def list(self, request, validated_data: dict):
        """获取奖项列表"""
        if "level" in validated_data:
            level = validated_data.pop("level", None)
            validated_data["policy__level__key"] = level
        query_set = self.get_queryset().filter(**validated_data)
        return self.get_paginated_response(self.paginate_queryset(query_set))

    @inject_serializer(
        out=serializers.IndexAwardsSLZ,
        tags=["奖项 award"],
        operation_summary="获取首页奖项列表",
    )
    @action(detail=False, methods=["GET"])
    def get_index_awards(self, request):
        """首页奖项列表"""
        award_queryset = self.get_queryset()
        return {"awards": self.paginate_queryset(award_queryset)}

    @inject_serializer(
        query_in=serializers.QueryAwardSLZ,
        out=serializers.PaginatedAwardSerializer,
        tags=["奖项 award"],
        operation_summary="获取待反馈评审时间的奖项列表",
    )
    @action(detail=False, methods=["GET"])
    def get_approval_awards(self, request, validated_data: dict):
        """获取待反馈评审时间的奖项列表"""
        if "level" in validated_data:
            level = validated_data.pop("level", None)
            validated_data["policy__level__key"] = level
        award_queryset = self.get_queryset()

        award_ids = Award.objects.get_approval_awards(award_queryset, request)  # type: ignore
        queryset = self.get_queryset().filter(pk__in=award_ids, enabled=True, **validated_data)

        return self.get_paginated_response(self.paginate_queryset(queryset))

    @inject_serializer(
        out=serializers.PaginatedApplicationDetailsSerializer,
        tags=["奖项 award"],
        operation_summary="评审详情",
    )
    @action(detail=True, methods=["GET"])
    def get_approval_award_details(self, request, pk: str):
        """获取指定奖项中待评审详情"""
        applications = Application.objects.filter(award_id=pk, enabled=True)
        award = get_object_or_404(Award, pk=pk)
        is_all_applications_type_approval = award.applications.check_application_steps_type(
            award, StepType.APPROVAL_TIME_COLLECTION.value
        )
        return ResponseParams(
            self.get_paginated_response(self.paginate_queryset(applications)),
            {"context": {"is_all_applications_type_approval": is_all_applications_type_approval}},
        )

    @atomic
    @inject_serializer(
        body_in=serializers.CreateApplicationSLZ,
        out=serializers.ApplicationSLZ,
        tags=["奖项 award"],
        operation_summary="发起申报",
    )
    @action(detail=True, methods=["POST"])
    def apply(self, request, pk: str, validated_data: dict):
        """发起申报"""
        award = get_object_or_404(Award, pk=pk)
        username = request.user.username
        validated_data["applicants"] = [username]

        # 判断是否可以申报
        if (
            settings.ALLOW_SAME_APPLICANT_PER_APPLICATION
            and Application.objects.filter(award=award, applicants=[username]).exists()
        ):
            logger.exception(f"申报人 <{','.join([username])}> 已经申报过该奖项")
            raise error_codes.APPLICANT_ALREADY_APPLIED
        if award.status != AwardStatus.STARTED.value:
            logger.exception(f"当前奖项 <{award.name}> 不可申报，请核实后重新发起")
            raise error_codes.AWARD_CANNOT_BE_APPLIED
        try:
            application = Application.objects.apply(award, validated_data)
        except Exception:
            logger.exception(f"发起申报 <{pk}> 失败")
            raise error_codes.APPLICATION_CANNOT_BE_CREATED

        return application

    @atomic()
    @inject_serializer(out=serializers.AwardSLZ, tags=["奖项 award"], operation_summary="复制奖项")
    @res_perm_required("copy")
    @action(detail=True, methods=["POST"])
    def copy(self, request, pk: str):
        """复制奖项"""
        try:
            return Award.objects.copy(pk)
        except Exception:
            logger.exception(f"复制奖项 <{pk}> 失败")
            raise error_codes.AWARD_CANNOT_BE_COPIED

    @atomic()
    @inject_serializer(
        body_in=serializers.AwardBulkCopySLZ,
        out=serializers.AwardSLZ(many=True),
        tags=["奖项 award"],
        operation_summary="批量复制奖项",
    )
    @action(detail=False, methods=["POST"])
    def bulk_copy(self, request, validated_data: dict):
        """批量复制奖项"""
        try:
            return Award.objects.bulk_copy(validated_data["award_ids"])
        except Exception:
            logger.exception(f"复制奖项 <{validated_data['award_ids']}> 失败")
            raise error_codes.AWARD_CANNOT_BE_COPIED

    @atomic
    @inject_serializer(
        body_in=serializers.AwardEditSLZ, out=serializers.AwardSLZ, tags=["奖项 award"], operation_summary="编辑奖项"
    )
    @res_perm_required("update")
    def update(self, request, pk: str, validated_data: dict):
        """编辑奖项"""
        try:
            Award.objects.filter(pk=pk).update(**validated_data)
        except Exception:
            logger.exception("编辑奖项失败")
            raise error_codes.AWARD_CANNOT_BE_UPDATED

        return self.get_object()

    @atomic
    @inject_serializer(out=serializers.AwardSLZ, tags=["奖项 award"], operation_summary="删除奖项")
    @res_perm_required("delete")
    def delete(self, request, pk: str):
        """删除奖项"""
        try:
            award = get_object_or_404(Award, pk=pk)
            award.delete()
        except Exception:
            logger.exception("删除奖项失败")
            raise error_codes.AWARD_CANNOT_BE_DELETED
        return award


class ApprovalPeriodViewSet(viewsets.ModelViewSet):
    queryset = Award.objects.filter(enabled=True)

    @inject_serializer(
        body_in=serializers.AvailablePeriodListSLZ,
        out=serializers.AvailablePeriodSLZ(many=True),
        tags=["奖项 award"],
        operation_summary="反馈可用时间",
    )
    @action(detail=True, methods=["POST"])
    def feed_available_periods(self, request, pk: str, validated_data: dict):
        """反馈可用时间"""
        award = self.get_object()
        login_username = request.user.username

        try:
            return AvailablePeriod.objects.create_by_periods(
                award=award,
                periods=validated_data["available_periods"],
                username=validated_data.get("username") or login_username,
            )
        except Exception:
            logger.exception("反馈奖项审批时间失败")
            raise error_codes.AVAILABLE_PERIOD_CANNOT_BE_CREATED

    @inject_serializer(
        query_in=serializers.QueryAvailablePeriodsSLZ,
        out=serializers.MixedPeriodsSLZ,
        tags=["奖项 award"],
        operation_summary="反馈可用时间",
    )
    @action(detail=True, methods=["GET"])
    def available_periods(self, request, pk: str, validated_data: dict):
        """获取可用时间"""
        award = self.get_object()
        grouped_periods = AvailablePeriod.objects.group_by_user(award, validated_data["step_index"])
        return {
            "username_periods": grouped_periods,
            "intersection_periods": AvailablePeriod.objects.get_intersection(award, **validated_data),
        }

    @inject_serializer(
        body_in=serializers.CreateApprovalPeriod,
        out=serializers.ApprovalPeriodSLZ,
        tags=["奖项 award"],
        operation_summary="反馈可用时间",
    )
    @action(detail=True, methods=["POST"])
    @sys_perm_required("manage_awards")
    def confirm_approval_period(self, request, pk: str, validated_data: dict):
        """确认审批时间"""
        award = self.get_object()

        # 检查奖项状态为：不可申报
        if award.status != AwardStatus.UNAPPLICABLE.value:
            raise error_codes.AWARD_STATUS_MANAGEMENT.f('确认审批时间之前需要将奖项状态设置为不可申报')

        # 0. 检查当前奖项的所有申报是否符合条件
        if award.applications.filter(status=ApplicationStatus.SUCCEED.value).exists():
            raise error_codes.APPROVAL_PERIOD_CANNOT_BE_CREATED.f("存在申报已获奖，请管理员确认奖项与各申报状态")

        applications = award.applications.filter(status=ApplicationStatus.STARTED.value)
        for application in applications:
            if not application.current_step:
                raise error_codes.APPROVAL_PERIOD_CANNOT_BE_CREATED.f(f"存在申报<{application}>未开始，请管理员确认奖项与各申报状态")

            if application.current_step.type != StepType.APPROVAL_TIME_COLLECTION.value:
                raise error_codes.APPROVAL_PERIOD_CANNOT_BE_CREATED.f(
                    f"存在申报<{application}>未达到审批时间收集步骤，" f"当前处于<{application.current_step}>步骤，请管理员确认相关申报状态"
                )

        # 1. 创建审批时间
        try:
            approval_period = ApprovalPeriod.objects.create(
                award=award,
                started_at=datetime.datetime.fromtimestamp(int(validated_data["started_at"])),
                ended_at=datetime.datetime.fromtimestamp(int(validated_data["ended_at"])),
                step_index=validated_data["step_index"],
            )
        except Exception:
            logger.exception("确认奖项审批时间失败")
            raise error_codes.APPROVAL_PERIOD_CANNOT_BE_CREATED

        # 2. 更新所有申报的状态
        try:
            approval_period.update_steps()
        except Exception:
            logger.exception("更新申报状态失败")
            raise error_codes.APPROVAL_PERIOD_CANNOT_BE_CREATED.f("确认审批时间成功，但同步更新所有相关申报状态失败，请管理员检查")

        return approval_period
