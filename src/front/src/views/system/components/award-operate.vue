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
  <div class="award-operate">
    <edit-form v-if="type === 'edit'"
               class="award-detail"
               v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }"
               :form-list="formList"
               @submit="submit"
               @changeFormData="changeFormData"
               @changeOptionData="changeOptionData"></edit-form>

    <left-detail
      class="award-detail"
      v-else
      v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }"
      :detail-list="formList"></left-detail>
  </div>
</template>
<script>
import moment from 'moment';

import { LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
import editForm from '@/components/system/edit-form.vue';
import leftDetail from '@/components/user/left-detail.vue';
// import _ from 'lodash';
const periodsDatas = [
  { label: '1', value: 1 },
  { label: '2', value: 2 },
  { label: '3', value: 3 },
  { label: '4', value: 4 },
];

export default {
  components: {
    editForm,
    leftDetail,
  },
  data() {
    return {
      policyList: [],
      type: '',
      formData: {},
      id: '',
      formLoading: true,
      formList: [
        {
          key: 'name',
          label: '奖项名称',
          type: 'bk-input',
          default: '',
          placeholder: '请输入奖项名称',
          required: true,
          rules: [
            {
              max: 100,
              message: '不能多于100个字符',
              trigger: 'blur',
            },
            { required: true,
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
          rules: [
            { required: true,
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'quarter',
          label: '奖项周期',
          type: 'bk-select',
          default: '',
          placeholder: '请填写奖项周期（1 2 3 4）',
          required: true,
          readonly: true,
          optionData: periodsDatas.slice(0, 1),
          rules: [
            { required: true,
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'addons',
          label: '附件',
          type: 'award-upload',
          default: [],
        },
        {
          key: 'liaisons',
          label: '知会人员',
          type: 'bk-tag-input',
          'allow-create': true,
          default: [],
          required: true,
          rules: [
            { required: true,
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'policy',
          label: '奖项策略',
          type: 'bk-select',
          default: '',
          placeholder: '请选择奖项策略',
          required: true,
          optionData: this.policyList,
          rules: [
            { required: true,
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'daterange-picker',
          label: '项目起止时间',
          type: 'bk-date-picker',
          default: [],
          placeholder: '选择日期范围',
          componentType: 'daterange',
          required: true,
          rules: [
            { required: true,
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'status',
          label: '状态',
          type: 'bk-radio-group',
          default: 'pending',
          required: true,
          data: [{ value: 'pending', label: '未开始' }, { value: 'started', label: '可申报' }, { value: 'unapplicable', label: '不可申报' }, { value: 'expired', label: '已过期' }],
          rules: [
            { required: true,
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'award_slideshow',
          label: '奖项图',
          theme: 'picture',
          type: 'award-upload',
          default: [],
        },
      ],
      detailData: {
        'daterange-picker': [],
      },
      awardDetail: {
        name: '',
      },
      dynamicAdmin: [],
      policyValue: '',
      periodsList: [],
      periodsData: [],
    };
  },
  computed: {
  },
  watch: {
  },
  async mounted() {
    // this.formListBackUp = _.cloneDeep(this.formList);   // 备份数据
    this.type = this.$route.query.type;
    this.id = this.$route.query.id;
    await this.fetchData();
    if (this.id) {
      this.fetchAwardDetail();
    }
    if (this.type === 'edit') {
      if (this.id) {
        this.$route.meta.name = '编辑奖项信息';
      } else {
        this.$route.meta.name = '新增奖项信息';
      }
    } else {
      this.$route.meta.name = '查看奖项信息';
    }
  },
  methods: {
    async fetchData() {
      const params = {
        page_size: 1000,
      };
      try {
        const res = await this.$store.dispatch('system/getPoliciesList', params);
        this.policyList = (res.results || []).map(e => ({
          value: e.id,
          label: e.name,
          user_groups: e.get_user_groups_from_steps,
          periods: e.periods,
        }));
        this.setPolicy();
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

    changeOptionData(target) {
      this.periodsList = target[0].periods;
      this.periodsData = periodsDatas.slice(0, this.periodsList.length === 0 ? 1 : this.periodsList.length);
      this.formList.forEach((item) => {
        if (item.key === 'quarter') {
          item.optionData = this.periodsData;
        }
      });
    },

    // 提交
    async submit(value) {
      const fetchUrl = this.id ? 'system/updateAwardsData' : 'system/addAwardsData';
      if (this.id) {
        value.id = this.id;
      }
      const userGroups = {};
      value = Object.keys(value).reduce((p, v) => {
        if (this.dynamicAdmin.includes(v)) {
          userGroups[v] = value[v];
        } else {
          p[v] = value[v];
        }
        return p;
      }, {});
      value.user_groups = userGroups;
      try {
        const res = await this.$store.dispatch(fetchUrl, value);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '操作成功',
        });
        this.$router.back(-1);
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
    async fetchAwardDetail() {
      this.formLoading = true;
      try {
        this.awardDetail =  await this.$store.dispatch('system/getAwardDetail', this.id);
        if (this.type === 'view') {
          const addData = this.policyList.find(e => e.value === this.awardDetail.policy.id).user_groups;
          this.dynamicAdmin = (addData || []).map(e => e.id);
          this.setUserGroup(addData);
        }
        this.setFormDetail(this.awardDetail);
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

    // 设置setPolicy
    setPolicy() {
      this.formList.forEach((e) => {
        if (e.key === 'policy') {
          e.optionData = this.policyList;
          if (!this.id) {
            e.default = this.policyList[0].value;
          }
        }
      });
    },

    // 设置default值
    setFormDetail(data) {
      this.formList.forEach((e) => {
        e.default = data[e.key];
        if (e.key === 'policy') {
          e.default = this.type === 'view' ? data[e.key].name : this.policyValue || data[e.key].id;
        } else if (e.key === 'status') {
          e.default = this.type === 'view' ? STATUS_ENUM[data[e.key]] : (data[e.key] || 'pending');
        } else if (e.key === 'daterange-picker') {
          // eslint-disable-next-line no-nested-ternary
          e.default = this.type === 'view' ? `${moment(data.started_at * 1000).format('YYYY-MM-DD')} 至 ${moment(data.ended_at * 1000).format('YYYY-MM-DD')}`
            : (data.started_at ? [moment(data.started_at * 1000), moment(data.ended_at * 1000)]
              : [moment(new Date().getTime()), moment(new Date().getTime())]);
        } else if (e.key === 'liaisons') {
          e.default = this.type === 'view' ? data[e.key] && data[e.key].join(',') : data[e.key];
        } else if (e.key === 'level') {
          e.default = data.policy ? LEVEL_ENUM[data.policy.level] : '';
        } else if (e.key === 'addons') {
          let url;
          if (data[e.key] && data[e.key][0] && data[e.key][0].url) {
            url = [data[e.key][0].url];
          } else if (data[e.key] && data[e.key][0] && !data[e.key][0].url) {
            url = [data[e.key][0]];
          } else {
            url = [];
          }
          e.default = this.type === 'view' ? url.join(',') : url ;
        } else if (e.key === 'award_slideshow' && this.type === 'view') {
          e.default = data[e.key][0]?.url;
        } else if (this.dynamicAdmin.includes(e.key)) {
          if (data.user_groups) {
            e.default = this.type === 'view' ? data.user_groups[e.key] && data.user_groups[e.key].join(',') : data.user_groups[e.key];
          } else {
            e.default = this.type === 'view' ? '' : [];
          }
        }
        this.formLoading = false;
      });
    },

    // 设置用户组
    setUserGroup(data) {
      const group = (data || []).map(e => ({
        key: e.id,
        label: e.name,
        type: 'bk-tag-input',
        'allow-create': true,
        default: [],
        required: true,
        rules: [
          { required: true,
            trigger: 'blur',
          },
        ],
      }));
      this.formList.splice(7, 0, ...group);
    },

    // 修改策略
    changeFormData(value, data) {
      if (!this.policyList.length) return;
      this.policyValue = value;
      const deleteLength = this.formList.findIndex(e => e.key === 'daterange-picker') - 7;
      this.formList.splice(7, deleteLength);
      const addData = this.policyList.find(e => e.value === value).user_groups;
      this.dynamicAdmin = (addData || []).map(e => e.id);
      // 奖项策略之前的内容保持不变
      this.awardDetail.name = data.name;
      this.awardDetail.description = data.description;
      this.awardDetail.addons = data.addons;
      this.awardDetail.quarter = data.quarter;
      this.awardDetail.liaisons = data.liaisons;
      this.awardDetail.award_slideshow = data.award_slideshow;
      this.setUserGroup(addData);
      this.setFormDetail(this.awardDetail);
    },

  },
};
</script>
<style lang="postcss" scoped>
.award-operate {
  .award-detail {
    height: calc(100vh - 295px);
    overflow: auto;
  }
}
</style>
