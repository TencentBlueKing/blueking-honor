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
from bk_honor.settings.django import *  # noqa
from bk_honor.settings.logging import get_stdout_logging
from bk_honor.settings.platform import *  # noqa

DEBUG = False
ALLOWED_HOSTS = ['*']

LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")
LOGGING = get_stdout_logging(LOG_LEVEL, "bk_honor")

DB_PREFIX = env.str("DB_PREFIX", default="DB")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str(f"{DB_PREFIX}_NAME"),
        "USER": env.str(f"{DB_PREFIX}_USER"),
        "PASSWORD": env.str(f"{DB_PREFIX}_PASSWORD"),
        "HOST": env.str(f"{DB_PREFIX}_HOST"),
        "PORT": env.int(f"{DB_PREFIX}_PORT"),
        "OPTIONS": {"charset": "utf8mb4"},
        "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_general_ci"},
    },
}
