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
 * @file auth
 * @author
 */

import store from '@/store';

const ANONYMOUS_USER = {
  id: null,
  isAuthenticated: false,
  username: 'anonymous',
};

let currentUser = {
  id: '',
  username: '',
};

export default {
  /**
   * 未登录状态码
   */
  HTTP_STATUS_UNAUTHORIZED: 401,

  /**
   * 获取当前用户
   *
   * @return {Object} 当前用户信息
   */
  getCurrentUser() {
    return currentUser;
  },

  redirectToLogin() {
    window.location = `${window.PROJECT_CONFIG.login_site}/?c_url=${encodeURIComponent(window.location.href)}`;
  },

  /**
   * 请求当前用户信息
   *
   * @return {Promise} promise 对象
   */
  requestCurrentUser() {
    let promise = null;
    if (currentUser.isAuthenticated) {
      promise = new Promise((resolve) => {
        resolve(currentUser);
      });
    } else {
      if (!store.state.user || !Object.keys(store.state.user).length) {
        // store action userInfo 里，如果请求成功会更新 state.user
        const req = store.dispatch('userInfo');
        promise = new Promise((resolve, reject) => {
          req.then(() => {
            // 存储当前用户信息(全局)
            currentUser = store.getters.user;
            currentUser.isAuthenticated = true;
            resolve(currentUser);
          }, (err) => {
            if (err.response.status === this.HTTP_STATUS_UNAUTHORIZED || err.crossDomain) {
              resolve({ ...ANONYMOUS_USER });
            } else {
              reject(err);
            }
          });
        });
      }
    }

    return promise;
  },
};
