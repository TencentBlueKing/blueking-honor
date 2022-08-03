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
from blue_krill.web.std_error import APIError
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler
from sentry_sdk import capture_exception


def custom_exception_handler(exc, context):
    """自定义异常处理器"""

    data = {}
    if isinstance(exc, APIError):
        data['code'] = exc.code
        data['message'] = exc.message
        return Response(data, status=exc.status_code)

    if isinstance(exc, ValidationError):
        message = ""
        for key, value in exc.detail.items():
            message += key + ' ' + exc.detail[key][0]
        data['code'] = exc.status_code
        data['message'] = message
        return Response(data, status=exc.status_code)

    # only send unknown problems to sentry
    if not isinstance(exc, (PermissionDenied, APIException)):
        capture_exception(exc)

    return exception_handler(exc, context)
