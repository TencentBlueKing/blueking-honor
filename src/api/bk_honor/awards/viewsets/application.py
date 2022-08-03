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

from blue_krill.web.drf_utils import inject_serializer
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from bk_honor.account.constants import SystemRole
from bk_honor.account.permissions.permissions import res_perm_required
from bk_honor.awards import serializers
from bk_honor.awards.exceptions import AlreadyLastStageError, StepConditionNotMeetError
from bk_honor.awards.models import Application, Step
from bk_honor.common.error_codes import error_codes
from bk_honor.common.response import export_excel_response
from bk_honor.common.serializers import EmptySerializer
from bk_honor.common.views import UpdateModelMixin

logger = logging.getLogger(__name__)


class ApplicationViewSet(mixins.RetrieveModelMixin, UpdateModelMixin, mixins.ListModelMixin, GenericViewSet):

    queryset = Application.objects.filter(enabled=True)
    serializer_class = serializers.ApplicationSLZ

    @inject_serializer(out=serializers.DetailApplicationSLZ, tags=["申报 application"], operation_summary="查询奖项申报详情")
    @res_perm_required("read")
    def retrieve(self, request, pk: str):
        """查询奖项详情"""
        return self.get_object()

    @inject_serializer(
        query_in=serializers.QueryApplicationSLZ,
        out=serializers.PaginatedApplicationSerializer,
        tags=["申报 application"],
        operation_summary="申报列表",
    )
    def list(self, request, validated_data: dict):
        """查询申报列表"""
        username = request.user.username
        role = request.user.system_role
        # TODO: 可在权限控制中 增加查询能力的判断
        if role == SystemRole.ADMIN.value:  # type: ignore
            queryset = self.get_queryset()
        elif role == SystemRole.USER.value:  # type: ignore
            queryset = self.get_queryset().filter(applicants__contains=username)
        else:
            raise error_codes.APPLICATION_USER_PERMISSION_ERROR

        if "award_name" in validated_data:
            queryset = queryset.filter(award__name__contains=validated_data["award_name"])
        if "application_status" in validated_data:
            queryset = queryset.filter(status=validated_data["application_status"])
        if "search_datetime" in validated_data:
            search_datetime = datetime.datetime.fromtimestamp(validated_data["search_datetime"])
            queryset = queryset.filter(award__started_at__lte=search_datetime, award__ended_at__gte=search_datetime)
        if "level" in validated_data:
            queryset = queryset.filter(award__policy__level__key=validated_data["level"])
        if "award_status" in validated_data:
            queryset = queryset.filter(award__status=validated_data["award_status"])
        if "liaison" in validated_data:
            queryset = queryset.filter(liaisons__contains=validated_data["liaison"])
        return self.get_paginated_response(self.paginate_queryset(queryset))

    @inject_serializer(
        body_in=EmptySerializer,
        out=serializers.ApplicationSLZ,
        tags=["申报 application"],
        operation_summary="将申报流转到下一步骤",
    )
    @res_perm_required("next")
    @action(detail=True, methods=["POST"])
    def next(self, request, pk: str, validated_data: dict):
        """将申报流转到下一步骤"""
        application = get_object_or_404(Application, pk=pk)
        try:
            application.next()
        except StepConditionNotMeetError:
            raise error_codes.APPLICATION_CANNOT_ENTER_NEXT.format("当前步骤不满足流转条件")
        except AlreadyLastStageError:
            raise error_codes.APPLICATION_CANNOT_ENTER_NEXT.format("已经是最后一步")
        except Exception:
            raise error_codes.APPLICATION_CANNOT_ENTER_NEXT

        return application

    @inject_serializer(
        body_in=EmptySerializer, out=serializers.ApplicationSLZ, tags=["申报 application"], operation_summary="导出申报信息"
    )
    @res_perm_required("export")
    @action(detail=True, methods=["POST"])
    def export(self, request, pk: str, validated_data: dict):
        """导出奖项申报信息"""
        application = get_object_or_404(Application, pk=pk)
        try:
            return export_excel_response(application=application)
        except Exception as e:
            logger.debug(f'export application error ：{e}')
            raise error_codes.APPLICATION_EXPORT_FAILED

    @inject_serializer(
        body_in=serializers.ApplicationBulkExportSLZ,
        out=serializers.ApplicationSLZ,
        tags=["申报 application"],
        operation_summary="批量导出申报信息",
    )
    @action(detail=False, methods=["POST"])
    def bulk_export(self, request, validated_data: dict):
        """批量导出"""
        try:
            return export_excel_response(application_ids=validated_data["application_ids"])
        except Exception:
            raise error_codes.APPLICATION_EXPORT_FAILED

    @inject_serializer(
        body_in=EmptySerializer, out=serializers.ApplicationSLZ, tags=["申报 application"], operation_summary="中止申报"
    )
    @res_perm_required("abort")
    @action(detail=True, methods=["POST"])
    def abort(self, request, pk: int, validated_data: dict):
        """中止申报"""
        application = get_object_or_404(Application, pk=pk)
        try:
            application.abort()
        except Exception:
            raise error_codes.APPLICATION_CANNOT_ABORTED

        return application

    @inject_serializer(
        body_in=EmptySerializer, out=serializers.ApplicationSLZ, tags=["申报 application"], operation_summary="申报结束 通知获奖"
    )
    @res_perm_required("finish")
    @action(detail=True, methods=["POST"])
    def finish(self, request, pk: int, validated_data: dict):
        """申报结束 通知获奖"""
        application = get_object_or_404(Application, pk=pk)
        try:
            application.finish()
        except Exception:
            raise error_codes.APPLICATION_CANNOT_FINISHED
        return application

    @inject_serializer(
        body_in=serializers.CreateApplicationPromoteSLZ,
        out=serializers.ApplicationSLZ,
        tags=["申报 application"],
        operation_summary="申报结束后 填写奖项宣讲内容",
    )
    @res_perm_required("promote")
    @action(detail=True, methods=["POST"])
    def promote(self, request, pk: int, validated_data: dict):
        """申报结束后 填写奖项宣讲内容"""
        application = get_object_or_404(Application, pk=pk)
        try:
            application.promote(validated_data=validated_data)
        except Exception:
            raise error_codes.APPLICANT_PROMOTION_CANNOT_BE_CREATED
        return application

    @inject_serializer(
        out=serializers.StepSLZ(many=True),
        tags=["申报 application"],
        operation_summary="获取当前申报的当前步骤内容",
    )
    @res_perm_required("read")
    @action(detail=True, methods=["GET"])
    def steps(self, request, pk: str):
        """获取当前申报的当前步骤内容"""
        return Step.generator.filter(enabled=True, stage__application__id=pk)

    @inject_serializer(
        body_in=serializers.UpdateApplicationSLZ,
        out=serializers.ApplicationSLZ,
        tags=["申报 application"],
        operation_summary="更新申报",
    )
    @res_perm_required("update")
    def update(self, request, pk: str, validated_data: dict):
        """更新申报"""
        try:
            Application.objects.filter(pk=pk).update(**validated_data)
        except Exception:
            logger.exception("更新申报失败")
            raise error_codes.APPLICATION_CANNOT_BE_UPDATED

        return self.get_object()
