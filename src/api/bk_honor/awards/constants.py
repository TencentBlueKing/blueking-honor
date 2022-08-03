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
from blue_krill.data_types.enum import EnumField, StructuredEnum


class Quarter(StructuredEnum):
    """季度"""

    Q1 = 1
    Q2 = 2
    Q3 = 3
    Q4 = 4


class AwardStatus(StructuredEnum):
    """奖项状态"""

    PENDING = EnumField("pending", label="未开始")
    STARTED = EnumField("started", label="可申报")
    UNAPPLICABLE = EnumField("unapplicable", label="不可申报")
    EXPIRED = EnumField("expired", label="已过期")


class ApplicationStatus(StructuredEnum):
    """申报状态"""

    STARTED = EnumField("started", label="申报中")
    FAILED = EnumField("failed", label="未获奖")
    SUCCEED = EnumField("succeed", label="已获奖")


class SummaryStatus(StructuredEnum):
    """奖项沉淀状态"""

    STARTED = EnumField("started", label="已填写")
    REJECT = EnumField("rejected", label="驳回")
    SUCCEED = EnumField("succeed", label="已通过")


class StageStatus(StructuredEnum):
    """环节状态"""

    PENDING = EnumField("pending", label="未开始")
    STARTED = EnumField("started", label="进行中")
    FINISHED = EnumField("finished", label="完成")
    ABORTED = EnumField("aborted", label="中止")


class StepType(StructuredEnum):
    """步骤类型"""

    NOTIFICATION = EnumField("notification", label="通知")
    APPROVAL = EnumField("approval", label="审批")

    SUMMARY_COLLECTION = EnumField("summary_collection", label="奖项沉淀收集")
    EXTRA_INFO_COLLECTION = EnumField("extra_info_collection", label="额外信息收集")
    APPROVAL_TIME_COLLECTION = EnumField("approval_time_collection", label="审批时间收集")


class ApprovalOperation(StructuredEnum):
    """审批操作"""

    APPROVE = EnumField("approve", label="同意")
    REJECT = EnumField("reject", label="拒绝")


class FixedUserGroup(StructuredEnum):
    """固定用户组"""

    AWARD_LIAISON = EnumField("award_liaison", label="奖项联系人")
    APPLICATION_LIAISON = EnumField("application_liaison", label="申报联系人")
    APPLICANT = EnumField("applicant", label="申报人")


class DefaultComment(StructuredEnum):
    """季度"""

    APPROVE_COMMENT = EnumField("通过", label="通过")
    REJECT_COMMENT = EnumField("未通过", label="未通过")
