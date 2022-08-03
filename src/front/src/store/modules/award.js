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
 * 奖项接口
 */

import queryString from 'query-string';

import http from '@/api';

export default {
  namespaced: true,
  state: {
  },
  mutations: {
  },
  actions: {
    getTableData(context, params, config = {}) {
      // eslint-disable-next-line no-undef
      return http.get(`/table?&${queryString.stringify(params)}`, params, config);
    },
    // 获取奖项信息
    getAward(context, params, config = {}) {
      return http.get(`/api/v1/awards/${params.id}/`, params, config);
    },
    // 获取奖项列表
    getAwardList(context, params, config = {}) {
      return http.get(`/api/v1/awards/?&${queryString.stringify(params)}`, params, config);
    },
    // 获取首页奖项申报列表
    getIndexAwards(context, params, config = {}) {
      return http.get(`/api/v1/awards/get_index_awards/?&${queryString.stringify(params)}`, params, config);
    },
    // 获取首页奖项回顾列表
    getIndexSummaries(context, params, config = {}) {
      return http.get(`/api/v1/summaries/get_index_awards_summaries/?&${queryString.stringify(params)}`, params, config);
    },
    // 获取奖项回顾列表
    getAwardSummaries(context, params, config = {}) {
      return http.get(`/api/v1/summaries/get_summaries_from_award/?&${queryString.stringify(params)}`, params, config);
    },
    // 获取单个奖项回顾列表
    getAwardSummary(context, params, config = {}) {
      return http.get('/api/v1/summaries/', params, config);
    },
    // 给奖项沉淀点赞
    likeAward(context, params, config = {}) {
      return http.post(`/api/v1/summaries/${params.id}/like/`, params, config);
    },
    // 获取个人获奖记录
    getAwardRecords(context, params, config = {}) {
      return http.get(`/api/v1/summaries/records/?&${queryString.stringify(params)}`, params, config);
    },
    // 搜索奖项申报、沉淀
    getSearchList(context, params, config = {}) {
      return http.get(`/api/v1/awards/search/?&${queryString.stringify(params)}`, params, config);
    },
    // 奖项申报
    apply(context, params, config = {}) {
      return http.post(`/api/v1/awards/${params.id}/apply/`, params, config);
    },
  },
};
