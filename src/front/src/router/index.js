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
 * @file router 配置
 * @author
 */

import Vue from 'vue';
import VueRouter from 'vue-router';

import systemRoutes from './system';
import userRoutes from './user';

import http from '@/api';
import preload from '@/common/preload';
import store from '@/store';

// import MainEntry from '@/views'
const MainEntry = () => import(/* webpackChunkName: 'entry' */'@/views');
const Apply = () => import(/* webpackChunkName: 'apply' */'@/views/apply');
const Summary = () => import(/* webpackChunkName: 'summary' */'@/views/summary');
const Records = () => import(/* webpackChunkName: 'records' */'@/views/records');
// import NotFound from '@/views/404'
const NotFound = () => import(/* webpackChunkName: 'none' */'@/views/404');

Vue.use(VueRouter);

const rootRoutes = [
  {
    path: '/index',
    name: 'index',
    component: MainEntry,
    alias: '',
    meta: {
      name: '首页',
    },
  },
  {
    path: '/apply',
    name: 'apply',
    component: Apply,
    alias: '',
    meta: {
      name: '申报',
    },
  },
  {
    path: '/summary',
    name: 'summary',
    component: Summary,
    alias: '',
    meta: {
      name: '沉淀',
    },
  },
  {
    path: '/records',
    name: 'records',
    component: Records,
    alias: '',
    meta: {
      name: '获奖记录',
    },
  },
  // 404
  {
    path: '*',
    name: '404',
    component: NotFound,
  },
];

const routes = rootRoutes.concat(userRoutes, systemRoutes);

const router = new VueRouter({
  linkActiveClass: 'is-active',
  mode: 'history',
  routes,
});

const cancelRequest = async () => {
  const allRequest = http.queue.get();
  const requestQueue = allRequest.filter(request => request.cancelWhenRouteChange);
  await http.cancel(requestQueue.map(request => request.requestId));
};

let preloading = true;
let canceling = true;
let pageMethodExecuting = true;

router.beforeEach(async (to, from, next) => {
  canceling = true;
  await cancelRequest();
  canceling = false;
  next();
});

router.afterEach(async (to) => {
  store.commit('setMainContentLoading', true);

  preloading = true;
  await preload();
  preloading = false;

  const pageDataMethods = [];
  const routerList = to.matched;
  routerList.forEach((r) => {
    Object.values(r.instances).forEach((vm) => {
      if (typeof vm.fetchPageData === 'function') {
        pageDataMethods.push(vm.fetchPageData());
      }
      if (typeof vm.$options.preload === 'function') {
        pageDataMethods.push(vm.$options.preload.call(vm));
      }
    });
  });

  pageMethodExecuting = true;
  await Promise.all(pageDataMethods);
  pageMethodExecuting = false;

  if (!preloading && !canceling && !pageMethodExecuting) {
    store.commit('setMainContentLoading', false);
  }
});

export default router;
