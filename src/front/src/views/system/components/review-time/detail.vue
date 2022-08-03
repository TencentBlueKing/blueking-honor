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
        评审时间
      </bk-button>
    </div>

    <bk-dialog
      v-model="dialogVisible"
      theme="primary"
      width="900"
      ext-cls="award-time"
      :show-footer="false">
      <div class="time-container">
        <div class="title mb20">复审时间反馈</div>
        <div class="tiem-flex" v-if="usernamePeriods.length">
          <div class="time-left">
            <div class="left-title">{{awardInfo.award.name}}复审时间反馈</div>
            <div>评委共 {{usernamePeriods.length}} 人</div>
            <div class="user-list">
              <div class="user-item" v-for="(item, index) in usernamePeriods" :key="index">{{item.username}}</div>
            </div>
            <div class="time-duration">
              评审时长
              <bk-input class="time-input" type="text" v-model="timeDuration"></bk-input>
              分钟
            </div>
            <div class="time-period" v-if="intersectionPeriods.length">
              <div class="info">评审可用时间段</div>
              <bk-radio-group v-model="reviewTimeData.time">
                <bk-radio
                  v-for="(item, index) in intersectionPeriods"
                  :value="`${item.started_at}, ${item.ended_at}`"
                  :key="index"
                  class="time-radio">
                  {{item.started_at | formatDate}} - {{item.ended_at | formatDate}}
                </bk-radio>
              </bk-radio-group>
            </div>

            <div class="time-period" v-else>
              <div class="info">暂无可用时间段，你可以手动填写可用时间</div>
              <bk-date-picker
                v-model="initDateTimeRange"
                :placeholder="'选择日期时间范围'"
                :type="'datetimerange'"
                @change="handleDateChange">
              </bk-date-picker>
            </div>
          </div>
          <div class="time-right">
            <b class="right-title">成员</b>
            <div class="user-list">
              <div class="user-item" v-for="item in usernamePeriods" :key="item.username">
                <div class="user-info">
                  <div class="user-img">
                    <img :src="getAvatarUrl(item.username)" class="avatar">
                  </div>
                  <div class="user-name">{{item.username}}</div>
                </div>
                <div class="user-time">
                  <div class="time-item" v-for="(v, i) in item.available_periods"
                       :key="i">{{v.started_at | formatDate}} - {{v.ended_at | formatDate}}</div>
                </div>
              </div>

            </div>
          </div>
        </div>
        <div class="time-btn-wrapper mt20" v-if="usernamePeriods.length">
          <bk-button
            theme="primary"
            class="mr10"
            @click="sentTime">
            确认可用时间段
          </bk-button>
          <bk-button
            theme="default"
            class="mr10"
            @click="dialogVisible = false">
            取消
          </bk-button>
        </div>
        <div v-if="!usernamePeriods.length" style="text-align: center">暂无数据</div>
      </div>
    </bk-dialog>
  </div>
</template>
<script>
import moment from 'moment';
import { mapGetters } from 'vuex';

import { LEVEL_ENUM } from '@/common/constants';
export default {
  components: {
  },
  filters: {
    formatTime(value) {
      return moment(value * 1000).format('YYYY-MM-DD HH:mm:ss');
    },
  },
  data() {
    return {
      loading: true,
      dialogVisible: false,
      timeDuration: '120',
      reviewTimeData: {
        time: '',
      },
      initDateTimeRange: [new Date(), new Date()],
      usernamePeriods: [],
      intersectionPeriods: [],
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
  watch: {
    timeDuration() {
      this.reviewTime();
    },
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
    async reviewTime() {
      this.params = {
        id: this.id,
        last_minutes: this.timeDuration,
      };
      try {
        const res = await this.$store.dispatch('system/getAvailableList', this.params);
        this.usernamePeriods = res.username_periods;
        this.intersectionPeriods = res.intersection_periods;
        this.reviewTimeData.time = res.intersection_periods.length
          ? `${res.intersection_periods[0].started_at}, ${res.intersection_periods[0].ended_at}` : '';    // 默认取第一条
        this.dialogVisible = true;
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

    // 确认审批时间
    async sentTime() {
      const params = {
        data: {
          started_at: this.reviewTimeData.time && this.reviewTimeData.time.split(',')[0],
          ended_at: this.reviewTimeData.time && this.reviewTimeData.time.split(',')[1],
        },
        id: this.id,
      };
      try {
        await this.$store.dispatch('system/confirmApproTime', params);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: '确认评审时间成功',
        });
        this.dialogVisible = false;
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

    // 可用时间段
    handleDateChange(value) {
      this.reviewTimeData.time = `${new Date(value[0]).getTime() / 1000},${new Date(value[1]).getTime() / 1000}`;
    },
    getAvatarUrl(username) {
      return `${window.PROJECT_CONFIG.avatar_site}/${username}/avatar.jpg`;
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
    font-size: 18px;
    font-weight: bold;
    text-align: center;
  }

  .tiem-flex {
    display: flex;
    min-height: 325px;

    .time-left {
      width: 49%;

      .left-title {
        font-weight: bold;
        text-align: center;
      }

      .user-list {
        display: flex;
        width: 60%;
        padding: 5px 7px;
        margin-top: 20px;
        border: 1px solid #3a84ff;
        flex-flow: wrap;
        align-items: center;
        justify-content: space-between;

        .user-item {
          width: 100px;
          padding: 5px 10px;
          margin: 8px 0;
          text-align: center;
          background: #e7e7e7;
          border-radius: 3px;
        }
      }

      .time-duration {
        display: flex;
        margin: 20px 0;
        align-items: center;

        .time-input {
          width: 100px;
          margin: 0 20px;
        }
      }

      .time-period {
        .info {
          margin: 20px 0;
        }

        .time-radio {
          display: block;
          margin-bottom: 10px;
        }
      }
    }

    .time-right {
      padding-left: 20px;
      border-left: 1px dashed #ccc;
      flex: 1;

      .user-list {
        .user-item {
          display: flex;
          align-items: center;
          padding: 12px 0;
          border-bottom: 1px solid #ccc;

          .user-info {
            width: 80px;
            margin-right: 15px;
            text-align: center;

            .user-img {
              img {
                width: 50px;
                height: 50px;
                border-radius: 30px;
              }
            }

            .user-name {
              font-weight: bold;
            }
          }

          .user-time {
            .time-item {
              font-size: 13px;
            }
          }
        }
      }
    }
  }

  .time-btn-wrapper {
    text-align: center;
  }
}
</style>
