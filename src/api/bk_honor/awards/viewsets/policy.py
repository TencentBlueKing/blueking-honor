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

from blue_krill.web.drf_utils import inject_serializer
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from bk_honor.account.permissions.permissions import res_perm_required, sys_perm_required
from bk_honor.awards import serializers
from bk_honor.awards.models import Policy

logger = logging.getLogger(__name__)


class PolicyViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Policy.objects.filter(enabled=True)
    serializer_class = serializers.PolicySLZ

    @inject_serializer(out=serializers.PolicySLZ, tags=["策略 policy"], operation_summary="查询策略详情")
    @res_perm_required("read")
    def retrieve(self, request, pk: str):
        """查询策略详情"""
        return get_object_or_404(Policy, pk=pk)

    @inject_serializer(
        query_in=serializers.QueryPolicySLZ,
        out=serializers.PaginatedPolicySerializer,
        tags=["策略 policy"],
        operation_summary="获取策略列表",
    )
    @sys_perm_required("manage_policies")
    def list(self, request, validated_data: dict):
        """获取策略列表"""
        query_params = {}
        if "level" in validated_data:
            query_params["level__key"] = validated_data["level"]

        return self.get_paginated_response(self.paginate_queryset(self.get_queryset().filter(**query_params)))
