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
from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from bk_honor.account.models import BkUser
from bk_honor.awards.constants import StageStatus
from bk_honor.awards.exceptions import StepConditionNotMeetError
from bk_honor.awards.parsers import load_from_db

from .models import Application, ApprovalPeriod, AvailablePeriod, Award, Policy, Stage, Step, Summary

################
# In
################


class CreatePolicySLZ(serializers.Serializer):
    """创建 Policy Serializer"""

    name = serializers.CharField(required=False)


class QueryPolicySLZ(serializers.Serializer):
    """查询 Policy Serializer"""

    level = serializers.CharField(required=False)


class SearchSerializer(serializers.Serializer):
    """首页搜素 Serializer"""

    keyword = serializers.CharField(required=False)


class CreateAwardSLZ(serializers.ModelSerializer):
    """创建 Award Serializer"""

    class Meta:
        model = Award
        exclude = ("id", "enabled", "year")


class QueryAwardSLZ(serializers.Serializer):
    """查询 Award Serializer"""

    level = serializers.CharField(help_text=_("奖项级别"), required=False)
    status = serializers.CharField(help_text=_("奖项状态"), required=False)
    name = serializers.CharField(help_text=_("奖项名称"), required=False)


class AwardBulkCopySLZ(serializers.Serializer):
    """批量复制 Award Serializer"""

    award_ids = serializers.ListField(help_text=_("奖项id列表"))


class ApplicationBulkExportSLZ(serializers.Serializer):
    """批量导出 Application Serializer"""

    application_ids = serializers.ListField(help_text=_("奖项申报id列表"))


class AwardEditSLZ(serializers.ModelSerializer):
    """编辑 Award Serializer"""

    class Meta:
        model = Award
        exclude = ("id", "enabled", "year", "orgs")


class CreateApplicationPromoteSLZ(serializers.ModelSerializer):
    """创建 Application Promote Serializer"""

    promotion = serializers.JSONField(help_text=_("获奖宣导材料"))

    class Meta:
        model = Application
        exclude = ("id", "enabled", "status")


class CreateApplicationSLZ(serializers.Serializer):
    """创建 Application Serializer"""

    liaisons = serializers.ListField(help_text=_("申报接口人列表"), required=False)
    staffs = serializers.ListField(help_text=_("项目成员"), required=False)
    details = serializers.JSONField(help_text=_("详情"))


class UpdateApplicationSLZ(serializers.ModelSerializer):
    """更新 Application Serializer"""

    class Meta:
        model = Application
        exclude = (
            "id",
            "enabled",
            "status",
            "created_at",
            "updated_at",
            "award",
            "current_step",
            "applicants",
            "liaisons",
            "staffs",
            "user_groups",
            "addons",
        )


class CreateJudgeSLZ(serializers.Serializer):
    """创建 AwardJudge Serializer"""

    application_id = serializers.CharField(help_text=_("奖项申报id"))
    judge_time = serializers.ListField(help_text=_("可评审时间列表"))


class ApplicationJudgeSLZ(serializers.Serializer):
    """评委复审 Serializer"""

    application_id = serializers.CharField(help_text=_("奖项申报id"))


class QuerySummarySLZ(serializers.Serializer):
    """查询 Summary Serializer"""

    award_name = serializers.CharField(help_text=_("奖项名称"), required=False)
    liaison = serializers.CharField(help_text=_("奖项接口人"), required=False)
    search_datetime = serializers.IntegerField(help_text=_("查询日期"), required=False)

    summary_id = serializers.CharField(help_text=_("奖项沉淀id"), required=False)


class QueryAwardSummarySLZ(serializers.Serializer):
    """查询 AwardSummary Serializer"""

    policy_id = serializers.CharField(help_text=_("奖项策略id"))
    year = serializers.CharField(help_text=_("年份"))


class ApproveStepSLZ(serializers.Serializer):
    """审批通过 Serializer"""

    comment = serializers.CharField(help_text=_("评语"), required=False, allow_null=True, allow_blank=True)


class BulkApproveStepSLZ(serializers.Serializer):
    """审批通过 Serializer"""

    application_ids = serializers.ListField(help_text=_("奖项申报id列表"), default=[])


class BulkRejectStepSLZ(serializers.Serializer):
    """审批通过 Serializer"""

    application_ids = serializers.ListField(help_text=_("奖项申报id列表"), default=[])


class RejectStepSLZ(serializers.Serializer):
    """审批驳回 Serializer"""

    comment = serializers.CharField(help_text=_("评语"))


class NotifyStepSLZ(serializers.Serializer):
    """通知 Serializer"""

    force_message = serializers.CharField(help_text=_("通知内容，传入此值时将忽略默认配置通知内容"), required=False)
    force_receivers = serializers.ListField(help_text=_("通知人，传入此值时将忽略默认配置通知人"), required=False)


class CollectionStepSLZ(serializers.Serializer):
    """收集 Serializer"""

    collection_data = serializers.JSONField(help_text=_("收集数据"))


class CreateSummarySLZ(serializers.ModelSerializer):
    """创建奖项沉淀 Serializer"""

    award_id = serializers.CharField(required=False, help_text=_("奖项id"))
    application_id = serializers.CharField(required=False, help_text=_("奖项申报id"))

    policy_id = serializers.CharField(required=False, help_text=_("奖项沉淀id"))
    year = serializers.IntegerField(required=False, help_text=_("奖项沉淀关联的年份"))

    class Meta:
        model = Summary
        exclude = ("id", "enabled", "award", "status", "application", "policy")


class SummaryEditSLZ(serializers.ModelSerializer):
    """编辑 AwardSummary Serializer"""

    policy_id = serializers.UUIDField(required=False, help_text=_("奖项沉淀id"))

    class Meta:
        model = Summary
        exclude = ("id", "enabled", "award", "application", "policy")


class QueryApplicationSLZ(serializers.Serializer):
    """查询 Application Serializer"""

    award_name = serializers.CharField(help_text=_("奖项名称"), required=False)
    # 个人中心页面查询字段
    username = serializers.CharField(help_text=_("用户名"), required=False)
    application_status = serializers.CharField(help_text=_("申请状态"), required=False)
    search_datetime = serializers.IntegerField(help_text=_("查询日期"), required=False)

    # 系统管理页面查询字段
    level = serializers.CharField(help_text=_("奖项级别"), required=False)
    award_status = serializers.CharField(help_text=_("奖项状态"), required=False)
    liaison = serializers.CharField(help_text=_("奖项接口人"), required=False)


class QueryApplicationApprovesSLZ(serializers.Serializer):
    """查询 Application Approves Serializer"""

    award_name = serializers.CharField(help_text=_("奖项名称"), required=False)
    search_datetime = serializers.IntegerField(help_text=_("查询日期"), required=False)


class CreateAvailablePeriodSLZ(serializers.ModelSerializer):
    """评委空闲时间"""

    started_at = serializers.CharField(help_text=_("开始时间，Unix时间戳"))
    ended_at = serializers.CharField(help_text=_("结束时间，Unix时间戳"))

    class Meta:
        model = AvailablePeriod
        fields = ("started_at", "ended_at")


class AvailablePeriodListSLZ(serializers.Serializer):
    """评委空闲时间段列表"""

    available_periods = CreateAvailablePeriodSLZ(many=True)
    username = serializers.CharField(help_text=_("用户名"), required=False)


class CreateApprovalPeriod(serializers.Serializer):
    """创建审批时间"""

    started_at = serializers.CharField(help_text=_("开始时间，Unix时间戳"))
    ended_at = serializers.CharField(help_text=_("结束时间，Unix时间戳"))

    step_index = serializers.IntegerField(help_text="步骤 index", default=-1)


class QueryAvailablePeriodsSLZ(serializers.Serializer):
    """查询评委空闲时间段"""

    step_index = serializers.IntegerField(help_text="步骤 index", default=-1, required=False)
    last_minutes = serializers.IntegerField(help_text="时长(分钟)", default=120, required=False)


class QueryRecordsSLZ(serializers.Serializer):
    """查询指定用户获奖记录"""

    username = serializers.CharField(help_text=_("用户名"), required=False)


################
# Out
################
class PaginatedSerializer(serializers.Serializer):
    count = serializers.IntegerField(required=False, help_text="总数")
    next = serializers.CharField(required=False, help_text="下一页游标")
    previous = serializers.CharField(required=False, help_text="上一页游标")


class AwardSearchDataSLZ(serializers.Serializer):
    """搜索接口: 奖项序列化器"""

    id = serializers.CharField(help_text="奖项id")
    name = serializers.CharField(help_text="奖项名称")
    year = serializers.IntegerField(help_text="奖项年份")

    # FIXME: 变量名保持 snake case
    fullName = serializers.CharField(help_text="奖项全称", source="full_name")


class SummarySearchDataSLZ(serializers.ModelSerializer):
    """搜索接口: 奖项沉淀序列化器"""

    id = serializers.SerializerMethodField(help_text="奖项沉淀id")
    name = serializers.SerializerMethodField(help_text="奖项沉淀名称")
    fullName = serializers.SerializerMethodField(help_text="奖项沉淀全称")

    class Meta:
        model = Award
        fields = ("id", "name", "year", "fullName")

    def get_fullName(self, obj) -> str:
        return str(obj.year) + " " + obj.policy.name

    def get_id(self, obj) -> str:
        return obj.policy.id

    def get_name(self, obj) -> str:
        return obj.policy.name


class SearchDataSLZ(serializers.Serializer):
    awards = AwardSearchDataSLZ(many=True, help_text="奖项列表")
    summaries = SummarySearchDataSLZ(many=True, help_text="奖项沉淀列表")


class SearchOutSLZ(serializers.Serializer):
    """搜索 Out Serializer"""

    search_data = SearchDataSLZ(help_text=_("搜索数据"))


class UserGroupSLZ(serializers.Serializer):
    name = serializers.CharField(help_text=_("用户组名称"))
    id = serializers.CharField(help_text=_("用户组id"))


class PolicySLZ(serializers.ModelSerializer):
    level = serializers.CharField(source="level.key")
    get_user_groups_from_steps = UserGroupSLZ(many=True, help_text=_("用户组列表"))

    class Meta:
        model = Policy
        fields = "__all__"


class MinimalPolicySLZ(serializers.ModelSerializer):
    level = serializers.CharField(source="level.key")

    class Meta:
        model = Policy
        exclude = ("stages", "global_config")


class MinimalIndexPolicySLZ(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ("id", "name")


class MinimalAwardSLZ(serializers.ModelSerializer):
    policy = MinimalPolicySLZ(help_text="所属策略")

    class Meta:
        model = Award
        fields = "__all__"


class AwardSLZ(serializers.ModelSerializer):
    policy = MinimalPolicySLZ(help_text="所属策略")

    class Meta:
        model = Award
        fields = "__all__"


class PaginatedPolicySerializer(PaginatedSerializer):
    results = PolicySLZ(many=True, help_text="结果")


class MinimalStepSLZ(serializers.ModelSerializer):
    class Meta:
        model = Step
        fields = ("id", "name", "status", "type")


class ApplicationSLZ(serializers.ModelSerializer):

    award = MinimalAwardSLZ()
    current_step = MinimalStepSLZ()
    is_summary_filled = serializers.SerializerMethodField(help_text="是否填写奖项沉淀")
    is_current_step_finished = serializers.SerializerMethodField(help_text="当前步骤是否完成")

    class Meta:
        model = Application
        fields = "__all__"

    def get_is_summary_filled(self, obj) -> bool:
        return Summary.objects.filter(award=obj.award, application=obj).exists()

    def get_is_current_step_finished(self, obj) -> bool:
        try:
            return load_from_db(obj.current_step).check_condition() == StageStatus.FINISHED.value
        except StepConditionNotMeetError:
            return False


class ApplicationDetailsSLZ(serializers.ModelSerializer):

    award = MinimalAwardSLZ()
    current_step = MinimalStepSLZ()
    is_all_applications_type_approval = serializers.SerializerMethodField(help_text="是否全部申请类型审批")

    class Meta:
        model = Application
        fields = "__all__"

    def get_is_all_applications_type_approval(self, obj):
        if not self.context["is_all_applications_type_approval"]:
            return False
        return True


class DetailApplicationSLZ(serializers.ModelSerializer):

    award = AwardSLZ()
    current_step = MinimalStepSLZ()

    class Meta:
        model = Application
        fields = "__all__"


class PaginatedApplicationSerializer(PaginatedSerializer):
    results = ApplicationSLZ(many=True, help_text="结果")


class PaginatedApplicationDetailsSerializer(PaginatedSerializer):
    results = ApplicationDetailsSLZ(many=True, help_text="结果")


class AwardRecordsSLZ(serializers.Serializer):
    level = serializers.CharField(help_text="奖项级别", source="policy.level.key")
    name = serializers.CharField(help_text="奖项策略名称", source="policy.name")
    year = serializers.IntegerField(help_text="年份")
    quarter = serializers.SerializerMethodField(help_text="期数")
    chinese_name = serializers.SerializerMethodField(help_text="中文名称")
    english_name = serializers.SerializerMethodField(help_text="英文名称")
    project_name = serializers.SerializerMethodField(help_text="项目名称")

    def get_quarter(self, obj: Summary):
        return obj.award.quarter if obj.award else 0

    def get_chinese_name(self, obj: Summary):
        if not self.context["user"]:
            user = BkUser.objects.filter(username=self.context["username"]).first()
            return user.chinese_name if user else ""
        return self.context["user"].chinese_name

    def get_english_name(self, obj: Summary):
        if not self.context["user"]:
            return self.context["username"]
        return self.context["user"].username

    def get_project_name(self, obj: Summary):
        return obj.details.get("project_name", "")


class DetailAwardSLZ(serializers.ModelSerializer):
    policy = PolicySLZ(help_text="所属策略")

    class Meta:
        model = Award
        fields = "__all__"


class IndexAwardSLZ(serializers.ModelSerializer):
    """首页奖项列表 Serializer"""

    policy = MinimalIndexPolicySLZ(help_text="所属策略名称")

    class Meta:
        model = Award
        fields = ("name", "award_slideshow", "quarter", "status", "year", "ended_at", "id", "policy")


class IndexSummariesAwardSLZ(serializers.Serializer):
    """首页奖项列表 Serializer"""

    id = serializers.CharField(help_text="奖项策略id", source="policy.id")
    name = serializers.CharField(help_text="奖项策略名称", source="policy.name")
    year = serializers.IntegerField(help_text="年份")


class IndexAwardsSLZ(serializers.Serializer):
    """首页奖项沉淀筛选"""

    awards = IndexAwardSLZ(many=True, help_text="首页奖项列表")


class IndexSummaryAwardsSLZ(serializers.Serializer):
    """首页奖项沉淀筛选"""

    summaries = IndexSummariesAwardSLZ(many=True, help_text="首页奖项列表")


class PaginatedAwardSerializer(PaginatedSerializer):
    results = AwardSLZ(many=True, help_text="结果")


class PaginatedAwardRecordsSerializer(PaginatedSerializer):
    results = AwardRecordsSLZ(many=True, help_text="结果")


class DetailSummarySLZ(serializers.ModelSerializer):
    award = AwardSLZ(help_text="所属奖项")
    policy_id = serializers.SerializerMethodField(help_text="所属策略id")

    class Meta:
        model = Summary
        exclude = ("policy", "id")

    def get_policy_id(self, obj):
        return obj.policy.id


class SummarySLZ(serializers.ModelSerializer):
    award = MinimalAwardSLZ(help_text="所属奖项")
    policy_name = serializers.SerializerMethodField(help_text="所属策略名称")

    class Meta:
        model = Summary
        fields = "__all__"

    def get_policy_name(self, obj) -> str:
        return obj.policy.name


class SummaryWithLikedSLZ(SummarySLZ):
    liked = serializers.SerializerMethodField(help_text="当前用户是否已点赞")
    like_count = serializers.SerializerMethodField(help_text="点赞数")

    def get_liked(self, obj: Summary) -> bool:
        """获取当前用户是否已点赞"""
        return obj.likes.filter(username=self.context["request"].user.username).exists()

    def get_like_count(self, obj: Summary) -> int:
        """获取点赞数"""
        return obj.likes.count()


class PaginatedSummarySerializer(PaginatedSerializer):
    results = SummaryWithLikedSLZ(many=True, help_text="结果")


class MinimalStageSLZ(serializers.ModelSerializer):
    """阶段 Serializer"""

    class Meta:
        model = Stage
        fields = ("id", "name", "status")


class StepSLZ(serializers.ModelSerializer):
    is_first = serializers.BooleanField(help_text="是否为第一步")
    is_last = serializers.BooleanField(help_text="是否为最后一步")
    is_final_approval = serializers.BooleanField(help_text="是否为最终审批步骤")
    stage = MinimalStageSLZ(help_text="所属阶段")

    summary_info = serializers.SerializerMethodField(help_text="奖项沉淀信息")

    @staticmethod
    def fulfill_auto_execute(result: dict):
        """填充自动执行字段"""

        # 由于 policy 本身未进行建模，这里我们临时操作 dict
        if "auto_execute" not in result['policy']:
            result["policy"]["auto_execute"] = settings.DEFAULT_STEP_AUTO_EXECUTE

    def to_representation(self, instance):
        result = super().to_representation(instance)
        self.fulfill_auto_execute(result)

        return result

    def get_summary_info(self, obj: Step):
        """获取奖项沉淀信息"""
        award_id = obj.stage.application.award_id
        application = obj.stage.application_id
        summary = Summary.objects.filter(
            award_id=award_id,
            application_id=application,
            enabled=True,
        ).first()
        return {"summary_id": summary.id, "is_summary_filled": True, "status": summary.status} if summary else {}

    class Meta:
        model = Step
        fields = "__all__"


class StageSLZ(serializers.ModelSerializer):
    """阶段 Serializer"""

    steps = StepSLZ(many=True)

    class Meta:
        model = Stage
        fields = "__all__"


class ApplicationStepSLZ(serializers.Serializer):
    """申请阶段 Serializer"""

    stages = StageSLZ(many=True)


class AvailablePeriodSLZ(serializers.ModelSerializer):
    """评委空闲时间"""

    class Meta:
        model = AvailablePeriod
        fields = "__all__"


class ApprovalPeriodSLZ(serializers.ModelSerializer):
    """奖项审批时间"""

    class Meta:
        model = ApprovalPeriod
        fields = "__all__"


class PeriodsSLZ(serializers.Serializer):
    """时间段"""

    started_at = serializers.DateTimeField(help_text="开始时间")
    ended_at = serializers.DateTimeField(help_text="结束时间")


class AvailablePeriodByUserSLZ(serializers.Serializer):
    """评委空闲时间"""

    username = serializers.SerializerMethodField(help_text="用户名")
    available_periods = serializers.SerializerMethodField(help_text="空闲时间")

    def get_username(self, obj: tuple):
        return obj[0]

    def get_available_periods(self, obj: tuple):
        return PeriodsSLZ(many=True, instance=obj[1]).data


class MixedPeriodsSLZ(serializers.Serializer):
    """混合了两种时间段的返回：按评委聚合的空闲时间和交集时间"""

    username_periods = AvailablePeriodByUserSLZ(many=True)
    intersection_periods = PeriodsSLZ(many=True)
