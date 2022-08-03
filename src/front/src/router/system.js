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
const system = () => import(/* webpackChunkName: 'system' */'@/views/system/index');
const SystemAwardsInfo = () => import(/* webpackChunkName: 'system' */'@/views/system/components/awards-info');
const SystemSummary = () => import(/* webpackChunkName: 'system' */'@/views/system/components/awards-summary/index.vue');
const SystemSummaryDetail = () => import(/* webpackChunkName: 'system' */'@/views/system/components/awards-summary/detail.vue');
const SystemAwardsOperate = () => import(/* webpackChunkName: 'system' */'@/views/system/components/award-operate');
const SystemApplyList = () => import(/* webpackChunkName: 'system' */'@/views/system/components/apply-list/index.vue');
const ApplyDetail = () => import(/* webpackChunkName: 'system' */'@/views/system/components/apply-list/apply-detail');
const SystemAwardsTemple = () => import(/* webpackChunkName: 'system' */'@/views/system/components/awards-temple/index');
const TempleDetail = () => import(/* webpackChunkName: 'system' */'@/views/system/components/awards-temple/temple-detail');
const ReviewTime = () => import(/* webpackChunkName: 'time' */'@/views/system/components/review-time/index');
const ReviewTimeDetail = () => import(/* webpackChunkName: 'time' */'@/views/system/components/review-time/detail');

const routes = [
  {
    path: '/system',
    name: 'system',
    component: system,
    redirect: '/system/awards-info',
    meta: {
      name: '系统管理',
    },
    children: [
      {
        path: 'awards-info',
        name: 'awards-info',
        component: SystemAwardsInfo,
        meta: {
          name: '奖项信息',
        },
      },
      {
        path: 'apply-list',
        name: 'apply-list',
        component: SystemApplyList,
        meta: {
          name: '申报信息',
        },
      },
      {
        path: 'awards-temple',
        name: 'awards-temple',
        component: SystemAwardsTemple,
        meta: {
          name: '奖项策略模版',
        },
      },
      {
        path: 'awards-summary',
        name: 'awards-summary',
        component: SystemSummary,
        meta: {
          name: '奖项沉淀',
        },
      },
      {
        path: 'summary-detail',
        name: 'summary-detail',
        component: SystemSummaryDetail,
        meta: {
          name: '奖项沉淀详情',
          prevMeta: [{
            name: '奖项沉淀',
            path: '/system/awards-summary',
          }],
        },
      },
      {
        path: 'system-time',
        name: 'system-time',
        component: ReviewTime,
        meta: {
          name: '评审时间',
        },
      },
      {
        path: 'systime-detail',
        name: 'systime-detail',
        component: ReviewTimeDetail,
        meta: {
          name: '反馈评审时间',
          prevMeta: [{
            name: '评审时间',
            path: '/system/system-time',
          }],
          id: 'system-time',
        },
      },
      {
        path: 'awards-add',
        name: 'awards-add',
        component: SystemAwardsOperate,
        meta: {
          name: '新增奖项',
        },
      },
      {
        path: 'award-operate',
        name: 'award-operate',
        component: SystemAwardsOperate,
        meta: {
          name: '查看奖项信息',
          prevMeta: [{
            name: '奖项信息',
            path: '/system/awards-info',
          }],
          id: 'awards-info',
        },
      },
      {
        path: 'award-detail',
        name: 'award-detail',
        component: ApplyDetail,
        meta: {
          name: '评审',
          prevMeta: [{
            name: '申报信息',
            path: '/system/apply-list',
          }],
          id: 'apply-list',
        },
      },
      {
        path: 'temple-detail',
        name: 'temple-detail',
        component: TempleDetail,
        meta: {
          name: '策略模板详情',
          prevMeta: [{
            name: '奖项策略模板',
            path: '/system/awards-temple',
          }],
          id: 'awards-temple',
        },
      },
    ],
  },
];

export default routes;
