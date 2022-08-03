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
import random
import string
import time
from typing import List

from bkstorages.backends.bkrepo import BKRepoStorage

logger = logging.getLogger(__name__)
bk_repo_storage = BKRepoStorage()


def check_file_valid(file_obj, support_extensions: List[str], max_mb: int = 10):
    """检查文件是否合法"""
    if file_obj.size // 1024 // 1024 > max_mb:
        raise Exception(f"文件大小超过最大限制 {max_mb}MB")

    if file_obj.name.split(".")[-1] not in support_extensions:
        raise Exception(f"文件类型不支持，请上传以下类型的文件：{','.join(support_extensions)}")

    return


def make_unique_key(file_obj, random_len: int = 8) -> str:
    """生成唯一文件 key"""
    now = int(time.time())
    random_str = "".join(random.choices(string.ascii_lowercase, k=random_len))
    return f"{now}_{random_str}_{file_obj.name}"


def upload_file_to_bk_repo(file_obj) -> str:
    """上传文件"""
    name = make_unique_key(file_obj)
    bk_repo_storage.save(name, file_obj)
    return bk_repo_storage.url(name)


def get_all_files_in_bk_repo():
    """[debug]显示所有文件，仅作为调试工具，请勿在运行时调用"""
    return bk_repo_storage.listdir("/")


def delete_all_file(dry_run: bool = True):
    """[debug]删除所有文件，仅作为调试工具，请勿在运行时调用"""
    all_files = get_all_files_in_bk_repo()
    for files in all_files:
        if not files:
            continue

        for file in files:
            if not dry_run:
                bk_repo_storage.delete(file)

            logger.info(f"【DEBUGGING】Deleting file in bk_repo: {file}")
