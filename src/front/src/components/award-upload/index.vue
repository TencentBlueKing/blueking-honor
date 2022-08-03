<!--
* Tencent is pleased to support the open source community by making
* 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) available.
*
* Copyright (C) 2021 THL A29 Limited, a Tencent company.  All rights reserved.
*
* 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition) is licensed under the MIT License.
*
* License for 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community Edition):
*
* ---------------------------------------------------
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
* documentation files (the "Software"), to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
* to permit persons to whom the Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in all copies or substantial portions of
* the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
* THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
* CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
* IN THE SOFTWARE.
-->
<template>
  <bk-upload
    :tip="''"
    :with-credentials="true"
    :handle-res-code="handleRes"
    :name="'file'"
    :multiple="false"
    :theme="theme"
    :files="file"
    :size="50"
    :header="{ name: 'X-CSRFToken', value: CSRFToken }"
    :url="theme === 'picture' ? '/api/v1/upload/images/' : '/api/v1/upload/files/'"
    @on-done="handleDone"
    @on-delete="handleDelete"
  ></bk-upload>
</template>

<script>
import cookie from 'cookie';

export default {
  model: {
    prop: 'value',
    event: 'update',
  },
  props: {
    value: [String, Array],
    theme: {
      type: String,
      default() {
        return 'draggable';
      },
    },
    file: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    const CSRFToken = cookie.parse(document.cookie)[`${window.PROJECT_CONFIG.BKPAAS_APP_ID}_csrftoken`];
    return {
      CSRFToken,
    };
  },
  methods: {
    handleRes(response) {
      if (response.url) {
        this.url = response.url;
        return true;
      }
      return false;
    },
    handleDone(fileList) {
      let urlList = fileList.reduce((prev, curr) => (curr.done ? prev.concat(curr.responseData.url) : prev), []);
      urlList = urlList.map(e => ({
        url: e,
      }));
      this.$emit('update', urlList);
    },
    handleDelete(file, fileList) {
      const urlList = fileList.reduce((prev, curr) => (curr.done ? prev.concat(curr.responseData.url) : prev), []);
      this.$emit('update', urlList);
    },
  },

};
</script>
