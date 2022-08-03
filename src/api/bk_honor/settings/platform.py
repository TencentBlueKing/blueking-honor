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
# 蓝鲸平台相关配置
from . import env

BK_APP_CODE = env("BKPAAS_APP_ID", default="bk-honor")
BK_APP_SECRET = env("BKPAAS_APP_SECRET")

CSRF_COOKIE_NAME = BK_APP_CODE + "_csrftoken"

# ===============================================================================
# 蓝鲸 ESB
# ===============================================================================
BK_ESB_BASE_URL = env("BK_ESB_BASE_URL")

DEFAULT_MESSAGE_TITLE = env.str("DEFAULT_MESSAGE_TITLE", default="荣誉激励系统")
DEFAULT_MESSAGE_SENDER = env.str("DEFAULT_MESSAGE_SENDER", default="bk-honor")
FORCE_SILENCE = env.bool("FORCE_SILENCE", default=False)
ALLOW_SAME_APPLICANT_PER_APPLICATION = env.bool("ALLOW_SAME_APPLICANT_PER_APPLICATION", default=False)
ANY_PASS = env.bool("ANY_PASS", default=False)
# ===============================================================================
# 蓝鲸登录相关配置
# ===============================================================================
BK_TOKEN_COOKIE_NAME = env('BK_TOKEN_COOKIE_NAME', default='bk_token')
BK_LOGIN_URL = env('BK_LOGIN_URL', default="")

BK_LOGIN_API_URL = env('BK_LOGIN_API_URL', default="")
BK_LOGIN_VERIFY_URI = env("BK_LOGIN_VERIFY_URI", default="/accounts/is_login/")
BK_LOGIN_USER_INFO_URI = env("BK_LOGIN_USER_INFO_URI", default="/accounts/get_user/")


BK_LOGIN_IFRAME_HEIGHT = env('BK_LOGIN_IFRAME_HEIGHT', default=400)
BK_LOGIN_IFRAME_WIDTH = env('BK_LOGIN_IFRAME_WIDTH', default=400)
ADD_CROSS_PREFIX = True


# paths for exempting of login
LOGIN_EXEMPT_WHITE_LIST = ["/swagger/"]

BASE_URL = env.str("BASE_URL", default="https:example.com")

# ===============================================================================
# 跨域设置
# ===============================================================================

CORS_ORIGIN_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])

CORS_ALLOW_CREDENTIALS = True
CSRF_COOKIE_DOMAIN = env.str("CSRF_COOKIE_DOMAIN", default=".example.com")

# ===============================================================================
# BkRepo 存储设置
# ===============================================================================
BKREPO_ENDPOINT_URL = env.str('BKREPO_ENDPOINT_URL')
BKREPO_USERNAME = env.str('BKREPO_USERNAME')
BKREPO_PASSWORD = env.str('BKREPO_PASSWORD')
BKREPO_PROJECT = env.str('BKREPO_PROJECT')
BKREPO_BUCKET = env.str('BKREPO_BUCKET')

SUPPORTED_FILE_TYPES = env.list(
    'SUPPORTED_FILE_TYPES',
    default=["zip", "xlsx", "xls", "doc", "docx", "ppt", "pptx", "pdf", "jpg", "jpeg", "png", "gif"],
)
SUPPORTED_IMAGE_TYPES = env.list("SUPPORTED_IMAGE_TYPES", default=["jpg", "jpeg", "png", "gif"])

FILE_MAX_MB = env.int('FILE_MAX_MB', default=50)
IMAGE_MAX_MB = env.int("IMAGE_MAX_MB", default=50)

# ==============================================================================
# Sentry
# ==============================================================================
SENTRY_DSN = env("SENTRY_DSN", default="")

# ==============================================================================
# 审批相关
# ==============================================================================
DEFAULT_APPROVED_COMMENT = env.str("DEFAULT_APPROVED_COMMENT", default="同意通过")

# ==============================================================================
# 步骤设置
# ==============================================================================
DEFAULT_STEP_AUTO_EXECUTE = env.bool("DEFAULT_STEP_AUTO_EXECUTE", default=False)
