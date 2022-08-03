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
from urllib.parse import urlparse, urlunparse

from django.conf import settings
from django.http import HttpResponseRedirect, QueryDict
from django.http.response import JsonResponse
from django.shortcuts import resolve_url


class ResponseHandler:

    C_URL = "c_url"

    def build_401_response(self):
        """返回无身份 401 错误"""
        context = {
            "login_url": settings.LOGIN_URL + "/plain/",
            "width": settings.BK_LOGIN_IFRAME_WIDTH,
            "height": settings.BK_LOGIN_IFRAME_HEIGHT,
        }
        return JsonResponse(context, status=401)

    def build_302_response(self, request):
        """跳转到登录页面"""
        _next = request.build_absolute_uri()
        _login_url = self.build_redirect_url(_next, settings.BK_LOGIN_URL, self.C_URL)
        return HttpResponseRedirect(_login_url)

    @staticmethod
    def build_redirect_url(next_url, current_url, redirect_field_name, extra_args=None):
        """
        即将访问 CRU_URL页面  加上下一步要跳转的页面
        """
        resolved_url = resolve_url(current_url)

        login_url_parts = list(urlparse(resolved_url))

        querystring = QueryDict(login_url_parts[4], mutable=True)
        querystring[redirect_field_name] = next_url

        if extra_args:
            querystring.update(extra_args)
        login_url_parts[4] = querystring.urlencode(safe="/")

        return urlunparse(login_url_parts)
