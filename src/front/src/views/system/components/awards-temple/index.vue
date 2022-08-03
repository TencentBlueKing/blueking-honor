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
    <bk-form :label-width="150"
             form-type="inline"
             ext-cls="apply-form">
      <bk-form-item label="" style="vertical-align: top;">
        <bk-button theme="primary" type="button" disabled> 新建策略模板 </bk-button>
      </bk-form-item>
    </bk-form>

    <!-- 表格 -->
    <bk-table
      :data="tableList"
      :size="'small'"
      :pagination="pagination"
      :outer-border="false"
      v-show="!tableLoading"
      v-bkloading="{ isLoading: tableLoading, opacity: 1 }"
      @page-limit-change="handlePageLimitChange"
      @page-change="handlePageChange">
      <bk-table-column
        v-for="item in tableColumnData"
        :key="item.prop"
        :formatter="item.formatter"
        :label="item.label" :prop="item.prop"
      ></bk-table-column>

      <bk-table-column label="操作" width="200" class="ag-action" :show-overflow-tooltip="false">
        <template slot-scope="props">
          <!-- <bk-popconfirm
            trigger="click"
            title="确认删除该策略？"
            content="删除操作无法撤回，请谨慎操作！"
            @confirm="handleDelete(props.row)">
            <bk-button
              class="mr10"
              text
              theme="primary">
              删除
            </bk-button>
          </bk-popconfirm> -->
          <bk-button
            class="mr10"
            text
            theme="primary"
            @click="handleView(props.row)">
            查看
          </bk-button>
        </template>
      </bk-table-column>
    </bk-table>
  </div>
</template>

<script>
import { LEVEL_ENUM } from '@/common/constants';
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
      tableColumnData: [
        { prop: 'level', label: '级别', formatter: row => LEVEL_ENUM[row.level] },
        { prop: 'name', label: '奖项' },
        { prop: 'liaisons', label: '奖项接口人', formatter: row => row.liaisons.join(',') || '--' },
      ],
      params: {
        page_size: 10,
      },
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    async fetchData() {
      this.tableLoading = true;
      try {
        const res = await this.$store.dispatch('system/getPoliciesList', this.params);
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

    // 删除某条数据
    async handleDelete(val) {
      const { id } = val;
      this.tableLoading = true;
      try {
        const res = await this.$store.dispatch('system/deletePoliciesData', { id });
        this.bkMessageInstance = this.$bkMessage({
          limit: 1,
          theme: 'success',
          message: res.message || '删除成功',
        });
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
        name: 'temple-detail',
        query: {
          id: data.id,
        },
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
