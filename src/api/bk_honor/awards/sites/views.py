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

from blue_krill.web.drf_utils import inject_serializer
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser

from bk_honor.awards.sites.serializers import UploadFileResponseSerializer, UploadFileSerializer
from bk_honor.common.bk_repo import check_file_valid, upload_file_to_bk_repo
from bk_honor.common.error_codes import error_codes

logger = logging.getLogger(__name__)


class UploadFileViewSet(viewsets.ViewSet):
    """上传文件"""

    parser_classes = (MultiPartParser,)

    @inject_serializer(
        body_in=UploadFileSerializer, out=UploadFileResponseSerializer, tags=["上传文件"], operation_summary="上传图片"
    )
    @action(detail=False, methods=["POST"])
    def images(self, request, validated_data):
        """上传图片"""
        file_obj = validated_data["file"]
        try:
            check_file_valid(file_obj, settings.SUPPORTED_IMAGE_TYPES, max_mb=settings.IMAGE_MAX_MB)
        except Exception as e:
            raise error_codes.UPLOADED_FILE_INVALID.format(str(e))

        try:
            url = upload_file_to_bk_repo(file_obj)
        except Exception:
            logger.exception("upload file to bk repo failed")
            raise error_codes.UPLOAD_FILE_FAILED

        return {"url": url}

    @inject_serializer(
        body_in=UploadFileSerializer, out=UploadFileResponseSerializer, tags=["上传文件"], operation_summary="上传文件"
    )
    @action(detail=False, methods=["POST"])
    def files(self, request, validated_data):
        """上传文件"""
        file_obj = validated_data["file"]
        try:
            check_file_valid(file_obj, settings.SUPPORTED_FILE_TYPES, max_mb=settings.FILE_MAX_MB)
        except Exception as e:
            raise error_codes.UPLOADED_FILE_INVALID.format(str(e))

        try:
            url = upload_file_to_bk_repo(file_obj)
        except Exception:
            logger.exception("upload file to bk repo failed")
            raise error_codes.UPLOAD_FILE_FAILED

        return {"url": url}
