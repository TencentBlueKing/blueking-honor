/*
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
*/
/**
 * @file app store
 * @author
 */


import cookie from 'cookie';

import http from '@/api';
import { json2Query } from '@/common/util';

export default {
  namespaced: true,
  state: {},
  mutations: {
    updateBreadcrumbList(state, data) {
      if (state.breadcrumbList.length > 1) {
        state.breadcrumbList.pop();
      }
      state.breadcrumbList.push(data);
    },

    /**
     * 更新奖项列表
     *
     * @param {Object} state store state
     * @param {Object} user data 数组
     */
    updateAwards(state, data) {
      state.awardsList = data;
    },
  },
  actions: {
    // 获取奖项信息
    getAwardsList(context, params, config = {}) {
      return http.get(`/api/v1/awards/?${json2Query(params)}`, config);
    },

    // 新增奖项
    addAwardsData(context, params, config = {}) {
      return http.post('/api/v1/awards/', params, config);
    },

    // 更新奖项
    updateAwardsData(context, params, config = {}) {
      const { id } = params;
      delete params.id;
      return http.put(`/api/v1/awards/${id}/`, params, config);
    },

    // 奖项详情
    getAwardDetail(context, id, config = {}) {
      return http.get(`/api/v1/awards/${id}/`, config);
    },

    // 删除奖项
    deleteAwardsData(context, { id }, config = {}) {
      return http.delete(`/api/v1/awards/${id}/`, config);
    },

    // 复制奖项
    copyAwardsData(context, id, config = {}) {
      return http.post(`/api/v1/awards/${id}/copy/`, config);
    },

    // 获取所有策略
    getPoliciesList(context, params, config = {}) {
      return http.get(`/api/v1/policies/?${json2Query(params)}`, config);
    },

    // 删除策略模板
    deletePoliciesData(context, { id }, config = {}) {
      return http.delete(`/api/v1/policies/${id}/`, config);
    },

    // 获取策略模板详情
    getTempleDetail(context, id, config = {}) {
      return http.get(`/api/v1/policies/${id}/`, config);
    },

    // 获取奖项沉淀
    getSummariesData(context, params = {}, config = {}) {
      return http.get(`/api/v1/summaries/?${json2Query(params)}`, config);
    },

    // 获取年度奖项沉淀
    getAnnualSummariesData(context, params = {}, config = {}) {
      return http.get(`/api/v1/summaries/get_annual_summary_list/?${json2Query(params)}`, config);
    },

    // 删除奖项沉淀
    deleteSummariesData(context, { id }, config = {}) {
      return http.delete(`/api/v1/summaries/${id}/`, config);
    },

    // 奖项沉淀详情
    getSummaryDetail(context, id, config = {}) {
      return http.get(`/api/v1/summaries/${id}/`, config);
    },

    // 新增奖项沉淀
    addSummaryData(context, params, config = {}) {
      return http.post('/api/v1/summaries/', params, config);
    },


    // 编辑奖项沉淀
    updateSummaryData(context, params, config = {}) {
      const { id } = params.details;
      delete params.details.id;
      return http.put(`/api/v1/summaries/${id}/`, params, config);
    },


    // 审批
    fetchApprove(context, { stepId, status, data  }, config = {}) {
      return http.post(`/api/v1/approvals/${stepId}/${status}/`, data, config);
    },

    // 通知
    fetchNotify(context, { stepId, data  }, config = {}) {
      return http.post(`/api/v1/notifications/${stepId}/notify/`, data, config);
    },

    // 下一步
    fetchNext(context, id, config = {}) {
      return http.post(`/api/v1/applications/${id}/next/`, config);
    },

    // BG复审
    fetchCollectData(context, { id, data  }, config = {}) {
      return http.post(`/api/v1/collections/${id}/extra_info_collect/`, data, config);
    },

    // 步骤
    getStepsDetail(context, id, config = {}) {
      return http.get(`/api/v1/applications/${id}/steps/`, config);
    },


    // 导出某条申报
    exportApplyItem(context, id) {
      const CSRFToken = cookie.parse(document.cookie)[`${window.PROJECT_CONFIG.BKPAAS_APP_ID}_csrftoken`];
      // eslint-disable-next-line no-undef
      const url = `${window.PROJECT_CONFIG.SITE_URL + AJAX_URL_PREFIX}/api/v1/applications/${id}/export/`;
      return fetch(url, {
        credentials: 'include',
        method: 'POST',
        // body: JSON.stringify(params),
        headers: new Headers({
          'Content-Type': 'application/json',
          'X-CSRFToken': CSRFToken,
        }),
      });
    },

    // 批量导出申报
    exportApplyList(context, params = {}) {
      const CSRFToken = cookie.parse(document.cookie)[`${window.PROJECT_CONFIG.BKPAAS_APP_ID}_csrftoken`];
      // eslint-disable-next-line no-undef
      const url = `${window.PROJECT_CONFIG.SITE_URL + AJAX_URL_PREFIX}/api/v1/applications/bulk_export/`;
      return fetch(url, {
        credentials: 'include',
        method: 'POST',
        body: JSON.stringify(params),
        headers: new Headers({
          'Content-Type': 'application/json',
          'X-CSRFToken': CSRFToken,
        }),
      });
    },


    // 批量通过
    approveList(context, data = {}, config = {}) {
      return http.post('/api/v1/approvals/bulk_approve/', data, config);
    },

    // 批量驳回
    rejectList(context, data = {}, config = {}) {
      return http.post('/api/v1/approvals/bulk_reject/', data, config);
    },

    // 获取评委复审列表
    getAvailableList(context, params, config = {}) {
      const { id } = params;
      delete params.id;
      return http.get(`/api/v1/awards/${id}/available_periods/?${json2Query(params)}`, config);
    },

    // 确认可用时间
    confirmApproTime(context, { id, data }, config = {}) {
      return http.post(`/api/v1/awards/${id}/confirm_approval_period/`, data, config);
    },

    // 获取反馈评审时间的奖项列表
    getApprovalAwards(context, params = {}, config = {}) {
      return http.get(`/api/v1/awards/get_approval_awards/?${json2Query(params)}`, config);
    },

    // 获取反馈评审时间的奖项详情
    getApprovalAwardsDetail(context, id, config = {}) {
      return http.get(`/api/v1/awards/${id}/get_approval_award_details/`, config);
    },
  },
};


