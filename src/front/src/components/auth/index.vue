<!--
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
-->
<script>
export default {
  data() {
    return {
      isShow: false,
      loginWindow: null,
      checkWindowTimer: -1,
    };
  },
  created() {
    window.addEventListener('message', this.messageListener, false);
  },
  beforeDestroy() {
    window.removeEventListener('message', this.messageListener, false);
  },
  methods: {
    showLoginModal(data = {}) {
      if (this.isShow) return;
      this.isShow = true;
      let url = data.login_url;
      if (!url) {
        const callbackUrl = `${location.origin}/static/login_success.html?is_ajax=1`;
        url = `${window.PROJECT_CONFIG.login_site}/plain?size=big&c_url=${callbackUrl}`;
      }
      const width = 700;
      const height = 510;
      const { availHeight, availWidth } = window.screen;
      this.loginWindow = window.open(url, '_blank', `
        width=${width},
        height=${height},
        left=${(availWidth - width) / 2},
        top=${(availHeight - height) / 2},
        channelmode=0,
        directories=0,
        fullscreen=0,
        location=0,
        menubar=0,
        resizable=0,
        scrollbars=0,
        status=0,
        titlebar=0,
        toolbar=0,
        close=0
      `);
      this.checkWinClose();
    },
    checkWinClose() {
      this.checkWindowTimer && clearTimeout(this.checkWindowTimer);
      this.checkWindowTimer = setTimeout(() => {
        if (!this.loginWindow || this.loginWindow.closed) {
          this.hideLoginModal();
          clearTimeout(this.checkWindowTimer);
          return;
        }
        this.checkWinClose();
      }, 300);
    },
    messageListener({ data = {} }) {
      if (data === null || typeof data !== 'object' || data.target !== 'bk-login' || !this.loginWindow) return;

      this.hideLoginModal();
    },
    hideLoginModal() {
      this.isShow = false;
      if (this.loginWindow) {
        this.loginWindow.close();
      }
      this.loginWindow = null;
    },
  },
  render() {
    return '';
  },
};
</script>
