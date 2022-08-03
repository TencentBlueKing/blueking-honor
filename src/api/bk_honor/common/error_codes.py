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
from blue_krill.web.std_error import ErrorCode


class ErrorCodes:
    # 通用
    CANNOT_FIND_TEMPLATE = ErrorCode("找不到模板")
    # 奖项相关
    AWARD_NOT_EXIST = ErrorCode("选择的奖项不存在")
    AWARD_CANNOT_BE_CREATED = ErrorCode("奖项创建失败")
    AWARD_CANNOT_BE_COPIED = ErrorCode("奖项复制失败")
    AWARD_CANNOT_BE_UPDATED = ErrorCode("奖项更新失败")
    AWARD_CANNOT_BE_DELETED = ErrorCode("奖项删除失败")
    AWARD_CANNOT_BE_APPLIED = ErrorCode("奖项状态不是可申报，请联系管理员")
    AWARD_STATUS_MANAGEMENT = ErrorCode("处理奖项状态")

    # 奖项沉淀相关
    AWARD_SUMMARY_CANNOT_BE_CREATED = ErrorCode("创建奖项沉淀内容失败")
    AWARD_SUMMARY_CANNOT_BE_UPDATED = ErrorCode("更新奖项沉淀内容失败")
    AWARD_SUMMARY_CANNOT_BE_DELETED = ErrorCode("删除奖项沉淀内容失败")
    AWARD_SUMMARY_ALREADY_EXISTS = ErrorCode("该团队申请的奖项沉淀内容已存在")
    AWARD_SUMMARY_NOT_EXIST = ErrorCode("该奖项沉淀内容不存在")
    AWARD_SUMMARY_UPDATE_LIKE_FAILED = ErrorCode("奖项沉淀点赞失败")
    AWARD_SUMMARY_UPDATE_STATUS_FAILED = ErrorCode("更新奖项沉淀状态失败")
    MISSING_REQUIRED_FIELDS = ErrorCode("缺少必填项")

    # 申报相关
    APPLICATION_CANNOT_ENTER_NEXT = ErrorCode("申报无法进入下一环节")
    APPLICATION_CANNOT_ABORTED = ErrorCode("申报无法中止")
    APPLICATION_CANNOT_BE_CREATED = ErrorCode("发起申报失败")
    APPLICATION_CANNOT_BE_UPDATED = ErrorCode("申报更新失败")
    APPLICATION_EXPORT_FAILED = ErrorCode("申报导出失败")
    APPLICANT_ALREADY_APPLIED = ErrorCode("该申报人已经申请过该奖项")
    APPLICANT_PROMOTION_CANNOT_BE_CREATED = ErrorCode("编辑奖项沉淀内容失败")
    APPLICATION_BATCH_PASS_FAILED = ErrorCode("批量通过申报失败")
    APPLICATION_BATCH_REJECT_FAILED = ErrorCode("批量驳回申报失败")
    APPLICATION_USER_PERMISSION_ERROR = ErrorCode("当前用户权限错误")

    # 步骤相关
    APPLICATION_STEP_NOT_MATCHED = ErrorCode("请求的步骤与申报当前步骤不匹配")
    APPLICATION_STEP_NOT_STARTED = ErrorCode("该步骤未开始")
    APPLICATION_CANNOT_FINISHED = ErrorCode("申报无法结束")
    OPERATION_NOT_SUPPORTED = ErrorCode("当前步骤不支持该操作")
    FAILED_TO_OPERATE_STEP = ErrorCode("操作步骤失败")

    # 策略相关
    POLICY_NOT_EXIST = ErrorCode("该奖项对应策略不存在")

    # 评审时间相关
    AVAILABLE_PERIOD_CANNOT_BE_CREATED = ErrorCode("创建可用时间段失败")
    APPROVAL_PERIOD_CANNOT_BE_CREATED = ErrorCode("创建评审时间段失败")

    # 时间相关
    TIME_START_LATER_THAN_END = ErrorCode("起始时间不能晚于结束时间")

    # 文件上传相关
    UPLOADED_FILE_INVALID = ErrorCode("上传文件无效")
    UPLOAD_FILE_FAILED = ErrorCode("上传文件失败")

    def dump(self, fh=None):
        """A function to dump ErrorCodes as markdown table."""
        attrs = [attr for attr in dir(self) if attr.isupper()]
        table = {}
        for attr in attrs:
            code = getattr(self, attr)
            if code.code_num == -1:
                continue
            table[code.code_num] = code.message

        print("| 错误码 | 描述 |", file=fh)
        print("| - | - |", file=fh)
        for code_num, message in sorted(table.items()):
            print(f"| {code_num} | {message} |", file=fh)


error_codes = ErrorCodes()
