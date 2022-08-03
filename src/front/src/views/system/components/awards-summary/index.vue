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
    <!-- 搜索 -->
    <bk-form :label-width="150" :model="formData"
             form-type="inline"
             ext-cls="apply-form">
      <bk-form-item
        v-for="obj in dataJson"
        :label="obj.label"
        :key="obj.key"
        :desc="obj.desc"
        :property="obj.key">
        <component
          :is="obj.type"
          style="width: 202px;"
          :placeholder="obj.placeholder"
          :type="obj.componentType"
          v-model="formData[obj.key]">
          <bk-option
            v-for="item in obj.optionData"
            :key="item.label"
            :id="item.label"
            :name="item.label">
          </bk-option>
        </component>
      </bk-form-item>
      <bk-form-item label="" style="vertical-align: top;">
        <bk-button theme="primary" type="button" @click="handleAdd('')"> 新增 </bk-button>
      </bk-form-item>
    </bk-form>

    <!-- 表格 -->
    <h3 class="tableTitle mt20">季度/分期奖项沉淀</h3>
    <bk-table
      :data="tableList"
      :size="'small'"
      :pagination="pagination"
      :outer-border="false"
      v-bkloading="{ isLoading: tableLoading }"
      @page-limit-change="handlePageLimitChange"
      @page-change="handlePageChange">
      <bk-table-column
        v-for="item in tableColumnData"
        :key="item.prop"
        :sortable="item.sortable"
        :formatter="item.formatter"
        :label="item.label" :prop="item.prop"
      ></bk-table-column>

      <bk-table-column label="操作" width="200" class="ag-action" :show-overflow-tooltip="false">
        <template slot-scope="props">
          <bk-button
            class="mr10"
            text
            theme="primary"
            @click="handleAdd(props.row)">
            编辑
          </bk-button>
          <bk-popconfirm
            trigger="click"
            title="确认删除该奖项？"
            content="删除操作无法撤回，请谨慎操作！"
            @confirm="handleDelete(props.row)">
            <bk-button
              class="mr10"
              text
              theme="primary">
              删除
            </bk-button>
          </bk-popconfirm>
        </template>
      </bk-table-column>
    </bk-table>

    <!-- 年度奖项沉淀表格 -->
    <h3 class="tableTitle">年度奖项沉淀</h3>
    <bk-table
      :data="tableListSummary"
      :size="'small'"
      :pagination="summaryPagination"
      :outer-border="false"
      v-bkloading="{ isLoading: tableSummaryLoading }"
      @page-limit-change="handleSummaryPageLimitChange"
      @page-change="handleSummaryPageChange">
      <bk-table-column
        v-for="item in tableSummaryColumnData"
        :key="item.prop"
        :sortable="item.sortable"
        :formatter="item.formatter"
        :label="item.label" :prop="item.prop"
      ></bk-table-column>

      <bk-table-column label="操作" width="200" class="ag-action" :show-overflow-tooltip="false">
        <template slot-scope="props">
          <bk-button
            class="mr10"
            text
            theme="primary"
            @click="handleAdd(props.row)">
            编辑
          </bk-button>
          <bk-popconfirm
            trigger="click"
            title="确认删除该奖项？"
            content="删除操作无法撤回，请谨慎操作！"
            @confirm="handleDelete(props.row)">
            <bk-button
              class="mr10"
              text
              theme="primary">
              删除
            </bk-button>
          </bk-popconfirm>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
import moment from 'moment';

import { LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
export default {
  data() {
    return {
      awards: '',
      awardsList: [],
      tableList: [],
      tableListSummary: [],
      tableLoading: false,
      tableSummaryLoading: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      summaryPagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      dataJson: [
        {
          key: 'award_name',
          label: '奖项名称',
          type: 'bk-select',
          default: '',
          optionData: [],
          placeholder: '请选择奖项名称',
        },
        {
          key: 'liaison',
          label: '奖项接口人',
          type: 'bk-tag-input',
          'allow-create': true,
          default: '',
          placeholder: '请选择奖项接口人',
        },
        {
          key: 'daterange-picker',
          label: '奖项沉淀时间',
          type: 'bk-date-picker',
          default: [],
          required: true,
          placeholder: '选择奖项沉淀时间',
        },
      ],
      tableColumnData: [
        { prop: 'level', label: '级别', formatter: row => LEVEL_ENUM[row.award.policy.level] },
        { prop: 'award.name', label: '奖项', sortable: true },
        { prop: 'award.status', label: '奖项状态', formatter: row => STATUS_ENUM[row.award.status] },
        { prop: 'award.started_at', label: '开始时间', formatter: row => moment(row.award.started_at * 1000).format('YYYY-MM-DD'), sortable: true },
        { prop: 'award.ended_at', label: '截止时间', formatter: row => moment(row.award.ended_at * 1000).format('YYYY-MM-DD'), sortable: true },
      ],
      tableSummaryColumnData: [
        { prop: 'details.material_title', label: '一句话标题' },
        { prop: 'year', label: '年度' },
        { prop: 'policy_name', label: '关联奖项/奖项策略名称' },
        { prop: 'details.project_name', label: '项目名称' },
        { prop: 'details.team_members', label: '团队成员名单', formatter: row => row.details.team_members && row.details.team_members.join(',') },
      ],
      formData: {},
      params: {
        page_size: 10,
      },
      summaryParams: {
        page_size: 10,
      },
    };
  },
  watch: {
    formData: {
      handler() {
        this.search();
      },
      deep: true,
    },
  },
  created() {
    this.fetchData();
    this.fetchSummaryData();
    this.fetchAawrdsList();
  },
  methods: {
    async fetchData() {
      this.tableLoading = true;
      try {
        const res = await this.$store.dispatch('system/getSummariesData', this.params);
        this.tableList = (res.results || []).filter(e => !!e.award);
        // this.tableListSummary = (res.results || []).filter(e => !e.award);
        this.pagination.count = res.count;
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
        this.tableLoading = false;
      }
    },

    async fetchSummaryData() {
      this.tableSummaryLoading = true;
      try {
        const res = await this.$store.dispatch('system/getAnnualSummariesData', this.summaryParams);
        this.tableListSummary = res.results;
        this.summaryPagination.count = res.count;
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
        this.tableSummaryLoading = false;
      }
    },

    async fetchAawrdsList() {
      const params = {
        page_size: 1000,
      };
      try {
        const res = await this.$store.dispatch('system/getAwardsList', params);
        this.awardsList = (res.results || []).map(e => ({
          value: e.id,
          label: e.name,
        }));
        this.$store.commit('system/updateAwards', this.awardsList);
        this.setAwardsList();
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

    // 设置setAwardsList
    setAwardsList() {
      this.dataJson.forEach((e) => {
        if (e.key === 'award_name') {
          e.optionData = this.awardsList;
        }
        this.formLoading = false;
      });
    },
    // 跳转新增编辑页面
    handleAdd(data) {
      this.$router.push({
        name: 'promotional',
        query: {
          id: data.application,
          summaryId: data.id,
        },
      });
    },
    handlePageLimitChange(limit) {
      this.pagination.limit = limit;
      this.pagination.current = 1;
      this.params.page = this.pagination.current;
      this.params.page_size = limit;
      this.fetchData();
    },
    handlePageChange(page) {
      this.pagination.current = page || 1;
      this.params.page = this.pagination.current;
      this.fetchData();
    },
    handleSummaryPageLimitChange(limit) {
      this.summaryPagination.limit = limit;
      this.summaryPagination.current = 1;
      this.summaryParams.page = this.summaryPagination.current;
      this.summaryParams.page_size = limit;
      this.fetchSummaryData();
    },
    handleSummaryPageChange(page) {
      this.summaryPagination.current = page || 1;
      this.summaryParams.page = this.summaryPagination.current;
      this.fetchSummaryData();
    },
    search() {
      this.pagination.current = 1;
      this.params = {
        page: 1,
        page_size: this.pagination.limit,
      };
      Object.keys(this.formData).forEach((key) => {
        this.params[key] = this.formData[key];
        if (key === 'liaison') {
          this.params[key] = this.formData[key].join(',');
        } else if (key === 'daterange-picker') {
          this.params.search_datetime = new Date(this.formData[key]).getTime() / 1000 || '';
          delete this.formData['daterange-picker'];
        }
      });
      this.fetchData();
    },

    // 删除某条数据
    async handleDelete(val) {
      const { id } = val;
      this.tableLoading = true;
      this.tableSummaryLoading = true;
      try {
        const res = await this.$store.dispatch('system/deleteSummariesData', { id });
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '删除成功',
        });
        this.fetchData();
        this.fetchSummaryData();
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
        this.tableLoading = false;
        this.tableSummaryLoading = false;
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
    .content-declare {
      background: #fff;
      border-radius: 15px;
    }

    .apply-form {
      margin: 20px 15px;
    }

    .input-demo {
      input {
        width: 150px;
        outline: none;
      }
    }

    .search-btn {
      margin-top: 2px;

      .bk-button {
        height: 28px;
        padding: 0 20px;
      }

      .font {
        display: inline-block;
        transform: translateY(-2px);
      }
    }

    .footer-btn {
      width: 200px;
      margin: 100px auto 0;
    }

    .tableTitle {
      margin: 40px 0 20px 20px;
    }
</style>
