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
const UserApply = () => import(/* webpackChunkName: 'user' */'@/views/user/index');
const MyDeclare = () => import(/* webpackChunkName: 'declare' */'@/views/user/components/my-apply/index');
const MyReview = () => import(/* webpackChunkName: 'review' */'@/views/user/components/my-review');
const ReviewDetail = () => import(/* webpackChunkName: 'draft' */'@/views/user/components/review-detail');
const ApplyDetail = () => import(/* webpackChunkName: 'draft' */'@/views/user/components/my-apply/apply-detail');
const ApplyPromotional = () => import(/* webpackChunkName: 'draft' */'@/views/user/components/my-apply/apply-promotional');
const ReviewTime = () => import(/* webpackChunkName: 'time' */'@/views/user/components/review-time/index');
const ReviewTimeDetail = () => import(/* webpackChunkName: 'time' */'@/views/user/components/review-time/detail');

const routes = [
  {
    path: '/user-info',
    name: 'user-apply',
    component: UserApply,
    redirect: '/user-info/apply',
    meta: {
      name: '个人中心',
    },
    children: [
      {
        path: 'apply',
        name: 'my-apply',
        component: MyDeclare,
        meta: {
          name: '我的申报',
          requiresAuth: true,
        },
      },
      {
        path: 'review',
        name: 'my-review',
        component: MyReview,
        meta: {
          name: '我的评审',
          requiresAuth: true,
        },
      },
      {
        path: 'time',
        name: 'review-time',
        component: ReviewTime,
        meta: {
          name: '评审时间',
        },
      },
      {
        path: 'time-detail',
        name: 'time-detail',
        component: ReviewTimeDetail,
        meta: {
          name: '反馈评审时间',
          prevMeta: [{
            name: '评审时间',
            path: '/user-info/time',
          }],
          id: 'review-time',
        },
      },
      {
        path: 'review-detail',
        name: 'review-detail',
        component: ReviewDetail,
        meta: {
          name: '评审内容',
          requiresAuth: true,
          prevMeta: [{
            name: '我的评审',
            path: '/user-info/review',
          }],
          id: 'my-review',
        },
      },
      {
        path: 'apply-detail',
        name: 'apply-detail',
        component: ApplyDetail,
        meta: {
          name: '申报信息查看',
          prevMeta: [{
            name: '我的申报',
            path: '/user-info/apply',
          }],
          id: 'my-apply',
        },
      },
      {
        path: 'promotional',
        name: 'promotional',
        component: ApplyPromotional,
        meta: {
          name: '填写奖项沉淀',
          prevMeta: [{
            name: '我的申报',
            path: '/user-info/apply',
          }],
          id: 'my-apply',
        },
      },
    ],
  },
];

export default routes;
