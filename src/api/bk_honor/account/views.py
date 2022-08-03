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
from blue_krill.web.drf_utils import inject_serializer
from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet

from bk_honor.account.models import BkUser
from bk_honor.common.serializers import EmptySerializer


class UserInfoSLZ(serializers.Serializer):
    username = serializers.CharField()
    system_role = serializers.CharField()
    chinese_name = serializers.CharField()


class UserView(GenericViewSet):
    queryset = BkUser.objects.all()
    serializer_class = UserInfoSLZ

    pagination_class = None

    @inject_serializer(
        out=UserInfoSLZ, config={"remain_request": True}, tags=["用户 user"], operation_summary="获取登录用户信息"
    )
    @action(detail=False, methods=["GET"])
    def info(self, request):
        """获取登录用户信息"""
        context = {
            "username": request.user.get_username(),
            "system_role": request.user.system_role,
            "chinese_name": request.user.chinese_name,
        }
        return context

    @inject_serializer(body_in=EmptySerializer, out=EmptySerializer, tags=["用户 user"], operation_summary="退出登录")
    @action(detail=False, methods=["POST"])
    def logout(self, request, validated_data: dict):
        """登出"""
        logout(request)
        resp = HttpResponse(status=status.HTTP_200_OK)
        resp.delete_cookie(settings.BK_TOKEN_COOKIE_NAME, domain=settings.CSRF_COOKIE_DOMAIN)
        return resp
