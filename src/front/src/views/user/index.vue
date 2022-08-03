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
import Nav from '@/views/mixins/common/nav';
export default {
  name: 'User',
  mixins: [Nav],
  data() {
    return {
      componentList: [
        { id: 'my-apply', name: '我的申报', path: '/user/apply' },
        { id: 'my-review', name: '我的审批/评审',  path: '/user/review' },
        { id: 'review-time', name: '评审时间',  path: '/user/time' },
      ],
    };
  },
  computed: {
  },
  methods: {
  },
};
</script>

<style lang="postcss" scoped>
.container {
  display: flex;
  width: 90%;
  min-width: 1680px;
  margin: 35px auto 0;
  justify-content: center;

  .left,
  .left {
    width: 250px;
    height: calc(100vh - 205px);
    min-width: 220px;
    min-height: 690px;
    background: #fff;
    border-radius: 15px;

    .user {
      text-align: center;
      border-bottom: 1px solid #e7e7e7;

      .username {
        margin: 10px auto 30px;
        color: #ccc;
      }

      .avatar {
        width: 120px;
        height: 120px;
        margin: 30px auto 0;
        border-radius: 50%;
      }
    }

    .nav {
      :hover {
        background: #f6f6f9;
      }

      a {
        display: block;
        height: 50px;
        line-height: 50px;
        text-align: center;
        border-bottom: 1px solid #e7e7e7;
      }

      li {
        display: block;
        height: 70px;
        line-height: 70px;
        text-align: center;
        border-bottom: 2px solid #e7e7e7;

        &:first-child {
          border-top: 2px solid #e7e7e7;
        }
      }
    }

    .is-active {
      background: #e1ecff !important;

      .path-name {
        color: #3a84ff;
        background: #e1ecff !important;
      }
    }
  }


  .path-name {
    color: #63656e;
  }

  .right-content {
    height: calc(100vh - 205px);
    min-height: 690px;
    margin-left: 30px;
    background: #fff;
    border-radius: 15px;
    flex: 1;

    .bread-crumbs {
      margin: 15px;
    }

    .dividing-line {
      height: 1px;
      background-color: #e7e7e7;
    }
  }
}
</style>
