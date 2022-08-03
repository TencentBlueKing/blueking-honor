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
  <div class="content">
    <left-detail
      v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }"
      :detail-list="formList"></left-detail>
  </div>
</template>
<script>
import moment from 'moment';

import { LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
import LeftDetail from '@/components/user/left-detail.vue';
export default {
  components: {
    LeftDetail,
  },
  data() {
    return {
      formLoading: true,
      formList: [
        {
          key: 'name',
          label: '奖项名称',
          type: 'bk-input',
          default: '',
          required: true,
          placeholder: '请输入奖项名称',
          rules: [
            {
              max: 10,
              message: '不能多于10个字符',
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'level',
          label: '级别',
          default: '',
          hidden: true,
        },
        {
          key: 'description',
          label: '奖项描述',
          type: 'bk-input',
          default: '',
          required: true,
          placeholder: '请输入奖项描述',
          componentType: 'textarea',
        },
        {
          key: 'liaisons',
          label: '知会人员',
          type: 'bk-tag-input',
          'allow-create': true,
          default: [],
          required: true,
        },
      ],
    };
  },
  mounted() {
    this.id = this.$route.query.id;
    if (this.id) {
      this.fetchTempleDetail();
    }
  },
  methods: {
    // 详情
    async fetchTempleDetail() {
      try {
        const res = await this.$store.dispatch('system/getTempleDetail', this.id);
        this.setFormDetail(res);
      } catch (e) {
        console.error(e);
        if (e.message.search('request canceled') === -1) {
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.message || '系统错误',
            ellipsisLine: 2,
            ellipsisCopy: true,
          });
        }
      }
    },
    // 设置default值
    setFormDetail(data) {
      this.formList.forEach((e) => {
        e.default = data[e.key];
        if (e.key === 'status') {
          e.default = this.type === 'view' ? STATUS_ENUM[data[e.key]] : data[e.key];
        } else if (e.key === 'daterange-picker') {
          e.default = this.type === 'view' ? `${moment(data.started_at * 1000).format('YYYY-MM-DD')} 至 ${moment(data.ended_at * 1000).format('YYYY-MM-DD')}`
            : [moment(data.started_at * 1000), moment(data.ended_at * 1000)];
        } else if (e.key === 'liaisons') {
          e.default = data[e.key].join(',');
        } else if (e.key === 'level') {
          e.default = LEVEL_ENUM[data.level];
        }
        this.formLoading = false;
      });
    },
    cancel() {
      this.$router.back(-1);
    },
  },
};
</script>
