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
from django.core.exceptions import ObjectDoesNotExist
from django.db.transaction import atomic
from django.shortcuts import get_object_or_404
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from bk_honor.account.constants import SystemRole
from bk_honor.account.permissions.permissions import res_perm_required
from bk_honor.awards import serializers
from bk_honor.awards.constants import DefaultComment, StageStatus, StepType
from bk_honor.awards.exceptions import AlreadyNotifiedError, NotSupportStepOperation
from bk_honor.awards.models import Application, Step, Summary
from bk_honor.awards.parsers import operate_step
from bk_honor.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class ApprovalViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Step.generator.filter(enabled=True)
    serializer_class = serializers.StepSLZ

    @inject_serializer(
        query_in=serializers.QueryApplicationApprovesSLZ,
        out=serializers.PaginatedApplicationSerializer,
        tags=["审批 approval"],
        operation_summary="查询 我的评审列表",
    )
    def list(self, request, validated_data: dict):
        """查询 我的评审列表"""
        username = request.user.username
        role = request.user.system_role
        # TODO: 管理员 放开所有权限
        if role == SystemRole.ADMIN.value:  # type: ignore
            step = Step.generator.filter(enabled=True).values("id")
        elif role == SystemRole.USER.value:  # type: ignore
            step = Step.generator.filter(type="approval", enabled=True, details__approvers__contains=username).values(
                "id"
            )
        else:
            raise error_codes.APPLICATION_USER_PERMISSION_ERROR

        queryset = Application.objects.filter(enabled=True)
        if "award_name" in validated_data:
            queryset = queryset.filter(award__name__contains=validated_data["award_name"])
        if "search_datetime" in validated_data:
            search_datetime = datetime.datetime.fromtimestamp(validated_data["search_datetime"])
            queryset = queryset.filter(award__started_at__lte=search_datetime, award__ended_at__gte=search_datetime)

        queryset = queryset.filter(current_step__in=step)
        return self.get_paginated_response(self.paginate_queryset(queryset))

    @atomic
    @inject_serializer(
        body_in=serializers.ApproveStepSLZ,
        out=serializers.StepSLZ,
        tags=["审批 approval"],
        operation_summary="审批通过",
    )
    @res_perm_required("approve", Step)
    @action(methods=["POST"], detail=True)
    def approve(self, request, pk: str, validated_data: dict):
        """审批通过"""
        step = get_object_or_404(Step, pk=pk)
        application = step.stage.application
        if not application.current_step == step:
            raise error_codes.APPLICATION_STEP_NOT_MATCHED
        Step.generator.check_step_status(step)
        try:
            operate_step(step, "approve", approver=request.user.username, **validated_data)
        except NotSupportStepOperation:
            logger.exception("通过审批[%s]失败", step)
            raise error_codes.OPERATION_NOT_SUPPORTED
        except Exception:
            logger.exception("通过审批[%s]失败", step)
            raise error_codes.FAILED_TO_OPERATE_STEP
        try:
            application.update_status()
        except Exception:
            logger.exception("同步更新申报[%s]状态失败", application)
            raise error_codes.APPLICATION_CANNOT_BE_UPDATED
        try:
            summary = Summary.objects.get(application=application)
            summary.update_status()
        except ObjectDoesNotExist:
            pass
        except Exception:
            raise error_codes.AWARD_SUMMARY_UPDATE_STATUS_FAILED

        return self.get_object()

    @atomic
    @inject_serializer(
        body_in=serializers.BulkApproveStepSLZ,
        out=serializers.PaginatedApplicationSerializer,
        tags=["审批 approval"],
        operation_summary="批量通过",
    )
    @action(methods=["POST"], detail=False)
    def bulk_approve(self, request, validated_data: dict):
        """批量审批通过"""
        applications = Application.objects.filter(pk__in=validated_data["application_ids"]).all()
        for application in applications:
            if not application.current_step:
                raise error_codes.FAILED_TO_OPERATE_STEP

            step = application.current_step

            Step.generator.check_step_status(step)
            try:
                operate_step(step, "approve", approver=request.user.username)
            except Exception:
                logger.exception(f"操作批量通过奖项申报 <{validated_data['application_ids']}> 失败")
                raise error_codes.APPLICATION_BATCH_PASS_FAILED
            try:
                application.update_status()
            except Exception:
                logger.exception("同步更新申报[%s]状态失败", application)
                raise error_codes.APPLICATION_CANNOT_BE_UPDATED

            try:
                summary = Summary.objects.get(application=application)
                summary.update_status()
            except ObjectDoesNotExist:
                pass
            except Exception:
                raise error_codes.AWARD_SUMMARY_UPDATE_STATUS_FAILED

        return self.get_paginated_response(self.paginate_queryset(applications))

    @atomic
    @inject_serializer(
        body_in=serializers.RejectStepSLZ,
        out=serializers.StepSLZ,
        tags=["审批 approval"],
        operation_summary="审批驳回",
    )
    @res_perm_required("reject", Step)
    @action(methods=["POST"], detail=True)
    def reject(self, request, pk: str, validated_data: dict):
        """审批驳回"""
        step = get_object_or_404(Step, pk=pk)
        application = step.stage.application

        if not application.current_step == step:
            raise error_codes.APPLICATION_STEP_NOT_MATCHED

        Step.generator.check_step_status(step)

        try:
            operate_step(step, "reject", rejecter=request.user.username, **validated_data)
        except NotSupportStepOperation:
            logger.exception("驳回审批[%s]失败", step)
            raise error_codes.OPERATION_NOT_SUPPORTED
        except Exception:
            logger.exception("驳回审批[%s]失败", step)
            raise error_codes.FAILED_TO_OPERATE_STEP

        try:
            application.update_status()
        except Exception:
            logger.exception("同步更新申报[%s]状态失败", application)
            raise error_codes.APPLICATION_CANNOT_BE_UPDATED

        return self.get_object()

    @atomic
    @inject_serializer(
        body_in=serializers.BulkRejectStepSLZ,
        out=serializers.PaginatedApplicationSerializer,
        tags=["审批 approval"],
        operation_summary="批量驳回",
    )
    @action(methods=["POST"], detail=False)
    def bulk_reject(self, request, validated_data: dict):
        """批量审批驳回"""
        applications = Application.objects.filter(pk__in=validated_data["application_ids"]).all()
        for application in applications:
            if not application.current_step:
                raise error_codes.FAILED_TO_OPERATE_STEP

            step = application.current_step
            Step.generator.check_step_status(step)

            try:
                validated_data.pop("application_ids")
                validated_data["comment"] = DefaultComment.REJECT_COMMENT.value
                operate_step(step, "reject", rejecter=request.user.username, **validated_data)
            except Exception:
                logger.exception("批量驳回奖项申报失败")
                raise error_codes.APPLICATION_BATCH_REJECT_FAILED

            try:
                application.update_status()
            except Exception:
                logger.exception("同步更新申报[%s]状态失败", application)
                raise error_codes.APPLICATION_CANNOT_BE_UPDATED
        return self.get_paginated_response(self.paginate_queryset(applications))


class NotificationViewSet(GenericViewSet):
    """通知"""

    queryset = Step.generator.filter(enabled=True)
    serializer_class = serializers.StepSLZ

    @atomic
    @inject_serializer(
        body_in=serializers.NotifyStepSLZ,
        out=serializers.StepSLZ,
        tags=["通知 notification"],
        operation_summary="发送通知",
    )
    @res_perm_required("update", Step)
    @action(methods=["POST"], detail=True)
    def notify(self, request, pk: str, validated_data: dict):
        """发送通知"""
        step = get_object_or_404(Step, pk=pk)
        application = step.stage.application

        if step.type != StepType.NOTIFICATION.value:
            raise error_codes.OPERATION_NOT_SUPPORTED.format(f"当前步骤类型 {step.type} 不支持审批")

        if not application.current_step == step:
            raise error_codes.APPLICATION_STEP_NOT_MATCHED

        if step.status != StageStatus.STARTED.value:
            raise error_codes.APPLICATION_STEP_NOT_STARTED

        try:
            operate_step(step, "notify", **validated_data)
        except NotSupportStepOperation:
            logger.exception("发送通知失败")
            raise error_codes.OPERATION_NOT_SUPPORTED
        except AlreadyNotifiedError as e:
            raise error_codes.FAILED_TO_OPERATE_STEP.format(str(e))
        except Exception:
            logger.exception("发送通知失败")
            raise error_codes.FAILED_TO_OPERATE_STEP

        try:
            application.update_status()
        except Exception:
            logger.exception("同步更新申报[%s]状态失败", application)
            raise error_codes.APPLICATION_CANNOT_BE_UPDATED

        return self.get_object()


class CollectionViewSet(GenericViewSet):
    """收集"""

    queryset = Step.generator.filter(enabled=True)
    serializer_class = serializers.StepSLZ

    @atomic
    @inject_serializer(
        body_in=serializers.CollectionStepSLZ,
        out=serializers.StepSLZ,
        tags=["收集 collection"],
        operation_summary="收集信息",
    )
    @res_perm_required("update", Step)
    @action(methods=["POST"], detail=True)
    def extra_info_collect(self, request, pk: str, validated_data: dict):
        """收集信息"""
        step = get_object_or_404(Step, pk=pk)
        application = step.stage.application

        if not step.type == StepType.EXTRA_INFO_COLLECTION.value:
            raise error_codes.OPERATION_NOT_SUPPORTED.format(f"当前步骤类型 {step.type} 不支持额外信息收集")

        if not application.current_step == step:
            raise error_codes.APPLICATION_STEP_NOT_MATCHED

        if step.status != StageStatus.STARTED.value:
            raise error_codes.APPLICATION_STEP_NOT_STARTED

        try:
            operate_step(step, "collect", data=validated_data["collection_data"])
        except NotSupportStepOperation:
            logger.exception("信息收集失败")
            raise error_codes.OPERATION_NOT_SUPPORTED
        except AlreadyNotifiedError as e:
            raise error_codes.FAILED_TO_OPERATE_STEP.f(str(e))
        except Exception:
            logger.exception("信息收集失败")
            raise error_codes.FAILED_TO_OPERATE_STEP

        try:
            application.update_status()
        except Exception:
            logger.exception("同步更新申报[%s]状态失败", application)
            raise error_codes.APPLICATION_CANNOT_BE_UPDATED

        return self.get_object()
