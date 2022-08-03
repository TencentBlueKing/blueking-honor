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


class SystemRole(StructuredEnum):
    """
    系统角色
    """

    ADMIN = "admin"
    USER = "user"


class ResourceRole(StructuredEnum):
    """
    资源角色
    """

    NOBODY = EnumField("nobody", "无身份")
    LIAISON = EnumField("liaison", "接口人")
    APPLICANT = EnumField("applicant", "申请人")
    STAFF = EnumField("staff", "团队成员")
    APPROVER = EnumField("approver", "审批人")


class GroupType(StructuredEnum):
    """
    分组类型
    """

    SYSTEM = EnumField("system", "系统分组")

    # 针对模型固定分组字段，例如 application.liasion
    FIXED = EnumField("fixed", "固定分组")
    # policy 中指定的动态分组，由数据驱动
    DYNAMIC = EnumField("dynamic", "动态分组")
    # 申报中间环节需要即时指定的角色分组，动态添加到用户组
    SPECIFIC = EnumField("specific", "指定分组")
