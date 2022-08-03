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
from collections import OrderedDict

from django.db.models import QuerySet
from rest_framework.pagination import CursorPagination, PageNumberPagination


class AdvancedCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 500
    ordering = '-created_at'

    def get_paginated_response(self, data: "QuerySet"):
        return OrderedDict(
            [
                ("next", self.get_next_link()),
                ("previous", self.get_previous_link()),
                ("results", data),
            ]
        )


class AdvancedPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 500
    ordering = '-created_at'

    def get_paginated_response(self, data):
        return OrderedDict(
            [
                ('count', self.page.paginator.count),
                ('next', self.get_next_link()),
                ('previous', self.get_previous_link()),
                ('results', data),
            ]
        )
