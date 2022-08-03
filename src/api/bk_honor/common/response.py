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

import xlwt
from django.http import HttpResponse

from bk_honor.awards.models import Application, Step, Summary


def export_excel_response(application=None, application_ids=None):
    """导出excel文件"""
    header = ["项目名称", "申报部门（团队）", "申报接口人", "项目经理（项目负责人）", "项目成员（项目核心成员）", "事迹描述", "各环节审批意见"]
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment;filename=荣誉激励系统-奖项申报信息.xls'
    ws = xlwt.Workbook(encoding='utf-8')
    w = ws.add_sheet('sheet1')
    for index, h in enumerate(header):
        w.write(0, index, h)
    if application_ids:
        applications = Application.objects.filter(pk__in=application_ids)
        for rows_index, application in enumerate(applications):
            stages = application.stages.values_list("id")
            steps = Step.generator.filter(stage__in=stages)
            comment = ""
            for s in steps:
                if not s.details.get("comment"):
                    comment += ""
                else:
                    comment += s.name + ':' + s.details.get("comment", "") + "\n"
            summary = Summary.objects.filter(award=application.award, application=application).first()
            details = application.details
            data = [
                summary.details.get("project_name") if summary else details.get("name", ""),
                details.get("declaration", ""),
                ",".join(details.get("liaisons", "")),
                ",".join(details.get("project_manager", "")),
                ",".join(details.get("staffs", "")),
                details.get("description", ""),
                comment,
            ]
            for index, d in enumerate(data):
                w.write(rows_index + 1, index, d)
        ws.save(response)
        return response
    if application:
        stages = application.stages.values_list("id")
        steps = Step.generator.filter(stage__in=stages)
        comment = ""
        for s in steps:
            if not s.details.get("comment"):
                comment += ""
            else:
                comment += s.name + ':' + s.details.get("comment", "") + "\n"
        summary = Summary.objects.filter(award=application.award, application=application).first()
        details = application.details
        data = [
            summary.details.get("project_name") if summary else details.get("name", ""),
            details.get("declaration", ""),
            ",".join(details.get("liaisons", "")),
            ",".join(details.get("project_manager", "")),
            ",".join(details.get("staffs", "")),
            details.get("description", ""),
            comment,
        ]
        for index, d in enumerate(data):
            w.write(1, index, d)
        ws.save(response)
        return response
