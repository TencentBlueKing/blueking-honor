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
  <div class="apply" v-bkloading="{ isLoading }">
    <div class="apply-left">
      <div class="apply-title">奖项指引</div>
      <div class="apply-content">
        <div class="content-item"><b>奖项名：</b>{{award.name}}</div>
        <div class="content-item"><b>级别：</b>{{LEVEL_ENUM[award.policy.level]}}</div>
        <div class="content-item"><b>详细标准：</b><span v-html="award.description"></span></div>
        <div class="content-item"><b>接口人：</b>{{award.liaisons.join(';')}}</div>
        <div class="content-item"><b>附件：</b>
          <a class="mr10" v-for="item in award.addons" :key="item" :href="item.url || item">
            <bk-button>点击下载附件</bk-button>
          </a>
        </div>
        <div class="content-item"><b>开始日期：</b>{{award.started_at | formatDate('date')}}</div>
        <div class="content-item"><b>截止日期：</b>{{award.ended_at | formatDate('date')}}</div>
      </div>
    </div>
    <div class="apply-right">
      <div class="apply-title">奖项申报</div>
      <div class="apply-content">
        <bk-form :label-width="165" :model="formData" :rules="rules" ref="manageForm">

          <template v-for="obj in dataJson">
            <bk-form-item
              :key="obj.key"
              :property="obj.key"
              v-bind="obj">
              <component
                :is="obj.type"
                :type="obj.componentType"
                :file="formData[obj.key] || []"
                v-bind="obj"
                v-model="formData[obj.key]"></component>
            </bk-form-item>
          </template>

          <bk-form-item>
            <bk-button theme="primary" class="mr10" title="我要申报" @click.stop.prevent="validate" :loading="isChecking">
              我要申报
            </bk-button>
            <bk-button theme="default" class="mr10" title="保存草稿" @click.stop.prevent="saveDraft" :loading="isChecking">
              保存草稿
            </bk-button>
            <bk-button ext-cls="mr5" theme="default" title="取消" @click="$router.go(-1)">
              取消
            </bk-button>
          </bk-form-item>
        </bk-form>
      </div>
    </div>
  </div>
</template>

<script>
import AwardSelect from './../../components/award-select';
import AwardUpload from './../../components/award-upload';

import { LEVEL_ENUM } from '@/common/constants';

export default {
  name: 'Apply',
  components: {
    AwardUpload,
    AwardSelect,
  },
  data() {
    return {
      id: this.$route.query.id,
      LEVEL_ENUM,
      award: {
        liaisons: [],
        policy: {},
      },
      dataJson: [],
      isChecking: false,
      formData: {},
      rules: {},
      isLoading: true,
    };
  },
  async created() {
    const { id } = this;
    const award = await this.$store.dispatch('award/getAward', { id });
    this.isLoading = false;
    this.award = award;
    this.dataJson = award.policy.raw_application_info.fields;
    const localData = JSON.parse(window.localStorage.getItem(id) || '{}');
    this.dataJson.forEach((item) => {
      this.$set(this.formData, item.key, localData[item.key] || item.default);
      if (item.rules) {
        this.$set(this.rules, item.key, item.rules);
      }
      if (item.required) {
        const requiredRules = {
          required: true,
          trigger: 'blur',
        };
        if (!this.rules[item.key]) {
          this.rules[item.key] = [requiredRules];
        } else {
          this.rules[item.key].push(requiredRules);
        }
      }
    });
  },
  methods: {
    validate() {
      this.isChecking = true;
      // 页面输入框防止 XSS攻击
      this.formData.description = this.$xss(this.formData.description);
      this.$refs.manageForm.validate().then(() => {
        this.isChecking = false;
        const { id } = this;
        const { applicants, liaisons, staffs } = this.formData;
        this.$store.dispatch('award/apply', { id, applicants, liaisons, staffs, details: this.formData }).then(() => {
          this.$bkMessage({ theme: 'success', message: '申报成功' });
          this.$router.push({ name: 'my-apply' });
        });
      }, (validator) => {
        this.isChecking = false;
      });
    },
    saveDraft() {
      const { id } = this;
      window.localStorage.setItem(id, JSON.stringify(this.formData));
      this.$bkMessage({ theme: 'success', message: '保存草稿成功' });
    },
  },

};
</script>

<style lang="postcss" scoped>
.apply {
  display: flex;
  width: 100%;
  margin: 55px auto;
  justify-content: center;
}

.apply-left,
.apply-right {
  background: #fff;
  border-radius: 10px;

  .apply-title {
    height: 65px;
    padding: 20px 30px;
    font-size: 16px;
    font-weight: bold;
    border-bottom: 1px solid #dcdee5;
  }

  .apply-content {
    height: calc(100vh - 290px);
    min-height: 500px;
    padding: 20px 30px;
    overflow: auto;
    font-size: 14px;
    color: #63656e;

    .content-item {
      line-height: 32px;
    }
  }
}

.apply-left {
  width: 42%;
  margin-right: 45px;
}

.apply-right {
  width: 48%;
}

.form-group {
  border-bottom: 1px solid #dcdee5;

  >>>.bk-label-text {
    font-size: 16px;
    font-weight: bold;
  }
}

.form-title {
  >>>.bk-label-text {
    font-weight: bold;
  }
}

</style>
