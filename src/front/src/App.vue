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
<template>
  <div id="app">
    <nav class="navigation-header">
      <div class="header-title pl50" @click="$router.push({ name: 'index' })">
        <img class="title-img" :src="honorImages" />
        <span class="title-txt">
          荣誉激励
        </span>
      </div>
      <div class="header-search">
        <bk-icon type="search" />
        <input
          class="search-input"
          v-model="searchValue"
          @focus="handleFocus"
          :placeholder="'搜索奖项申报和奖项沉淀'"
          :left-icon="'bk-icon icon-search'" />
        <bk-icon v-if="searchValue.length" @click="searchValue = ''" type="close-circle-shape" />
        <div class="search-list"
             v-if="searchVisable"
             v-bk-clickoutside="handleClickOutside">
          <ul v-bkloading="{ isLoading: searchLoading }">
            <li>
              <div class="group-name">申报</div>
              <ul v-if="awardList.length">
                <li class="list-item"
                    v-for="item in awardList"
                    :key="item.id"
                    @click="handleGoApply(item.id)">
                  {{item.name}}
                </li>
              </ul>
              <div v-else class="list-empty">无匹配数据</div>
            </li>
            <li>
              <div class="group-name">沉淀</div>
              <ul v-if="summaryList.length">
                <li class="list-item"
                    v-for="item in summaryList"
                    :key="item.id"
                    @click="handleGoSummary(item.id, item.year, item.name)">
                  {{item.fullName}}
                </li>
              </ul>
              <div v-else class="list-empty">无匹配数据</div>
            </li>
          </ul>
        </div>
      </div>
      <div class="header-nav pr40">
        <span class="header-admin pr50"
              v-if="user.system_role === 'admin'" @click="$router.push({ name: 'system' })">系统管理</span>
        <span class="header-user"
              @mouseover="showUserList = true"
              @mouseleave="showUserList = false">
          <img :src="getAvatarUrl()" class="avatar">
          <span>{{user.username}}</span>
          <i class="bk-icon icon-angle-down f24"></i>
          <div class="user-list" v-show="showUserList">
            <ul>
              <li class="user-list-item" @click="$router.push({ name: 'user-apply' })">个人中心</li>
              <li class="user-list-item" @click="$router.push({ name: 'records' })">获奖记录</li>
              <li class="user-list-item-divider"><bk-divider></bk-divider></li>
              <li class="user-list-item user-exit" @click="logout">退出</li>
            </ul>
          </div>
        </span>
      </div>
    </nav>
    <div class="navigation-content">
      <main class="main-content">
        <router-view :key="$route.fullPath" v-show="!mainContentLoading" />
      </main>
    </div>
    <div class="navigation-footer">
      Copyright © 2012-{{curYear}} Tencent BlueKing. All Rights Reserved. 腾讯蓝鲸 版权所有
    </div>
    <app-auth ref="bkAuth"></app-auth>
  </div>
</template>
<script>
import { mapGetters } from 'vuex';

import honorImages from './images/honor.png';

import { bus } from '@/common/bus';

export default {
  name: 'App',
  components: {
  },
  data() {
    return {
      honorImages,
      showUserList: false,
      searchValue: '',
      searchTimeout: null,
      awardList: [],
      summaryList: [],
      searchVisable: false,
      searchLoading: false,
    };
  },
  computed: {
    ...mapGetters(['mainContentLoading', 'user']),
    curYear() {
      return (new Date()).getFullYear();
    },
  },
  watch: {
    searchValue(newVal, oldVal) {
      this.searchLoading = true;
      this.handleDebounce(newVal);
    },
  },
  created() {
    this.handleSearch();
  },
  mounted() {
    bus.$on('show-login-modal', (data) => {
      this.$refs.bkAuth.showLoginModal(data);
    });
    bus.$on('close-login-modal', () => {
      this.$refs.bkAuth.hideLoginModal();
      setTimeout(() => {
        window.location.reload();
      }, 0);
    });
  },
  methods: {
    logout() {
      this.$store.dispatch('logout').then(() => {
        window.location = `${window.PROJECT_CONFIG.login_site}/?c_url=${window.location.href}`;
      });
    },
    handleClickOutside(e) {
      if (!document.querySelector('.header-search').contains(e.target)) {
        this.searchVisable = false;
        document.querySelector('.search-input').blur();
      }
    },
    handleDebounce(value) {
      if (this.searchTimeout) {
        clearTimeout(this.searchTimeout);
      }
      this.searchTimeout = setTimeout(() => {
        this.searchVisable = true;
        this.handleSearch(value.trim());
      }, 500);
    },
    handleSearch(value) {
      const params = {
        keyword: value,
        page: 1,
        page_size: 100,
      };
      this.$store.dispatch('award/getSearchList', params).then((res) => {
        this.awardList = res.search_data.awards || [];
        this.summaryList = res.search_data.summaries || [];
        this.searchLoading = false;
      });
    },
    handleGoApply(id) {
      this.searchVisable = false;
      this.$router.push({
        name: 'apply',
        query: { id },
      });
    },
    handleGoSummary(id, year, name) {
      this.searchVisable = false;
      this.$router.push({
        name: 'summary',
        query: { id, year, name },
      });
    },
    handleFocus() {
      this.searchVisable = true;
      this.handleSearch();
    },
    getAvatarUrl() {
      return `${window.PROJECT_CONFIG.avatar_site}/${this.user.username}/avatar.jpg`;
    },
  },
};
</script>

<style lang="postcss">
  @import './css/reset.css';
  @import './css/app.css';

  body {
    min-width: 1366px;
    background: #e7e7e7;
  }
</style>

<style lang="postcss" scoped>

  .navigation-header {
    position: fixed;
    z-index: 2;
    display: flex;
    width: 100%;
    height: 69px;
    min-width: 1366px;
    line-height: 69px;
    color: #fff;
    background: #343434;
    justify-content: space-between;
    align-items: center;

    .header-title {
      display: flex;
      cursor: pointer;
    }

    .title-img {
      position: relative;
      top: 5px;
      height: 32px;
    }

    .title-txt {
      padding-left: 20px;
      line-height: 32px;
    }

    .header-search {
      position: relative;

      .bk-icon {
        position: absolute;
        top: 29px;
        color: #c4c6cc;
      }

      .icon-search {
        left: 10px;
      }

      .icon-close-circle-shape {
        right: 10px;
        cursor: pointer;
      }

      .search-input {
        width: 615px;
        height: 36px;
        padding: 0 30px;
        font-size: 14px;
        line-height: normal;
        color: #63656e;
        text-align: left;
        vertical-align: middle;
        background-color: #fff;
        border: 1px solid #c4c6cc;
        border-radius: 36px;
        outline: none;
        box-sizing: border-box;
        resize: none;

        &::input-placeholder {
          color: #c3cdd7;
        }
      }
    }

    .avatar {
      width: 33px;
      height: 33px;
      margin-right: 5px;
      vertical-align: middle;
      border-radius: 50%;
    }

    .header-admin {
      cursor: pointer;

      &:hover {
        color: #699df4;
      }
    }

    .header-user {
      position: relative;
      display: inline-block;
      height: 69px;
      cursor: pointer;
    }

    .user-list {
      position: absolute;
      top: 69px;
      right: 0;
      width: 132px;
      padding: 10px 20px;
      color: #000;
      text-align: center;
      background: #fff;
      border: 1px solid #dde4eb;
      border-radius: 2px;
      box-shadow: 0 3px 6px rgb(51 60 72 / 12%);

      .user-list-item {
        line-height: 32px;
        cursor: pointer;

        &:hover {
          color: #699df4;
        }
      }

      .user-list-item-divider {
        font-size: 6px;
      }
    }
  }

  .main-content {
    min-height: 300px;
  }

  .navigation-content {
    min-height: calc(100vh - 100px);
    padding-top: 69px;

    /* background: #FFFFFF; */

    /* box-shadow: 0px 2px 4px 0px rgba(25,25,41,0.05); */

    /* border-radius: 2px; */

    /* border: 1px solid rgba(220,222,229,1); */
  }

  .navigation-footer {
    display: flex;
    width: 100%;
    height: 52px;
    margin: 32px 0 0 ;
    font-size: 12px;
    color: #63656e;
    border-top: 1px solid #dcdee5;
    align-items: center;
    justify-content: center;
  }

  .search-list {
    position: absolute;
    width: 615px;
    max-height: 320px;
    padding-bottom: 10px;
    overflow: auto;
    font-size: 14px;
    color: #63656e;
    background: #fff;
    border: 1px solid #dcdee5;
    box-shadow: 0 3px 9px 0 rgb(0 0 0 / 10%);

    .group-name,
    .list-empty {
      height: 32px;
      margin: 0 20px;
      line-height: 32px;
      color: #979ba5;
      border-bottom: 1px solid #dcdee5;
    }

    .list-empty {
      text-align: center;
      border-bottom: none;
    }

    .list-item {
      height: 32px;
      padding: 0 40px;
      line-height: 32px;
      cursor: pointer;

      &.is-selected {
        color: #3a84ff;
        background-color: #f4f6fa;
      }

      &:hover {
        color: #3a84ff;
        background-color: #eaf3ff;
      }
    }
  }
</style>
