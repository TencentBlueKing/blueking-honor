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
            <bk-option
              v-for="item in obj.optionData"
              :key="item.value"
              :id="item.value"
              :name="item.label">
            </bk-option>

          </template>
        </component>
      </bk-form-item>
      <bk-form-item class="btn-info">
        <!-- <bk-button theme="primary" type="button" @click="search"> 查询 </bk-button> -->
        <bk-button theme="primary" type="button" @click="handleAdd()"> 新增 </bk-button>
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
        :formatter="item.formatter"
        :sortable="item.sortable"
        :key="item.prop"
        :label="item.label" :prop="item.prop"
      ></bk-table-column>

      <bk-table-column label="操作" width="200" class="ag-action" :show-overflow-tooltip="false">
        <template slot-scope="props">
          <bk-button
            class="mr10"
            text
            theme="primary"
            @click="handleView(props.row)">
            查看
          </bk-button>
          <bk-button
            class="mr10"
            text
            theme="primary"
            v-if="props.row.policy.liaisons.includes(user.username)"
            @click="handleCopy(props.row)">
            复制
          </bk-button>
          <bk-button
            class="mr10"
            text
            theme="primary"
            v-if="props.row.policy.liaisons.includes(user.username)"
            @click="handleAdd(props.row)">
            编辑
          </bk-button>
          <bk-popconfirm
            trigger="click"
            title="确认删除该奖项？"
            content="删除操作无法撤回，请谨慎操作！"
            v-if="props.row.policy.liaisons.includes(user.username)"
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
import { mapGetters } from 'vuex';

import { LEVEL_ENUM, STATUS_ENUM } from '@/common/constants';
import { json2Array } from '@/common/util';
export default {
  data() {
    return {
      awards: '',
      awardsList: [],
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
        const res = await this.$store.dispatch('system/getAwardsList', this.params);
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

    // 复制
    async handleCopy(data) {
      try {
        const res = await this.$store.dispatch('system/copyAwardsData',  data.id);
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '复制成功',
        });
        this.fetchData();
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
    handleView(data) {
      this.$router.push({
        name: 'award-operate',
        query: {
          type: 'view',
          id: data.id,
        },
      });
    },

    // 跳转新增编辑页面
    handleAdd(data = '') {
      this.$router.push({
        name: 'award-operate',
        query: {
          type: 'edit',
          id: data ? data.id : '',
        },
      });
    },

    // 删除某条数据
    async handleDelete(val) {
      const { id } = val;
      this.tableLoading = true;
      try {
        const res = await this.$store.dispatch('system/deleteAwardsData', { id });
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '删除成功',
        });
        this.fetchData();
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
  },
};
</script>

<style lang="postcss" scoped>
    .apply-form {
      margin: 20px 15px;
    }
</style>
