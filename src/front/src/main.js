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
 * @file main entry
 * @author
 */
import { format } from 'date-fns';
import Vue from 'vue';
import xss from 'xss';

import './public-path';
import '@/common/bkmagic';
import http, { injectCSRFTokenToHeaders } from '@/api';
import App from '@/App';
import auth from '@/common/auth';
import { bus } from '@/common/bus';
import AuthComponent from '@/components/auth';
import Exception from '@/components/exception';
import Img403 from '@/images/403.png';
import router from '@/router';
import store from '@/store';

// 定义全局XSS解决方法
Object.defineProperty(Vue.prototype, '$xss', {
  value: xss,
});
Vue.prototype.$http = http;

Vue.component('AppException', Exception);
Vue.component('AppAuth', AuthComponent);

Vue.filter('formatDate', (value, arg1) => {
  if (!value) return '--';
  return arg1 === 'date' ? format(value * 1000, 'yyyy-MM-dd') : format(value * 1000, 'yyyy-MM-dd HH:mm:ss');
});

auth.requestCurrentUser().then((user) => {
  injectCSRFTokenToHeaders();
  if (user.isAuthenticated) {
    global.bus = bus;
    global.mainComponent = new Vue({
      el: '#app',
      router,
      store,
      components: { App },
      template: '<App/>',
    });
  } else {
    auth.redirectToLogin();
  }
}, (err) => {
  let message;
  if (err.status === 403) {
    message = 'Sorry，您的权限不足!';
    if (err.data && err.data.msg) {
      message = err.data.msg;
    }
  } else {
    message = '无法连接到后端服务，请稍候再试。';
  }

  const divStyle = ''
        + 'text-align: center;'
        + 'width: 400px;'
        + 'margin: auto;'
        + 'position: absolute;'
        + 'top: 50%;'
        + 'left: 50%;'
        + 'transform: translate(-50%, -50%);';

  const h2Style = 'font-size: 20px;color: #979797; margin: 32px 0;font-weight: normal';

  const content = ''
        + `<div class="bk-exception bk-exception-center" style="${divStyle}">`
        + `<img src="${Img403}"><h2 class="exception-text" style="${h2Style}">${message}</h2>`
        + '</div>';

  document.write(content);
});
