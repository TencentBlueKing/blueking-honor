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
  <div class="time-container" v-bkloading="{ isLoading: loading }">
    <div class="content">
      <div class="title">奖项信息</div>
      <div class="info">
        <div class="mt10">
          <span class="label">奖项名</span>
          <b>{{awardInfo && awardInfo.award.name}}</b>
        </div>

        <div class="mt10">
          <span class="label">级别</span>
          <b>{{LEVEL_ENUM[awardInfo && awardInfo.award.policy.level]}}</b>
        </div>

        <div class="mt10">
          <span class="label">审批环节</span>
          <b>评委反馈复审时间</b>
        </div>
      </div>

      <div class="product-list">
        <div class="title">申报信息</div>
        <div class="product-item" v-for="item in applyDetailList" :key="item.id">
          <div class="item-info">
            <div class="mt10">
              <span class="label">申报项目名称</span>
              <b>{{item.details.name}}</b>
            </div>

            <div class="mt10">
              <span class="label">申报部门</span>
              <b>{{item.details.declaration}}</b>
            </div>

            <div class="mt10">
              <span class="label">申报接口人</span>
              <b>{{item.liaisons.length ? item.liaisons.join(',') : '--'}}</b>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="btn-wrapper">
      <bk-button
        :theme="'primary'"
        class="mr10"
        :outline="true"
        @click="reviewTime">
        填写评审时间
      </bk-button>
    </div>

    <bk-dialog
      v-model="dialogVisible"
      theme="primary"
      width="600"
      ext-cls="award-time"
      :show-footer="false">
      <div class="time-container">
        <div class="title mb20">添加评审时间<span class="tips">最多可填写3条评审时间</span></div>
        <bk-form
          :label-width="150"
          :model="formData"
          form-type="inline"
          ext-cls="time-form">
          <bk-form-item
            :label="index === 0 ? '填写可用时间' : ''"
            :class="[index !== 0 ? 'item-margin' : '']"
            v-for="(item, index) in datePickerData" :key="index">
            <bk-date-picker
              v-model="formData[item]"
              :placeholder="'选择日期时间范围'"
              :type="'datetimerange'"
              :options="{ disabledDate: disabledDateTime }"
              @change="handleDateChange(...arguments, item)">
            </bk-date-picker>
          </bk-form-item>
        </bk-form>
        <div class="time-btn-wrapper mt20">
          <bk-button
            theme="primary"
            class="mr10"
            @click="sentTime">
            确认可用时间
          </bk-button>
          <bk-button
            theme="default"
            class="mr10"
            @click="dialogVisible = false">
            取消
          </bk-button>
        </div>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
import { mapGetters } from 'vuex';

import { LEVEL_ENUM } from '@/common/constants';
export default {
  components: {
  },
  data() {
    return {
      loading: true,
      dialogVisible: false,
      formData: {
        firstTime: [],
        nextTime: [],
        thirdTime: [],
      },
      datePickerData: ['firstTime', 'nextTime', 'thirdTime'],
      params: {},
      applyDetailList: [],
      awardInfo: {
        name: '--',
        award: {
          policy: {},
        },
      },
      LEVEL_ENUM,
    };
  },
  computed: {
    ...mapGetters(['user']),
  },
  mounted() {
    this.id = this.$route.query.id;
    if (this.id) {
      this.fetchDetail();
    }
  },
  methods: {
    // 详情
    async fetchDetail() {
      try {
        const res = await this.$store.dispatch('system/getApprovalAwardsDetail', this.id);
        this.applyDetailList = res.results || [];
        // eslint-disable-next-line prefer-destructuring
        this.awardInfo = res.results[0];
        this.loading = false;
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
    reviewTime() {
      if (window.localStorage.getItem('time')) {
        this.formData = JSON.parse(window.localStorage.getItem('time'));
      }
      this.dialogVisible = true;
    },

    // 确认可用时间
    async sentTime() {
      const time = Object.keys(this.formData).reduce((prev, key) => {
        if (this.formData[key][0]) {
          prev.push({
            started_at: new Date(this.formData[key][0]).getTime() / 1000,
            ended_at: new Date(this.formData[key][1]).getTime() / 1000,
          });
        }
        return prev;
      }, []);
      this.params = {
        data: {
          available_periods: time,
        },
        id: this.id,
      };
      try {
        await this.$store.dispatch('user/postAvaiFeedTime', this.params);
        this.dialogVisible = false;
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: '添加评审时间成功',
        });
        window.localStorage.setItem('time', JSON.stringify(this.formData));
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
        this.formData = {
          firstTime: '',
          nextTime: '',
        };
      }
    },

    handleDateChange(data, date, item) {
      this.formData[item] = data;
    },

    disabledDateTime(time) {
      const tiemVal = new Date(time);
      if (tiemVal <= new Date().getTime() - 24 * 60 * 60 * 1000) {
        return true;
      }
      return false;
    },
  },
};
</script>
<style lang="postcss" scoped>
.time-container {
  .content {
    width: 50%;
    height: calc(100vh - 305px);
    min-height: 500px;
    padding-top: 30px;
    margin: 0 auto;
    overflow: auto;
    font-size: 14px;
    color: #646464;

    .title {
      margin-bottom: 20px;
      font-size: 18px;
      font-weight: bold;
    }

    .info {
      padding-bottom: 20px;
      margin-bottom: 50px;
      border-bottom: 1px solid #ccc;

      .label {
        display: inline-block;
        width: 100px;
      }
    }

    .product-list {
      .product-item {
        margin-top: 10px;

        .item-info {
          padding-bottom: 20px;
          border-bottom: 1px solid #ccc;
        }

        .product-name {
          font-size: 18px;
          font-weight: bold;
        }

        .product-desc {
          font-size: 14px;
        }

        .label {
          display: inline-block;
          width: 100px;
        }
      }
    }
  }

  .btn-wrapper {
    margin: 7px auto 0;
    text-align: center;

    .btn-font {
      font-weight: 700;
    }
  }
}

.award-time .time-container {
  .title {
    display: flex;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    align-items: center;
    justify-content: center;

    .tips {
      padding-left: 10px;
      font-size: 12px;
      color: #ccc;
    }
  }

  .item-margin {
    margin: 20px 0px 0 98px;
  }

  .time-btn-wrapper {
    text-align: center;
  }
}
</style>
