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
from django.apps import AppConfig

from bk_honor.common.sentry import init_sentry_sdk


class AwardsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bk_honor.awards"

    def ready(self) -> None:
        from .parsers import approval  # noqa
        from .parsers import approval_time_collection  # noqa
        from .parsers import extra_info_collection  # noqa
        from .parsers import notification  # noqa
        from .parsers import summary_collection  # noqa

        init_sentry_sdk()
