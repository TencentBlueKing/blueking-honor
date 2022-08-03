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
  <div>
    <div class="award-edit">
      <bk-form :label-width="150" :model="formData" :rules="rules" ref="formRef">
        <bk-form-item
          v-if="!obj.hidden"
          v-for="obj in formList"
          :label="obj.label"
          :key="obj.key"
          :required="obj.required"
          :desc="obj.desc"
          :rules="obj.rules"
          :property="obj.key">
          <quill-editor v-if="obj.key === 'description'" v-model="formData[obj.key]" @change="onEditorChange($event)" />
          <award-upload
            v-else-if="obj.type === 'award-upload'"
            :theme="obj.theme"
            :file="formData[obj.key] || []"
            v-model="formData[obj.key]"
          ></award-upload>
          <component
            v-else
            :is="obj.type"
            :theme="obj.theme"
            :placeholder="obj.placeholder"
            :type="obj.componentType"
            v-model="formData[obj.key]"
            @change="selectChange(...arguments, obj.key, formData[obj.key], obj.optionData)">
            <template v-if="obj.type === 'bk-radio-group'">
              <bk-radio style="padding-left: 10px"
                        v-for="item in obj.data"
                        :key="item.value"
                        :value="item.value">{{item.label}}</bk-radio>
            </template>
            <template v-if="obj.type === 'bk-select'">
              <bk-option v-for="option in obj.optionData"
                         :key="option.value"
                         :id="option.value"
                         :name="option.label">
              </bk-option>
            </template>
          </component>
        </bk-form-item>
      </bk-form>
    </div>
    <slot>
      <bk-form>
        <bk-form-item class="footer-btn">
          <bk-button theme="primary" title="确定" @click.stop.prevent="validate" :loading="isChecking">确定</bk-button>
          <bk-button ext-cls="mr5" theme="default" title="取消" @click.stop.prevent="cancel">取消</bk-button>
        </bk-form-item>
      </bk-form>
    </slot>
  </div>
</template>

<script>
import moment from 'moment';
import { quillEditor } from 'vue-quill-editor';

// import _ from 'lodash';
import 'quill/dist/quill.core.css';
import 'quill/dist/quill.snow.css';
import 'quill/dist/quill.bubble.css';
import AwardUpload from '@/components/award-upload';
export default {
  components: {
    AwardUpload,
    quillEditor,
  },
  props: {
    formList: {
      type: Array,
      default() {
        return [];
      },
    },
  },
  data() {
    return {
      isChecking: false,
      formData: {},
      rules: {},
    };
  },
  watch: {
    formList: {
      handler(value) {
        // _.throttle(() => {
        value.forEach((item) => {
          this.$set(this.formData, item.key, item.default);
          if (item.key === 'daterange-picker') {
            const startedAt = moment(item.default[0]).format('YYYY-MM-DD');
            const endedAt = moment(item.default[1]).format('YYYY-MM-DD');
            // eslint-disable-next-line prefer-destructuring
            this.formData.started_at = new Date(`${startedAt} 00:00:00 GMT`);
            // eslint-disable-next-line prefer-destructuring
            this.formData.ended_at = new Date(`${endedAt} 23:59:59 GMT`);
          }
          if (item.rules) {
            this.$set(this.rules, item.key, item.rules);
          }
        });
        // }, 100);
      },
      immediate: true,
      deep: true,
    },
  },
  created() {

  },
  methods: {
    validate() {
      this.isChecking = true;
      this.$refs.formRef.validate().then(() => {
        this.isChecking = false;
        delete this.formData['daterange-picker'];
        this.$emit('submit', this.formData);
      }, () => {
        this.isChecking = false;
      });
    },

    selectChange(data, date, key, value, optionData) {
      if (key === 'policy') {
        const policyData = optionData.filter(v => v.value === value);
        this.$emit('changeOptionData', policyData);
        this.$emit('changeFormData', value, this.formData);
      } else if (key === 'daterange-picker') {
        // eslint-disable-next-line prefer-destructuring
        this.formData.started_at = new Date(`${data[0]} 00:00:00 GMT`);
        // eslint-disable-next-line prefer-destructuring
        this.formData.ended_at = new Date(`${data[1]} 23:59:59 GMT`);
      }
    },

    cancel() {
      this.$refs.formRef.clearError();
      this.$router.back(-1);
    },

    // 保存草稿
    saveDraft() {
      Object.keys(this.formData).forEach((key) => {
        if (key === 'daterange-picker') {
          // eslint-disable-next-line prefer-destructuring
          this.formData.started_at = this.formData[key][0];
          // eslint-disable-next-line prefer-destructuring
          this.formData.ended_at = this.formData[key][1];
        }
      });
      this.$emit('saveDraft', this.formData);
    },

    // 富文本编辑
    onEditorChange(e) {
      this.$set(this.formData, 'description', e.html);
    },
  },
};
</script>

<style lang="postcss" scoped>

.award-edit {
  padding: 20px 30px;
}

.view-form {
  font-size: 14px;
  color: #63656e
}

.footer-btn {
  padding-right: 150px;
  margin: 20px auto;
  text-align: center;
}

</style>
