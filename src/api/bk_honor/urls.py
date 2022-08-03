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
from django.contrib import admin
from django.urls import include, path, re_path

from bk_honor.account import urls as account_urls
from bk_honor.apis import urls as apis_urls
from bk_honor.awards import urls as awards_urls
from bk_honor.common.views import WebPageViewSet

urlpatterns = [
    path("", include(awards_urls)),
    path("", include(account_urls)),
    path("", include(apis_urls)),
    path("adminUydhfe75W2/", admin.site.urls),
    # 其余路由转发到 web 页面
    re_path(r"^", WebPageViewSet.as_view({"get": "index"}), name="index"),
]
