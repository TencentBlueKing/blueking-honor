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
formatters = {
    "verbose": {
        "format": "%(levelname)s [%(asctime)s] %(lineno)d %(funcName)s %(process)d %(thread)d %(message)s \n",
        "datefmt": "%Y-%m-%d %H:%M:%S",
    },
    "simple": {"format": "%(levelname)s %(message)s"},
}


def get_loggers(package_name: str, log_level: str) -> dict:
    return {
        "django": {
            "handlers": ["null"],
            "level": "INFO",
            "propagate": True,
        },
        "django.request": {
            "handlers": ["root"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.db.backends": {
            "handlers": ["root"],
            "level": "INFO",
            "propagate": True,
        },
        "django.security": {
            "handlers": ["root"],
            "level": "INFO",
            "propagate": True,
        },
        package_name: {
            "handlers": ["root"],
            "level": log_level,
            "propagate": True,
        },
        "requests": {
            "handlers": ["root"],
            "level": log_level,
        },
    }


def get_stdout_logging(log_level: str, package_name: str, formatter: str = "verbose"):
    """获取标准输出日志配置"""
    log_class = "logging.StreamHandler"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": {
            "null": {"level": "DEBUG", "class": "logging.NullHandler"},
            "root": {
                "class": log_class,
                "formatter": formatter,
            },
            "component": {
                "class": log_class,
                "formatter": formatter,
            },
        },
        "loggers": get_loggers(package_name, log_level),
    }
