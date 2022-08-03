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
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.template.response import TemplateResponse
from rest_framework import mixins, viewsets
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bk_honor.common.error_codes import error_codes


class WebPageViewSet(viewsets.ViewSet):

    serializer_class = None

    permission_classes: list = []

    @inject_serializer(auto_schema=None, config={"remain_request": True})
    def index(self, request):
        """首页"""
        try:
            return TemplateResponse(request=request, template=get_template("index.html"))
        except TemplateDoesNotExist:
            raise error_codes.CANNOT_FIND_TEMPLATE


class UpdateModelMixin:
    """
    Update a model instance.
    """

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class NoPatchModelViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`, `destroy()` and `list()` actions.
    """

    pass
