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
// 获取 OA 登录用户详情
module.exports = async function user(req, res, next) {
  if (req.path !== '/api/v1/user' && req.path !== '/user') {
    next();
    return;
  }
  const request = require('request');
  request(`${window.PROJECT_CONFIG.login_site}/user/get_info?bk_ticket=${req.cookies.bk_ticket}`, (err, response, body) => {
    if (err) {
      return;
    }

    const loginURL = `${window.PROJECT_CONFIG.login_site}/plain?`;

    const data = JSON.parse(body || '{}');

    // 有登录状态
    if (data.ret === 0) {
      const {
        username,
        avatar_url,
      } = data.data;
      res.json({
        code: 0,
        message: data.msg,
        data: {
          username,
          avatar_url,
        },
      });
      return;
    }
    // 登录状态失效
    res.status(401);
    res.set({
      'X-Login-Url': loginURL,
    });
    res.send('');
  });
};
