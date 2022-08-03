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

DEBUG = True
ALLOWED_HOSTS = ["*"]

LOG_LEVEL = env.str("LOG_LEVEL", default="DEBUG")
LOGGING = get_stdout_logging(LOG_LEVEL, "bk_honor")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env.str("DB_NAME"),
        "USER": env.str("DB_USER"),
        "PASSWORD": env.str("DB_PASSWORD"),
        "HOST": env.str("DB_HOST"),
        "PORT": env.int("DB_PORT"),
        "OPTIONS": {"charset": "utf8mb4"},
        "TEST": {"CHARSET": "utf8mb4", "COLLATION": "utf8mb4_general_ci"},
    },
}

PROJECT_SOURCE_DIR = Path(os.path.dirname(os.path.dirname(BASE_DIR)))
STATICFILES_DIRS = (PROJECT_SOURCE_DIR / "front/dist/static",)


LOGIN_EXEMPT_WHITE_LIST = ["/swagger/"]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "dist",
            PROJECT_SOURCE_DIR / "front/dist",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "bk_honor.common.context_processors.configs",
            ],
        },
    },
]
# --------------------------
# 开发图表相关，仅在本地开发配置
# --------------------------
GRAPH_MODELS = {
    'all_applications': False,
    'group_models': False,
}

INSTALLED_APPS += ["django_extensions"]
