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
import os
from pathlib import Path

import pymysql

pymysql.install_as_MySQLdb()

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-nyz4za^%si#d^+*otgh41iha=(^&_8i(5x(h(2-dh$^2^l_w-e"

# SECURITY WARNING: don't run with debug turned on in production!

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "corsheaders",
    "bk_honor.awards.apps.AwardsConfig",
    "bk_honor.account.apps.AccountConfig",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "bk_honor.account.middlewares.LoginRequiredMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bk_honor.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "dist"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "bk_honor.common.context_processors.configs",
            ],
        },
    },
]

WSGI_APPLICATION = "bk_honor.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
# defined in overlays

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "zh-hans"

TIME_ZONE = "Asia/Shanghai"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR.joinpath("staticfiles"))

STATICFILES_DIRS = (os.path.join(BASE_DIR, "dist/static/"),)

# Templates
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Site url
SITE_URL = "/"

# ===============================================================================
# Authentication
# ===============================================================================
AUTHENTICATION_BACKENDS = ("bk_honor.account.backends.TokenBackend",)

SYSTEM_ADMIN_SHOULD_OWN_ALL_RES = True

# ===============================================================================
# REST framework
# ===============================================================================
REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "bk_honor.common.exception_handler.custom_exception_handler",
    'DEFAULT_PAGINATION_CLASS': 'bk_honor.common.pagination.AdvancedPageNumberPagination',
    'PAGE_SIZE': 100,
    'DATETIME_FORMAT': '%s',
    'DATE_FORMAT': '%s',
}

DRF_CROWN_DEFAULT_CONFIG = {"remain_request": True}
