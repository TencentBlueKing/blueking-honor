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
    <div class="main" v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }">
      <div class="detail">
        <left-detail v-if="id" :detail-list="formList"></left-detail>
        <div class="empty" v-else>暂无奖项信息</div>
      </div>
      <div class="edit">
        <bk-form class="policy_form" :label-width="150">
          <bk-form-item label="奖项策略" :required="true" v-if="!isAward">
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
          @saveDraft="saveDraft"
          :form-list="editFormList">
          <div></div>
        </edit-form>
      </div>
    </div>
    <div class="btn-wrapper">
      <bk-button :theme="'primary'" class="mr10" @click="validate">
        提 交
      </bk-button>
      <bk-button
        :theme="'default'"
        type="submit"
        :title="'基础按钮'"
        class="mr10"
        @click="noticSaveDraft">
        保存草稿
      </bk-button>
      <bk-button :theme="'default'" @click="cancel" :title="'基础按钮'" class="mr10" style="padding: 0 30px;">
        取 消
      </bk-button>
    </div>
  </div>
</template>

<script>
import moment from 'moment';
import { mapGetters } from 'vuex';

import { APPROVE_ENUM, LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
import editForm from '@/components/system/edit-form.vue';
import LeftDetail from '@/components/user/left-detail.vue';
export default {
  components: {
    LeftDetail,
    editForm,
  },
  data() {
    return {
      reviewInfo: {
        status: 'approve',
        comment: '',
      },
      formList: [
        {
          key: 'name',
          label: '奖项名称',
          default: '',
        },
        {
          key: 'level',
          label: '级别',
          default: '',
        },
        {
          key: 'description',
          label: '奖项描述',
          default: '',
        },
        {
          key: 'liaisons',
          label: '知会人员',
          default: [],
        },
        {
          key: 'daterange-picker',
          label: '项目起止时间',
          default: [],
        },
        {
          key: 'status',
          label: '状态',
          default: 'pending',
        },
      ],
      policyId: '',
      editFormList: [
      ],
      params: {},
      APPROVE_ENUM,
      formLoading: false,
      awardId: '',
      id: '',
      summaryId: '',
      policyList: [],
      year: '',
      summaryDetail: [],
    };
  },
  computed: {
    ...mapGetters(['user']),
    isAward() {
      return this.$route.query.isAward || [];
    },
  },
  async mounted() {
    this.id = this.$route.query.id;
    this.summaryId = this.$route.query.summaryId;
    if (this.summaryId) {
      this.$route.meta.name = '编辑奖项沉淀';
    } else {
      this.$route.meta.name = '填写奖项沉淀';
    }
    if (window.localStorage.getItem(`${this.id}prome`)) {
      const storageData = JSON.parse(window.localStorage.getItem(`${this.id}prome`));
      this.setStorageData(storageData);
    }
    await this.fetchData();
    if (this.id) {
      this.fetchApplyDetail();
    }
    if (this.summaryId) {
      this.fetchSummaryDetail();
    }
  },
  methods: {
    // 详情
    async fetchApplyDetail() {
      try {
        const res = await this.$store.dispatch('user/getApplyDetail', this.id);
        this.setLeftData(res);
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

    // 获取策略
    async fetchData() {
      const params = {
        page_size: 1000,
      };
      try {
        const res = await this.$store.dispatch('system/getPoliciesList', params);
        this.policyList = res.results;
        this.policyId = res.results[0].id;
        this.editFormList = this.policyList.find(e => e.id === this.policyId).summary_info;
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
    setLeftData(data) {
      this.awardId = data.award.id;
      this.formList.forEach((e) => {
        e.default = data.award[e.key];
        if (e.key === 'status') {
          e.default = STATUS_ENUM[data[e.key]];
        } else if (e.key === 'daterange-picker') {
          e.default = `${moment(data.award.started_at * 1000).format('YYYY-MM-DD')} 至 ${moment(data.award.ended_at * 1000).format('YYYY-MM-DD')}`;
        } else if (e.key === 'liaisons') {
          e.default = data[e.key].join(',');
        } else if (e.key === 'level') {
          e.default = LEVEL_ENUM[data.award.policy.level];
        }
        this.formLoading = false;
      });
    },

    // 详情
    async fetchSummaryDetail() {
      this.formLoading = true;
      try {
        const res = await this.$store.dispatch('system/getSummaryDetail', this.summaryId);
        this.policyId = res.policy_id;
        this.year = moment(Date.parse(res.year)).format();
        this.summaryDetail = res.details || [];
        this.setFormDetail(res.details);
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
      this.editFormList.forEach((e) => {
        e.default = data[e.key];
        if (e.key === 'award_id') {
          e.default = data.award.id;
        }
        this.formLoading = false;
      });
    },

    async validate() {
      this.$refs.editFormRef.validate();
    },

    // 新增奖项沉淀
    async submit(value) {
      const year = this.year ? moment(this.year).format('YYYY') : '';
      let fetchUrl = 'system/addSummaryData';
      if (this.summaryId) {
        fetchUrl = 'system/updateSummaryData';
        value.id = this.summaryId;
      }
      const params = {
        details: value,
        year,
        policy_id: this.policyId,
      };
      if (this.id) {
        params.award_id = this.awardId;
        params.application_id = this.id;
      }
      try {
        const res = await this.$store.dispatch(fetchUrl, params);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || this.summaryId ? '编辑奖项沉淀成功' : '新建奖项沉淀成功',
        });
        this.cleanDraft();
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
    cancel() {
      this.$router.back(-1);
    },

    // 出发子组件保存方法
    noticSaveDraft() {
      this.$refs.editFormRef.saveDraft();
    },

    // 保存草稿
    saveDraft(value) {
      window.localStorage.setItem(`${this.id}prome`, JSON.stringify(value));
      this.$bkMessage({ theme: 'success', message: '保存草稿成功' });
    },

    // 清除草稿
    cleanDraft() {
      localStorage.removeItem(`${this.id}prome`);
    },

    // 沉淀设置缓存数据
    setStorageData(data) {
      this.editFormList.forEach((e) => {
        e.default = data[e.key];
      });
    },

    // 选择奖项策略
    selectPolicy(v) {
      this.editFormList = this.policyList.find(e => e.id === v).summary_info;
      this.setFormDetail(this.summaryDetail);
    },
  },
};
</script>

<style lang="postcss" scoped>

.main {
  display: flex;
  height: calc(100vh - 320px);
  padding: 10px 20px;
  overflow: auto;
  font-size: 14px;
  line-height: 2em;
  color: #646464;
  justify-content: space-between;

  .detail {
    width: 590px;
    word-wrap: break-word;

    .empty {
      text-align: center;
    }
  }

  .edit {
    flex: 1;
    border-left: 1px solid #ccc;

    .policy_form {
      padding: 0px 30px;
    }
  }

}

.btn-wrapper {
  text-align: center;

  .btn-font {
    font-weight: 700;
  }
}
</style>
