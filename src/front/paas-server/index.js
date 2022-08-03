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
 * @file prod server
 * 静态资源
 * 模块渲染输出
 * 注入全局变量
 * 添加html模板引擎
 */
const Express = require('express');
const path = require('path');
const artTemplate = require('express-art-template');
const cookieParser = require('cookie-parser');
const history = require('connect-history-api-fallback');
const user = require('./middleware/user');


const mockTable = require('./api/table');

const app = new Express();

const PORT = process.env.PORT || 5000;

/** 仅解决空模版直接部署时，模拟的接口，防止直接部署接口404，实际项目可删除 */
mockTable(app);

app.use(cookieParser());
app.use(user);

// 注入全局变量
const GLOBAL_VAR = {
  SITE_URL: process.env.SITE_URL || '',
  BK_STATIC_URL: process.env.BK_STATIC_URL || '',
  // 当前应用的环境，预发布环境为 stag，正式环境为 prod
  BKPAAS_ENVIRONMENT: process.env.BKPAAS_ENVIRONMENT || '',
  // EngineApp名称，拼接规则：bkapp-{appcode}-{BKPAAS_ENVIRONMENT}
  BKPAAS_ENGINE_APP_NAME: process.env.BKPAAS_ENGINE_APP_NAME || '',
  // 内部版对应ieod，外部版对应tencent，混合云版对应clouds
  BKPAAS_ENGINE_REGION: process.env.BKPAAS_ENGINE_REGION || '',
  // APP CODE
  BKPAAS_APP_ID: process.env.BKPAAS_APP_ID || '',
};

const distDir = path.resolve(__dirname, '../dist');

app.use(history({
  index: '/',
  rewrites: [
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 /cs/28aa9eda67644a6eb254d694d944307e/cluster/BCS-MESOS-10001/node/10.121.23.12 这样以 IP 结尾的 url
      // from: /\d+\.\d+\.\d+\.\d+$/,
      from: /\/(\d+\.)*\d+$/,
      to: '/',
    },
    {
      // connect-history-api-fallback 默认会对 url 中有 . 的 url 当成静态资源处理而不是当成页面地址来处理
      // 兼容 下面带有.路径
      // /bcs/projectId/app/214/taskgroups/0.application-1-13.test123.10013.1510806131114508229/containers/containerId
      from: /\/\/+.*\..*\//,
      to: '/',
    },
    {
      from: '/api/user',
      to: '/user',
    },
    {
      from: '/user',
      to: '/user',
    },
  ],
}));


// 首页
app.get('/', (req, res) => {
  const scriptName = (req.headers['x-script-name'] || '').replace(/\//g, '');
  // 使用子路径
  if (scriptName) {
    GLOBAL_VAR.BK_STATIC_URL = `/${scriptName}`;
    GLOBAL_VAR.SITE_URL = `/${scriptName}`;
  } else {
    // 使用系统分配域名
    GLOBAL_VAR.BK_STATIC_URL = '';
    GLOBAL_VAR.SITE_URL = '';
  }
  // 注入全局变量
  res.render(path.join(distDir, 'index.html'), GLOBAL_VAR);
});


app.use('/static', Express.static(path.join(distDir, '../dist/static')));
// 配置视图
app.set('views', path.join(__dirname, '../dist'));

// 配置模板引擎
// http://aui.github.io/art-template/zh-cn/docs/
app.engine('html', artTemplate);
app.set('view engine', 'html');

// 配置端口
app.listen(PORT, () => {
  console.log(`App is running in port ${PORT}`);
});


