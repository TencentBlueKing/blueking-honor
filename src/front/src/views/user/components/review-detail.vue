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
  <div class="detail-content">
    <div class="main" v-bkloading="{ isLoading: formLoading, opacity: 1, zIndex: 1000 }">
      <div class="detail">
        <left-detail :detail-list="formList"></left-detail>
      </div>
      <div class="content">
        <left-detail :detail-list="detailFormList"></left-detail>
        <div v-if="finishData.length">
          <p class="mt20">
            <span class="label-right">前置环节意见：</span>
          </p>
          <div class="prev-container" v-for="item in finishData" :key="item.id">
            <b class="left">{{item.name}}</b>
            <div class="right">
              <div class="status" :class="item.status === 'aborted' ? 'aborted' : 'approved'">
                {{item.type === 'notification' ? '已通知' : (APPROVE_ENUM[item.status] || '通过')}}
              </div>
              <div class="comment">
                {{item.details.comment || '暂无评语'}}
              </div>
            </div>
          </div>
        </div>
        <p class="mt20" v-if="startedData.name">
          <span class="label-right">当前审批环节:</span>
          <b>{{startedData.name}}</b>
        </p>
        <p class="mt20" v-if="startedData.details &&
          startedData.details.approvers &&
          startedData.details.approvers.length">
          <span class="label-right">当前审批人:</span>
          <b>{{startedData.details.approvers.join(',')}}</b>
        </p>
        <p class="mt20" v-if="pendingData[0] && !isAborted">
          <span class="label-right">下一环节:</span>
          <b>{{pendingData[0].name}}</b>
        </p>

        <!-- 通知操作-->
        <div v-if="reviewInfo.type === 'notification' && (startedData.details && !startedData.details.sent)">
          <div class="review-comments mt20">
            <span class="label-right">接收人:</span>
            <bk-tag-input allow-create v-model="reviewInfo.forceReceivers" style="width: 420px;"></bk-tag-input>
          </div>
          <div class="review-comments mt20">
            <span class="label-right">内容:</span>
            <bk-input
              style="width: 420px;"
              type="textarea"
              v-model="reviewInfo.forceMessage"
              placeholder="请输入内容"></bk-input>
          </div>
        </div>

        <!-- 审批操作-->
        <div class="review-operate" v-else-if="reviewInfo.type === 'approval'">
          <div class="review-comments mt20">
            <p class="label-right radio-comments">评审意见:</p>
            <bk-radio-group v-model="reviewInfo.status">
              <bk-radio :value="'approve'" style="margin-right: 10px;">
                {{startedData.is_final_approval ? '切换为“已获奖”状态' : '通过'}}
              </bk-radio>
              <bk-radio :value="'reject'">{{startedData.is_final_approval ? '切换为“未获奖”状态' : '驳回'}}</bk-radio>
            </bk-radio-group>
          </div>
          <div class="review-comments mt20">
            <p class="label-right radio-comments">评语:</p>
            <bk-input type="textarea" v-model="reviewInfo.comment" placeholder="此处填写具体评语"></bk-input>
          </div>
        </div>

        <!-- BG复审-->
        <div class="review-operate mt20" v-else-if="reviewInfo.type === 'extra_info_collection'">
          <bk-form :label-width="150" :model="formData" :rules="rules" ref="formRef">
            <bk-form-item
              v-for="obj in editFormList"
              :label="obj.label"
              :key="obj.key"
              :required="obj.required"
              :desc="obj.desc"
              :rules="obj.rules"
              :property="obj.key">
              <quill-editor v-if="obj.key === 'description'" v-model="formData[obj.key]" />
              <award-upload
                v-else-if="obj.key === 'upload'"
                :theme="obj.theme"
                :file="formData[obj.key]"
                v-model="formData[obj.key]"
              ></award-upload>
              <component
                v-else
                :is="obj.type"
                :theme="obj.theme"
                :placeholder="obj.placeholder"
                :type="obj.componentType"
                v-model="formData[obj.key]">
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
      </div>
    </div>
    <div class="border"></div>
    <div class="btn-wrapper" v-if="!isAborted">
      <!-- 反馈复审时间 -->
      <bk-button
        v-if="reviewInfo.type === 'approval_time_collection'"
        :theme="'primary'"
        class="mr10"
        :outline="true"
        @click="toReviewTime(startedData)">
        反馈复审时间
      </bk-button>
      <bk-button
        v-if="reviewInfo.type === 'notification' && (startedData.details && !startedData.details.sent)"
        :theme="'primary'" class="mr10" @click="submit">
        发送通知
      </bk-button>
      <bk-button
        v-if="reviewInfo.type === 'approval'
          || reviewInfo.type === 'extra_info_collection'"
        :theme="'primary'"
        class="mr10" @click="submit">
        提交
      </bk-button>
      <bk-button
        :theme="'primary'"
        class="mr10"
        :outline="true"
        @click="toSummaryPage(summaryInfo.summary_id)"
        v-if="summaryInfo.is_summary_filled">
        查看/编辑奖项沉淀
      </bk-button>
      <bk-button
        :theme="'primary'"
        class="mr10"
        :outline="true"
        @click="next"
        v-if="!autoExecute && showNextBtn && !isLast">
        下一步
      </bk-button>
      <bk-button
        :theme="'default'"
        type="submit"
        :title="'基础按钮'"
        class="mr10"
        v-if="(startedData.details && !startedData.details.sent)
          && startedData.type !== 'summary_collection'"
        @click="saveDraft">
        保存草稿
      </bk-button>
      <bk-button :theme="'default'" @click="cancel" :title="'基础按钮'" class="mr10" style="padding: 0 30px;">
        {{isLast ? '返 回' : '取 消'}}
      </bk-button>
      <span v-if="isLast" class="last-text">当前步骤为最后一步</span>
    </div>
    <summary-form :summary-data="summaryData" :visible="dialogVisible" @close="close"></summary-form>
  </div>
</template>

<script>
import moment from 'moment';
// import _ from 'lodash';
import { mapGetters } from 'vuex';

import { APPROVE_ENUM, LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
import AwardUpload from '@/components/award-upload';
import SummaryForm from '@/components/system/summary-form.vue';
import LeftDetail from '@/components/user/left-detail.vue';
export default {
  components: {
    LeftDetail,
    AwardUpload,
    SummaryForm,
  },
  data() {
    return {
      reviewInfo: {
        status: 'approve',
        comment: '',
        forceMessage: '',
        forceReceivers: [],
        type: '',
        file: '',
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
      params: {},
      finishData: [],
      startedData: {
        details: {},
      },
      pendingData: [],
      APPROVE_ENUM,
      formLoading: true,
      visible: false,
      timeFormData: {},
      autoExecute: 'false',
      isLast: false,
      dialogVisible: false,
      awardId: '',
      detailFormList: [],
      editFormList: [],
      formData: {},
      rules: {},
      isAborted: false,
      showNextBtn: false,
      summaryInfo: {},
      summaryData: {},
    };
  },
  computed: {
    ...mapGetters(['user']),
  },
  mounted() {
    this.id = this.$route.query.id;
    this.stepId = this.$route.query.stepId;
    this.showNextBtn = this.$route.query.showNextBtn;
    if (window.localStorage.getItem(this.stepId)) {
      this.reviewInfo = JSON.parse(window.localStorage.getItem(this.stepId));
    }
    this.fetchApplyDetail();
    this.fetchStepsDetail();
  },
  methods: {
    // 详情
    async fetchApplyDetail() {
      try {
        const res = await this.$store.dispatch('user/getApplyDetail', this.id);
        this.awardId = res.award.id;
        this.setDetailRightData(res);
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

    // 右边动态信息
    setDetailRightData(data) {
      this.detailFormList = data.award.policy.raw_application_info.fields.map((e) => {
        if (e.key === 'status') {
          e.default = STATUS_ENUM[data[e.key]];
        } else if (e.key === 'date') {
          if (data.details[e.key]) {
            e.default = `${moment(data.details[e.key][0]).format('YYYY-MM-DD')} 至 ${moment(data.details[e.key][1]).format('YYYY-MM-DD')}`;
          }
        } else if (e.key === 'level') {
          e.default = LEVEL_ENUM[data.award.policy.level];
        } else if (e.key === 'upload') {
          e.default = data.details[e.key] && data.details[e.key].length &&  data.details[e.key][0].url;
        } else {
          e.default = Array.isArray(data.details[e.key]) ? data.details[e.key].join(',') : data.details[e.key];
        }
        return e;
      });
    },

    // 右边动态编辑信息
    setEditRightData(data) {
      this.editFormList = data || [];
      this.editFormList.forEach((item) => {
        this.$set(this.formData, item.key, item.default);
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

    // 左边申报信息
    setLeftData(data) {
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
      });
    },


    // 获取步骤
    async fetchStepsDetail() {
      try {
        const res = await this.$store.dispatch('system/getStepsDetail', this.id);
        this.finishData = res.filter(e => e.status === 'finished' || e.status === 'aborted');    // 前置环节
        this.startedData = res.find(e => e.status === 'started') || {};   // 当前环节
        this.autoExecute = this.startedData.policy?.auto_execute;   // 是否自动执行下一步
        this.isLast = this.finishData.length === res.length;    // 是否是最后一步
        this.isAborted = this.finishData.some(e => e.status === 'aborted');   // 是否有驳回操作
        this.summaryInfo = this.startedData.summary_info || {};   // 奖项沉淀信息
        this.reviewInfo.type = this.reviewInfo.type || this.startedData.type;      // 步骤对应的类型
        this.reviewInfo.forceMessage = this.reviewInfo.forceMessage || this.startedData.contents;
        this.reviewInfo.forceReceivers = this.reviewInfo.forceReceivers && this.reviewInfo.forceReceivers.length
          ? this.reviewInfo.forceReceivers : this.startedData.details?.receivers;
        this.reviewInfo.comment = this.reviewInfo.comment || this.startedData.details?.comment;
        this.pendingData = res.filter(e => e.status === 'pending');   // 下一环节
        if (this.startedData.policy && this.startedData.policy.bk_schemas) {
          this.setEditRightData(this.startedData.policy.bk_schemas);
        }
        this.formLoading = false;
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


    // 提交
    async submit() {
      let fetchUrl = '';
      if (this.reviewInfo.type === 'approval') {
        this.params = {
          id: this.id,
          status: this.reviewInfo.status,
          data: {
            comment: this.reviewInfo.comment,
          },
        };
        fetchUrl = 'system/fetchApprove';
      } else if (this.reviewInfo.type === 'extra_info_collection') {
        this.params = {
          id: this.startedData.id,
          data: {
            collection_data: this.formData,
          },
        };
        fetchUrl = 'system/fetchCollectData';
      } else {
        this.params = {
          data: {
            force_message: this.reviewInfo.forceMessage,
            force_receivers: this.reviewInfo.forceReceivers,
          },
        };
        fetchUrl = 'system/fetchNotify';
      }
      this.params.stepId = this.stepId;

      try {
        const res = await this.$store.dispatch(fetchUrl, this.params);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '操作成功',
        });
        // this.fetchNextApprove();
        this.cleanDraft();
        this.cancel();
      } catch (e) {
        console.error(e);
        if (e.message.search('request canceled') === -1) {
          this.bkMessageInstance = this.$bkMessage({
            limit: 1,
            theme: 'error',
            message: e.response.data.comment[0] || e.message || '系统错误',
            ellipsisLine: 2,
            ellipsisCopy: true,
          });
        }
      }
    },

    // 下一步
    async next() {
      try {
        const res = await this.$store.dispatch('system/fetchNext', this.id);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '操作成功',
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
    cancel() {
      this.$router.back(-1);
    },

    handleAfterLeave() {
      this.expiredAt = 15552000;
      this.$emit('update:show', false);
    },

    // 保存草稿
    saveDraft() {
      const { id } = this.startedData;
      window.localStorage.setItem(id, JSON.stringify(this.reviewInfo));
      this.$bkMessage({ theme: 'success', message: '保存草稿成功' });
    },

    // 清除草稿
    cleanDraft() {
      const { id } = this.startedData;
      localStorage.removeItem(id);
    },


    // 跳转反馈复审时间
    toReviewTime() {
      this.$router.push({
        name: this.user.system_role === 'admin' ? 'systime-detail' : 'time-detail',
        query: {
          id: this.awardId,
        },
      });
    },

    // 跳转奖项沉淀编辑
    toSummaryPage(summaryId) {
      this.dialogVisible = true;
      this.summaryData = {
        summaryId,
        id: this.id,
        awardId: this.id,
      };
    },

    // 关闭弹窗
    close() {
      this.dialogVisible = false;
    },
  },
};
</script>

<style lang="postcss" scoped>
.detail-content {
  position: relative;

  .main {
    display: flex;
    height: calc(100vh - 305px);
    min-height: 500px;
    padding: 10px 20px;
    overflow: auto;
    font-size: 14px;
    line-height: 2em;
    color: #646464;
    justify-content: space-between;

    .detail {
      width: 590px;
      word-wrap: break-word;
    }

    .content {
      padding: 0 15px;
      background: #fff;
      flex: 1;

      /* border-left: 1px solid #ccc; */
      .content-txt {
        margin-bottom: 20px;
      }

      .label-right {
        display: inline-block;
        width: 145px;
        margin-right: 15px;
        text-align: right;
      }

      .review-upload {
        width: 420px;
      }


      .review-comments {
        display: flex;
      }

      .radio-comments {
        width: 185px;
      }

      .file-wrapper {
        margin: 10px 0;
      }
    }

    .bk-form-radio {
      line-height: 28px;
    }

    .prev-container {
      display: flex;
      margin-top: 10px;

      .left {
        display: flex;
        width: 200px;
        height: 100px;
        padding: 0px 10px;
        overflow-y: auto;
        background: #e7e7e7;
        align-items: center;
        justify-content: center;
      }

      .right {
        margin-left: 20px;
        flex: 1;

        .status {
          height: 30px;
          padding-left: 15px;
          line-height: 30px;
          color: #2dcb56;
          background: #e7e7e7;
        }

        .aborted {
          color: #ff5656;
        }

        .comment {
          height: 63px;
          padding: 0 15px;
          margin-top: 5px;
          overflow-y: auto;
          font-size: 12px;
          background: #e7e7e7;
        }

      }
    }

  }

  .border {
    position: absolute;
    top: 0px;
    bottom: 39px;
    left: 610px;
    width: 1px;
    background: #ccc;
  }

  .btn-wrapper {
    padding-top: 7px;
    text-align: center;

    .btn-font {
      font-weight: 700;
    }

    .last-text {
      font-size: 14px;
      color: #ff9c01;
    }
  }
}
</style>
