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
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action

from bk_honor.account.permissions.permissions import sys_perm_required
from bk_honor.awards import serializers
from bk_honor.awards.constants import SummaryStatus
from bk_honor.awards.models import Application, Award, Policy, Summary, SummaryLike
from bk_honor.common.error_codes import error_codes
from bk_honor.common.views import NoPatchModelViewSet

logger = logging.getLogger(__name__)


class SummaryViewSet(NoPatchModelViewSet):
    """奖项沉淀API"""

    queryset = Summary.objects.filter(enabled=True)
    serializer_class = serializers.SummarySLZ

    @inject_serializer(out=serializers.DetailSummarySLZ, tags=["奖项沉淀 summary"], operation_summary="查看奖项沉淀详情")
    def retrieve(self, request, pk: str):
        """查询奖项沉淀详情"""
        return self.get_object()

    @inject_serializer(
        query_in=serializers.QuerySummarySLZ,
        out=serializers.PaginatedSummarySerializer,
        tags=["奖项沉淀 summary"],
        operation_summary="查询奖项回顾",
    )
    def list(self, request, validated_data: dict):
        """查询奖项回顾"""
        queryset = self.get_queryset().filter(enabled=True, status=SummaryStatus.SUCCEED.value, award__isnull=False)
        if "award_name" in validated_data:
            queryset = queryset.filter(award__name__contains=validated_data["award_name"])
        if "year" in validated_data:
            queryset = queryset.filter(award__year=validated_data["year"])
        if "liaison" in validated_data:
            queryset = queryset.filter(award__liaisons__contains=validated_data["liaison"])
        if "search_datetime" in validated_data:
            search_datetime = datetime.datetime.fromtimestamp(validated_data["search_datetime"])
            queryset = queryset.filter(award__started_at__lte=search_datetime, award__ended_at__gte=search_datetime)
        if "summary_id" in validated_data:
            queryset = queryset.filter(pk=validated_data["summary_id"])
        return ResponseParams(
            self.get_paginated_response(self.paginate_queryset(queryset)), {"context": {"request": request}}
        )

    @inject_serializer(
        out=serializers.PaginatedSummarySerializer,
        tags=["奖项沉淀 summary"],
        operation_summary="查询年度奖项回顾",
    )
    @action(detail=False, methods=["get"])
    def get_annual_summary_list(self, request):
        """查询年度奖项回顾"""
        queryset = self.get_queryset().filter(enabled=True, status=SummaryStatus.SUCCEED.value, award__isnull=True)
        return ResponseParams(
            self.get_paginated_response(self.paginate_queryset(queryset)), {"context": {"request": request}}
        )

    @inject_serializer(
        query_in=serializers.QueryAwardSummarySLZ,
        out=serializers.PaginatedSummarySerializer,
        tags=["奖项沉淀 summary"],
        operation_summary="根据奖项年度和名称获取对应奖项沉淀列表",
    )
    @action(detail=False, methods=["GET"])
    def get_summaries_from_award(self, request, validated_data: dict):
        """根据奖项年份和名称获取对应奖项沉淀列表"""
        policy = get_object_or_404(Policy, pk=validated_data["policy_id"])
        summary_queryset = self.get_queryset().filter(
            enabled=True,
            status=SummaryStatus.SUCCEED.value,
            policy=policy,
            year=validated_data["year"],
        )
        return ResponseParams(
            self.get_paginated_response(self.paginate_queryset(summary_queryset)), {"context": {"request": request}}
        )

    @atomic
    @inject_serializer(
        body_in=serializers.CreateSummarySLZ,
        out=serializers.SummarySLZ,
        tags=["奖项沉淀 summary"],
        operation_summary="创建奖项沉淀内容",
    )
    @sys_perm_required("manage_awards")
    def create(self, request, validated_data: dict):
        """创建奖项沉淀内容"""
        if not validated_data["details"]["upload"] or not validated_data["details"]["gm_approval_image"]:
            raise error_codes.MISSING_REQUIRED_FIELDS.f("上传附件及gm审批截图")

        if "award_id" in validated_data and "application_id" in validated_data:
            award = get_object_or_404(Award, pk=validated_data["award_id"])
            application = get_object_or_404(Application, pk=validated_data["application_id"])
            validated_data["year"] = award.year
            validated_data["policy"] = award.policy

            try:
                summary = Summary.objects.create_summary(award, application, validated_data)
            except Exception:
                logger.exception("创建奖项沉淀内容失败，创建信息: %s", validated_data)
                raise error_codes.AWARD_SUMMARY_CANNOT_BE_CREATED
            try:
                summary.update_steps()
            except Exception:
                logger.exception("更新奖项沉淀<%s>关联的申报步骤失败", summary)
                raise error_codes.APPLICATION_CANNOT_BE_UPDATED.f("更新奖项沉淀关联的申报步骤失败")
        else:
            try:
                # TODO: 年度奖项沉淀默认通过 直接展示
                validated_data["status"] = SummaryStatus.SUCCEED.value
                summary = Summary.objects.create_annual_summary(validated_data=validated_data)
            except Exception:
                logger.exception("创建年度奖项沉淀内容失败，创建信息: %s", validated_data)
                raise error_codes.AWARD_SUMMARY_CANNOT_BE_CREATED
        return summary

    @atomic
    @inject_serializer(
        body_in=serializers.SummaryEditSLZ,
        out=serializers.SummarySLZ,
        tags=["奖项沉淀 summary"],
        operation_summary="编辑奖项沉淀内容",
    )
    def update(self, request, pk: str, validated_data: dict):
        """编辑奖项沉淀内容"""
        if not validated_data["details"]["upload"] or not validated_data["details"]["gm_approval_image"]:
            raise error_codes.MISSING_REQUIRED_FIELDS.f("上传附件及gm审批截图")

        summary = self.get_queryset().filter(pk=pk)
        if not summary:
            raise error_codes.AWARD_SUMMARY_NOT_EXIST
        try:
            if "policy_id" in validated_data:
                validated_data["policy"] = get_object_or_404(Policy, pk=validated_data["policy_id"])
            else:
                validated_data["policy"] = summary.first().policy  # type: ignore
            summary.update(**validated_data)
        except Exception:
            logger.exception("编辑奖项沉淀内容失败")
            raise error_codes.AWARD_SUMMARY_CANNOT_BE_UPDATED

    @inject_serializer(out=serializers.SummarySLZ, tags=["奖项沉淀 summary"], operation_summary="删除奖项回顾")
    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except Exception:
            logger.exception("删除奖项回顾失败")
            raise error_codes.AWARD_SUMMARY_CANNOT_BE_DELETED

    @atomic
    @inject_serializer(
        out=serializers.SummarySLZ,
        tags=["奖项沉淀 summary"],
        operation_summary="给奖项沉淀内容点赞",
    )
    @action(detail=True, methods=["POST"])
    def like(self, request, pk: str):
        """增加奖项沉淀点赞数"""
        summary = get_object_or_404(Summary, pk=pk)
        username = request.user.username
        try:
            SummaryLike.objects.update_summary_like(summary, username)
        except Exception:
            logger.exception(f"奖项沉淀：{summary} 点赞失败")
            raise error_codes.AWARD_SUMMARY_UPDATE_LIKE_FAILED
        return summary

    @inject_serializer(
        query_in=serializers.QueryRecordsSLZ,
        out=serializers.PaginatedAwardRecordsSerializer,
        tags=["奖项沉淀 summary"],
        operation_summary="查询获奖记录",
    )
    @action(detail=False, methods=["GET"])
    def records(self, request, validated_data: dict):
        """查询获奖记录"""
        if "username" not in validated_data:
            user = request.user
            username = request.user.username
        else:
            user = None
            username = validated_data["username"]
        # TODO:  判断用户是获奖团队成员的条件不定，此处根据当前用户是否为奖项沉淀填写的团队成员
        queryset = self.get_queryset().filter(
            details__team_members__contains=username, enabled=True, status=SummaryStatus.SUCCEED.value
        )
        return ResponseParams(
            self.get_paginated_response(self.paginate_queryset(queryset)),
            {"context": {"user": user, "username": username}},
        )

    @inject_serializer(
        out=serializers.IndexSummaryAwardsSLZ,
        tags=["奖项沉淀 summary"],
        operation_summary="获取包含某年所有奖项沉淀对应的奖项列表",
    )
    @action(detail=False, methods=["GET"])
    def get_index_awards_summaries(self, request):
        """获取首页展示历年各期奖项沉淀对应的奖项策略信息"""
        summary_queryset = self.get_queryset().filter(enabled=True, status=SummaryStatus.SUCCEED.value).distinct()
        summary_policy_set = set()
        summary_list = []
        for summary in summary_queryset:
            if summary.policy not in summary_policy_set:
                summary_list.append(summary)
                summary_policy_set.add(summary.policy)
        summary_queryset = summary_list

        return {"summaries": self.paginate_queryset(summary_queryset)}
