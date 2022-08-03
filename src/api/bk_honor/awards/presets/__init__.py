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
import glob
import logging
from collections import defaultdict
from typing import Dict, List

import yaml

from bk_honor.account.models import UserGroup
from bk_honor.awards.models import Level, Policy

logger = logging.getLogger(__name__)


def create_policies(data: list) -> List[Policy]:
    """创建奖项策略"""
    created = failed = updated = 0
    policies = []
    for policy_data in data:
        spec = policy_data["spec"]
        try:
            name = spec.pop("name")
            level_key = spec.pop("level")

            policy, is_created = Policy.objects.update_or_create(
                name=name, level=Level.objects.get(key=level_key), defaults=spec
            )
            if is_created:
                created += 1
            else:
                updated += 1

            policies.append(policy)

        except Exception:
            logger.warning("Failed to create policy: %s", spec["name"])
            failed += 1

    logger.info("Policies: %d created; %d updated; %d failed.", created, updated, failed)
    return policies


def create_levels(data: list) -> List[Level]:
    """创建奖项等级"""
    created = failed = updated = 0
    levels = []
    for levels_data in data:
        for level_data in levels_data["spec"]:
            try:
                level, is_created = Level.objects.update_or_create(**level_data)
                if is_created:
                    created += 1
                else:
                    updated += 1

                levels.append(level)
            except Exception:
                logger.warning("Failed to create level: %s", level_data["name"])
                failed += 1

    logger.info("Levels: %d created; %d updated; %d failed.", created, updated, failed)
    return levels


def create_user_group(data: list) -> List[UserGroup]:
    """创建用户组"""
    created = failed = updated = 0
    groups = []
    for group_set_data in data:
        for group_info in group_set_data["spec"]:
            key, name = group_info.pop("key"), group_info.pop("name")
            create_params = {'id': key, 'name': name}
            if group_info.get("type"):
                create_params["type"] = group_info.pop("type")
            try:
                group, is_created = UserGroup.objects.update_or_create(**create_params)
                if is_created:
                    created += 1
                else:
                    updated += 1

                groups.append(group)
            except Exception:
                logger.exception("Failed to create approval role: %s-%s", key, name)
                failed += 1

    logger.info("User groups: %d created; %d updated; %d failed.", created, updated, failed)
    return groups


def create_rawappinfo(data: list):
    """创建申报信息配置"""
    failed = updated = 0
    rawappinfos = []
    for rawappinfo_data in data:
        spec = rawappinfo_data["spec"]
        policy_name = spec.pop("bindPolicy")
        try:
            policy = Policy.objects.get(name=policy_name)
            policy.raw_application_info = spec
            policy.save()
            updated += 1
            rawappinfos.append(policy)
        except Exception:
            failed += 1
    logger.info("Rawappinfos: %d updated; %d failed.", updated, failed)
    return rawappinfos


def create_summaryinfo(data: list):
    """创建奖项沉淀信息配置"""
    failed = updated = 0
    policies = []
    for summaryinfo_data in data:
        spec = summaryinfo_data["spec"]
        try:
            policy = Policy.objects.all()
            for p in policy:
                p.summary_info = spec
                p.save()
                policies.append(p)
            updated += 1
        except Exception:
            failed += 1
    logger.info("Summaryinfos: %d updated; %d failed.", updated, failed)
    return policies


def load_data_from_path(path: str, dry_run: bool = False) -> Dict:
    raw_datas = defaultdict(list)
    for file_path in glob.glob(str(path)):
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)
        if dry_run:
            logger.info("creating %s: %s", data["kind"], data)
            continue
        raw_datas[data["kind"]].append(data)

    return {
        "levels": create_levels(raw_datas["LevelSet"]),
        "policies": create_policies(raw_datas["Policy"]),
        "user_group": create_user_group(raw_datas["UserGroupSet"]),
        "rawappinfo": create_rawappinfo(raw_datas["RawAppInfo"]),
        "summaryinfo": create_summaryinfo(raw_datas["SummaryInfo"]),
    }
