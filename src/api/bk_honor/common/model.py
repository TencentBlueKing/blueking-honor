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
import uuid

from django.db import models


class UuidModel(models.Model):
    """Mixin with uuid as id"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        self.enabled = False
        self.save(update_fields=["enabled", "updated_at"])


class TimestampedModelMixin(models.Model):
    """Mixin with 'created_at' and 'updated_at' fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
