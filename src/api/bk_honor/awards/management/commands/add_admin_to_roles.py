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
from django.db.transaction import atomic

from bk_honor.account.models import BkUser
from bk_honor.awards.models import Policy

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "add admin to roles from yaml file"

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--add", type=str, help="add someone to roles, as 'hhh,ddd' ", required=False)
        parser.add_argument("--del", type=str, help="del roles, as 'hhh, ddd' ", required=False)

    def handle(self, *args: Any, **options: Any):
        add_key = options.get("add", "")
        del_key = options.get("del", "")

        with atomic():
            data_list = []
            for policy in Policy.objects.filter(enabled=True):
                if add_key:
                    for key in add_key.split(","):
                        policy.liaisons.append(key)
                if del_key:
                    for key in del_key.split(","):
                        if key not in policy.liaisons:
                            continue
                        policy.liaisons.remove(key)
                policy.save()
                data_list.extend(policy.liaisons)
            all_roles = list(set(data_list))  # type: ignore
            try:
                BkUser.objects.filter(username__in=all_roles).update(system_role="admin")
            except Exception as e:
                logger.error(e)
