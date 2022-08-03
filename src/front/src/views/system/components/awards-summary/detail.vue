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
    <edit-form
      v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }"
      :form-list="formList" @submit="submit"></edit-form>

  </div>
</template>
<script>
import editForm from '@/components/system/edit-form.vue';
export default {
  components: {
    editForm,
  },
  data() {
    return {
      policyList: [],
      type: '',
      formData: {},
      id: '',
      formLoading: false,
      formList: [
        {
          key: 'award_id',
          label: '奖项类别',
          type: 'bk-select',
          default: '',
          placeholder: '请选择奖项类别',
          optionData: this.$store.state.system.awardsList,
          required: true,
        },
        {
          key: 'material_title',
          label: '材料标题',
          type: 'bk-input',
          default: '',
          required: true,
          placeholder: '请输入材料标题',
          rules: [
            {
              max: 20,
              message: '不能多于20个字符',
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'winning_team_name',
          label: '获奖团队名称',
          type: 'bk-input',
          default: '',
          required: true,
          placeholder: '请输入获奖团队名称',
          rules: [
            {
              max: 20,
              message: '不能多于20个字符',
              trigger: 'blur',
            },
          ],
        },
        {
          key: 'deeds_introduction',
          label: '事迹介绍',
          type: 'bk-input',
          default: '',
          required: true,
          placeholder: '请输入2000字以内事迹介绍',
          componentType: 'textarea',
        },
        {
          key: 'team_members',
          label: '团队成员名单',
          type: 'bk-tag-input',
          'allow-create': true,
          default: [],
          required: true,
        },
        {
          key: 'funding_sys_name',
          label: '部门经费系统',
          type: 'bk-input',
          default: '',
          required: true,
          placeholder: '可咨询部门秘书',
          rules: [
            {
              max: 20,
              message: '不能多于20个字符',
              trigger: 'blur',
            },
          ],
        },
      ],
      detailData: {
        'daterange-picker': [],
      },
    };
  },
  computed: {
  },
  mounted() {
    this.id = this.$route.query.id;
    if (this.id) {
      this.fetchSummaryDetail();
    }
  },
  methods: {
    // 提交
    async submit(value) {
      let fetchUrl = 'system/addSummaryData';
      if (this.id) {
        fetchUrl = 'system/updateSummaryData';
        value.id = this.id;
      }
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
    async fetchSummaryDetail() {
      this.formLoading = true;
      try {
        const res = await this.$store.dispatch('system/getSummaryDetail', this.id);
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
      } finally {
        this.formLoading = false;
      }
    },

    // 设置default值
    setFormDetail(data) {
      this.formList.forEach((e) => {
        e.default = data[e.key];
        if (e.key === 'award_id') {
          e.default = data.award.id;
        }
        this.formLoading = false;
      });
    },
  },
};
</script>
<style lang="postcss" scoped>
  .award-operate {
    height: calc(100vh - 343px);
    padding: 20px 30px;
    overflow: auto;
  }
</style>
