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
  },
  actions: {

    // 获取申请列表
    getApplicationsList(context, params, config = {}) {
      return http.get(`/api/v1/applications/?${json2Query(params)}`, config);
    },

    // 获取评审列表
    getApprovesList(context, params, config = {}) {
      return http.get(`/api/v1/approvals/?${json2Query(params)}`, config);
    },

    // 获取当前申报的详情内容
    getApplyDetail(context, id, config = {}) {
      return http.get(`/api/v1/applications/${id}/`, config);
    },

    // 获取当前申报的审批内容
    getApprovalStep(context, id, config = {}) {
      return http.get(`/api/v1/applications/${id}/steps/`, config);
    },

    // 评委提交可用时间
    postAvaiFeedTime(context, { id, data }, config = {}) {
      return http.post(`/api/v1/awards/${id}/feed_available_periods/`, data, config);
    },
  },
};

