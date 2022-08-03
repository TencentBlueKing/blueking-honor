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


class StepConditionNotMeetError(Exception):
    """步骤状态未满足流转条件"""


class AlreadyLastStepError(Exception):
    """已经是最后一步骤"""


class AlreadyLastStageError(Exception):
    """已经是最后一阶段"""


class NotSupportStepOperation(Exception):
    """不支持步骤操作"""

    def __init__(self, operation: str, all_operations: list, *args):
        super().__init__(args)

        self.operation = operation
        self.message = f"该步骤不支持操作 {self.operation}，仅支持 {','.join(all_operations)}"


class AlreadyNotifiedError(Exception):
    """已经通知过"""
