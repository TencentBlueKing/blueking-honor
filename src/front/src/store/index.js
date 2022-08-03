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
/* eslint-disable no-undef */
/**
 * @file main store
 * @author
 */

import Vue from 'vue';
import Vuex from 'vuex';

import award from './modules/award';
import system from './modules/system';
import user from './modules/user';

import http from '@/api';

Vue.use(Vuex);

const store = new Vuex.Store({
  // 模块
  modules: {
    award,
    user,
    system,
  },
  // 公共 store
  state: {
    mainContentLoading: false,
    // 系统当前登录用户
    user: {},
  },
  // 公共 getters
  getters: {
    mainContentLoading: state => state.mainContentLoading,
    user: state => state.user,
  },
  // 公共 mutations
  mutations: {
    /**
     * 设置内容区的 loading 是否显示
     *
     * @param {Object} state store state
     * @param {boolean} loading 是否显示 loading
     */
    setMainContentLoading(state, loading) {
      state.mainContentLoading = loading;
    },

    /**
     * 更新当前用户 user
     *
     * @param {Object} state store state
     * @param {Object} user user 对象
     */
    updateUser(state, user) {
      state.user = Object.assign({}, user);
    },
  },
  actions: {
    /**
     * 获取用户信息
     *
     * @param {Object} context store 上下文对象 { commit, state, dispatch }
     *
     * @return {Promise} promise 对象
     */
    userInfo(context, params, config = {}) {
      return http.get('/api/v1/user/info/', params, config).then((response) => {
        const userData = response || {};
        context.commit('updateUser', userData);
        return userData;
      });
    },
    logout(context, params, config = {}) {
      return http.post('/api/v1/user/logout/', params, config).then(response => response);
    },

    logout() {
      return http.post('/api/v1/user/logout/').then(response => response);
    },
  },
});

export default store;
