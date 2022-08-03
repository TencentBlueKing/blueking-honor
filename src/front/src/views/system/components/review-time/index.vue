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
          <template v-if="obj.type === 'bk-select'">
            <template v-if="obj.key === 'award_name'">
              <bk-option
                v-for="item in obj.optionData"
                :key="item.label"
                :id="item.label"
                :name="item.label">
              </bk-option>
            </template>
            <template v-else>
              <bk-option
                v-for="item in obj.optionData"
                :key="item.value"
                :id="item.value"
                :name="item.label">
              </bk-option>
            </template>
          </template>
        </component>
      </bk-form-item>
    </bk-form>

    <!-- 表格 -->
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
            @click="handleRouter(props.row)">
            反馈复审时间
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
import moment from 'moment';
import { mapGetters } from 'vuex';

import { LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
import { json2Array } from '@/common/util';
export default {
  data() {
    return {
      awards: '',
      tableList: [],
      tableLoading: false,
      pagination: {
        current: 1,
        count: 10,
        limit: 10,
      },
      dataJson: [
        {
          key: 'level',
          label: '级别',
          type: 'bk-select',
          default: '',
          optionData: json2Array(LEVEL_ENUM),
          placeholder: '请选择级别',
        },
        {
          key: 'status',
          label: '奖项状态',
          type: 'bk-select',
          default: '',
          optionData: json2Array(STATUS_ENUM),
          placeholder: '请选择奖项状态',
        },
      ],
      tableColumnData: [
        { prop: 'policy.level', label: '级别', formatter: row => LEVEL_ENUM[row.policy.level] },
        { prop: 'name', label: '奖项', sortable: true },
        { prop: 'status', label: '奖项状态', formatter: row => STATUS_ENUM[row.status] },
        { prop: 'started_at', label: '开始时间', formatter: row => moment(row.started_at * 1000).format('YYYY-MM-DD'), sortable: true },
        { prop: 'ended_at', label: '截止时间', formatter: row => moment(row.ended_at * 1000).format('YYYY-MM-DD'), sortable: true  },
      ],
      formData: {},
      params: {
        page: 1,
        page_size: 10,
      },
    };
  },
  computed: {
    ...mapGetters(['user']),
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
  },
  methods: {
    async fetchData() {
      this.tableLoading = true;
      try {
        const res = await this.$store.dispatch('system/getApprovalAwards', this.params);
        this.tableList = res.results;
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

    // 查看
    handleRouter(data) {
      this.$router.push({
        name: 'systime-detail',
        query: {
          id: data.id,
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
    search() {
      this.pagination.current = 1;
      this.params = {
        page: 1,
        page_size: this.pagination.limit,
      };
      Object.keys(this.formData).forEach((key) => {
        this.params[key] = this.formData[key];
      });
      this.fetchData();
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
</style>
