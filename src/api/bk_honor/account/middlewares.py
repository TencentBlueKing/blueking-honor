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

from django.conf import settings
from django.contrib import auth
from django.utils.deprecation import MiddlewareMixin

from bk_honor.account.forms import AuthenticationForm
from bk_honor.account.response import ResponseHandler

logger = logging.getLogger(__name__)


class LoginRequiredMiddleware(MiddlewareMixin):
    def process_view(self, request, view, args, kwargs):
        """
        login into bk_honor
        The user has logged in through authentication
        """
        if request.path in settings.LOGIN_EXEMPT_WHITE_LIST:
            logger.debug(
                "current_path:<%s> in white_url:<%s>, exempting login", request.path, settings.LOGIN_EXEMPT_WHITE_LIST
            )
            return None

        form = AuthenticationForm(request.COOKIES)
        if form.is_valid():
            bk_token = form.cleaned_data[settings.BK_TOKEN_COOKIE_NAME]
            user = auth.authenticate(request=request, bk_token=bk_token)
            if user:
                if user.get_username() != request.user.username:
                    logger.debug("user[%s] login, request path: %s", user.get_username(), request.path)
                    auth.login(request, user)
                return None

        handler = ResponseHandler()
        if request.is_ajax():
            return handler.build_401_response()
        return handler.build_302_response(request)
