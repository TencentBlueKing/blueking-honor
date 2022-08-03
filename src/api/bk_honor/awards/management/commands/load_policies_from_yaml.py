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
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser

from bk_honor.awards.presets import load_data_from_path

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "load policies from yaml file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--dry_run", action="store_true", help="dry run")
        parser.add_argument(
            "--path", type=str, help="文件路径", default=settings.BASE_DIR / Path("awards/presets/*/*.yaml")
        )

    def handle(self, *args: Any, **options: Any):
        dry_run = options["dry_run"]
        path = options["path"]

        load_data_from_path(path, dry_run)
