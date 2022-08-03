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
import logging
from typing import Tuple

import requests
from django.conf import settings
from django.contrib.auth.backends import ModelBackend

from bk_honor.account.constants import SystemRole
from bk_honor.account.models import BkUser, UserGroup

logger = logging.getLogger(__name__)


class TokenBackend(ModelBackend):
    def authenticate(self, request=None, bk_token=None, **kwargs):
        logger.debug("going to authenticate by bk_token")
        if not bk_token:
            return None
        verify_result = self.verify_bk_token(bk_token)
        if not verify_result:
            return None

        try:
            get_user_info_result, user_info = self.get_user_info(bk_token)
            if not get_user_info_result:
                return None
        except Exception:
            return None

        try:
            user, _ = BkUser.objects.get_or_create(username=user_info["username"])
            user.chinese_name = user_info.get("chinese_name")
        except Exception:
            logger.exception("get_or_create award user<%s> fail", user_info)
            return None

        # 保证某些用户登录后即成为管理员
        if user.get_username() in UserGroup.objects.get_usernames(SystemRole.ADMIN.value):
            user.system_role = SystemRole.ADMIN.value

        try:
            user.save()
            return user
        except Exception:
            logger.exception("Auto create & update award user<%s> fail", user.get_username())
            return None

    @staticmethod
    def get_user_info(bk_token) -> Tuple[bool, dict]:
        api_params = {settings.BK_TOKEN_COOKIE_NAME: bk_token}

        try:
            response = requests.get(
                settings.BK_LOGIN_API_URL + settings.BK_LOGIN_USER_INFO_URI, params=api_params, verify=False
            )
        except Exception:
            logger.exception("Abnormal error in get_full_user_info")
            return False, {}

        try:
            resp_body = response.json()
        except Exception:
            logger.exception("response can not be parsed to json, content: %s", response.content)
            return False, {}

        if resp_body.get("ret") == 0:
            return True, resp_body.get("data", {})
        else:
            logger.error("Failed to Get User Info: error=%s, ret=%s", resp_body.get("message", "未知异常"), response)
            return False, {}

    @staticmethod
    def verify_bk_token(bk_token) -> bool:
        api_params = {settings.BK_TOKEN_COOKIE_NAME: bk_token}

        try:
            response = requests.get(
                settings.BK_LOGIN_API_URL + settings.BK_LOGIN_VERIFY_URI, params=api_params, verify=False
            )
        except Exception as e:
            logger.exception("Abnormal error in verify_bk_token...:%s" % e)
            return False

        try:
            resp_body = response.json()
        except Exception:
            logger.exception("response can not be parsed to json, content: %s", response.content)
            return False

        if resp_body.get("ret") != 0:
            logger.error("Failed to Verify Token: error=%s, ret=%s", resp_body.get("message", "未知异常"), response)
            return False

        return True
