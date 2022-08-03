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
import base64
import logging
from dataclasses import dataclass
from typing import ClassVar, List, Optional, Protocol

import requests
from blue_krill.encoding import force_text
from django.conf import settings

logger = logging.getLogger(__name__)


class NotifyPluginNotFoundError(Exception):
    """未知通知插件"""


class NotifyPlugin(Protocol):
    """通知插件协议"""

    name: ClassVar[str]

    def notify(self, message: str, receivers: List[str], sender: Optional[str]) -> None:
        """通知"""


@dataclass
class ESBApiRequester:
    """ESB API请求器"""

    base_url: str
    bk_app_code: str
    bk_app_secret: str
    operator: str = settings.DEFAULT_MESSAGE_SENDER

    @classmethod
    def from_settings(cls):
        """从配置文件中获取 ESB API请求器"""
        return cls(settings.BK_ESB_BASE_URL, settings.BK_APP_CODE, settings.BK_APP_SECRET)

    @property
    def common_params(self) -> dict:
        """公共参数"""
        return {
            "bk_app_code": self.bk_app_code,
            "bk_app_secret": self.bk_app_secret,
        }

    def post(self, api_path: str, data: dict, operator: Optional[str] = None) -> dict:
        """请求"""
        url = f"{self.base_url}/{api_path}"
        operator = operator or self.operator
        params = dict(self.common_params)
        params.update({"operator": operator})

        headers = {
            "Content-Type": "application/json",
            # TODO: 增加 request id ?
        }

        return self.handle_esb_resp(requests.post(url, params=params, data=data, verify=False, headers=headers))

    @staticmethod
    def handle_esb_resp(resp) -> dict:
        """处理ESB响应"""
        try:
            result = resp.json()
        except Exception:
            raise ValueError(f"ESB 响应异常：{resp.text}")

        if not result.get("result"):
            raise ValueError(f"ESB 请求失败, code: {result.get('code', 0)}, message: {result.get('message', '未知错误')}")

        return result.get("data", {})


@dataclass
class WecomPlugin(ESBApiRequester):
    """企业微信通知插件"""

    name = 'wecom'

    def notify(
        self, message: str, receivers: List[str], sender: Optional[str] = settings.DEFAULT_MESSAGE_SENDER, **kwargs
    ) -> None:
        """通知"""
        if settings.FORCE_SILENCE:
            logger.info("【主动静默未发送】message: %s, receivers: %s, sender: %s", message, receivers, sender)
            return

        if not receivers:
            raise ValueError("接收人为空，将跳过此次发送")

        self.post(
            "tof/send_rtx/",
            {
                "title": settings.DEFAULT_MESSAGE_TITLE,
                "receiver": receivers,
                "message": message,
                "sender": sender,
                "is_ignore_former_staff": True,
            },
            operator=sender,
        )


@dataclass
class EMailPlugin(ESBApiRequester):
    """邮件通知插件"""

    name = 'email'

    def notify(self, message: str, receivers: List[str], sender: Optional[str] = None, **kwargs) -> None:
        """通知"""
        if settings.FORCE_SILENCE:
            logger.info("【主动静默未发送】message: %s, receivers: %s, sender: %s", message, receivers, sender)
            return

        if not receivers:
            raise ValueError("接收人为空，将跳过此次发送")

        self.post(
            "tof/send_mail/",
            {
                "title": settings.DEFAULT_MESSAGE_TITLE,
                "receiver": ",".join(receivers),
                "content": force_text(base64.b64encode(message.encode("utf-8"))),
                "is_content_base64": True,
            },
            operator=sender,
        )


@dataclass
class Notifier:
    """通知器"""

    plugins: List[NotifyPlugin]

    def __post_init__(self):
        self.plugins_map = {plugin.name: plugin for plugin in self.plugins}

    def notify(self, message: str, methods: List[str], **kwargs):
        """通知"""

        for method in methods:
            try:
                plugin = self.get_plugin_by_name(method)
            except NotifyPluginNotFoundError:
                logger.warning(f"未知通知插件: {method}")
                continue

            plugin.notify(message, **kwargs)

    def get_plugin_by_name(self, name: str) -> NotifyPlugin:
        try:
            return self.plugins_map[name]
        except KeyError:
            raise NotifyPluginNotFoundError(name)


notifier = Notifier(plugins=[WecomPlugin.from_settings(), EMailPlugin.from_settings()])


def get_notifier() -> Notifier:
    return notifier
