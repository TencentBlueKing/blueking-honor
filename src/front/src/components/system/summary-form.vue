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
  <bk-dialog
    v-model="dialogVisible"
    theme="primary"
    width="900"
    :mask-close="false"
    :on-close="handleClose"
    :show-footer="false">
    <div class="edit">
      <bk-form class="policy_form" :label-width="150">
        <bk-form-item label="奖项策略" :required="true">
          <bk-select
            v-model="policyId"
            placeholder="请选择奖项策略"
            :clearable="false"
            @change="selectPolicy">
            <bk-option
              v-for="(option, i) in policyList"
              :key="i"
              :id="option.id"
              :name="option.name">
            </bk-option>
          </bk-select>
        </bk-form-item>
        <bk-form-item label="项目年份" :required="true">
          <bk-date-picker v-model="year" placeholder="选择项目年份" type="year">
          </bk-date-picker>
        </bk-form-item>
      </bk-form>
      <edit-form
        v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }"
        ref="editFormRef"
        @submit="submit"
        :form-list="editFormList">
        <div></div>
      </edit-form>
    </div>
    <div class="btn-wrapper">
      <bk-button :theme="'primary'" class="mr10" @click="validate">
        提 交
      </bk-button>
      <bk-button :theme="'default'" @click="handleClose" :title="'基础按钮'" class="mr10" style="padding: 0 30px;">
        取 消
      </bk-button>
    </div>
  </bk-dialog>
</template>

<script>
import moment from 'moment';

import editForm from '@/components/system/edit-form.vue';
export default {
  components: {
    editForm,
  },
  props: {
    visible: {
      type: Boolean,
      default: () => false,
    },
    summaryData: {
      type: Object,
      default: () => {},
    },
  },
  data() {
    return {
      dialogVisible: false,
      formLoading: false,
      policyId: '',
      year: '',
      summaryDetail: [],
      policyList: [],
      editFormList: [],
    };
  },

  watch: {
    async visible(value) {
      this.dialogVisible = value;
      if (value) {
        await this.fetchSummaryDetail();
        this.fetchData();
      }
    },
  },

  mounted() {
  },

  methods: {
    // 获取策略
    async fetchData() {
      const params = {
        page_size: 1000,
      };
      try {
        const res = await this.$store.dispatch('system/getPoliciesList', params);
        this.policyList = res.results;
        this.editFormList = this.policyList.find(e => e.id === this.policyId).summary_info;
        this.setFormDetail(this.summaryDetail);
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
    // 详情
    async fetchSummaryDetail() {
      this.formLoading = true;
      try {
        const res = await this.$store.dispatch('system/getSummaryDetail', this.summaryData.summaryId);
        this.policyId = res.award.policy.id;
        this.year = moment(Date.parse(res.year)).format();
        this.summaryDetail = res.details || [];
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
      } finally {
        this.formLoading = false;
      }
    },

    // 设置default值
    setFormDetail(data) {
      this.editFormList && this.editFormList.forEach((e) => {
        e.default = data[e.key];
        this.formLoading = false;
      });
    },

    // 编辑奖项沉淀
    async submit(value) {
      value.award_id = this.summaryData.awardId;
      value.application_id = this.summaryData.id;
      value.id = this.summaryData.summaryId;
      const year = this.year ? moment(this.year).format('YYYY') : '';
      const params = {
        details: value,
        year,
        policy_id: this.policyId,
      };

      try {
        const res = await this.$store.dispatch('system/updateSummaryData', params);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || this.summaryData.summaryId ? '编辑奖项沉淀成功' : '新建奖项沉淀成功',
        });
        this.cancel();
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

    validate() {
      this.$refs.editFormRef.validate();
    },

    handleClose() {
      this.$emit('close', false);
    },
    // 选择奖项策略
    selectPolicy(v) {
      this.editFormList = this.policyList.find(e => e.id === v) && this.policyList.find(e => e.id === v).summary_info;
      this.setFormDetail(this.summaryDetail);
    },
  },
};
</script>
<style lang="postcss" scoped>
.edit {
  .policy_form {
    padding: 0px 30px;
  }
}

.btn-wrapper {
  text-align: center;

  .btn-font {
    font-weight: 700;
  }
}
</style>
