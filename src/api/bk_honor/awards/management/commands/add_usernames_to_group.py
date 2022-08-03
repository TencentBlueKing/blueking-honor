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
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from bk_honor.account.models import UserGroup

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "adding usernames to group which is loaded by `python manage.py load_policies_from_yaml`"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--group", type=str, help="Role key")
        parser.add_argument("--usernames", type=str, help="usernames, as 'foo,bar,baz'")
        parser.add_argument("--append", action="store_true", help="whether override bindings")

    def handle(self, *args: Any, **options: Any):
        group_key = options.get("group")
        if not group_key:
            raise ValueError("role is required")

        group = UserGroup.objects.get(id=group_key)
        usernames = options.get("usernames", "").split(",")

        if options.get("append"):
            already_bind = set(group.bindings)
            group.bindings = list(already_bind | set(usernames))
        else:
            group.bindings = list(set(usernames))

        group.save()
