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
  <div class="container">
    <div class="left">
      <div class="user">
        <img :src="getAvatarUrl()" class="avatar">
        <p class="username">{{user.username}}</p>
      </div>
      <div class="nav" v-for="item in componentList" :key="item.id">
        <router-link :to="{ name: item.id }"
                     :class="{ 'is-active': $route.name === item.id || ($route.meta.id === item.id) }" :name="item.id">
          <span class="path-name">{{item.name}}</span>
        </router-link>
      </div>
    </div>
    <div class="right-content">
      <!-- 面包屑 -->
      <div class="bread-crumbs">
        <bk-breadcrumb>
          <!-- :to="item.path" -->
          <bk-breadcrumb-item
            v-for="(item, index) in routeMatched"
            :key="index"
          >{{ item.name }}</bk-breadcrumb-item>
        </bk-breadcrumb>
      </div>

      <div class="dividing-line"></div>

      <div>
        <router-view></router-view>
      </div>

    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';
export default {
  name: 'LeftNav',
  data() {
    return {
      list: this.$store.state.user.breadcrumbList || [],
      componentList: [],
      breadCrumbsList: Object.assign([], this.$route.matched),
    };
  },
  computed: {
    ...mapGetters(['user']),
    routeMatched() {
      const breadCrumbsList = this.breadCrumbsList.reduce((p, v) => {
        if (v.meta && v.meta.prevMeta) {
          v.meta.prevMeta.forEach((e) => {
            p.push({
              name: e.name,
              path: e.path,
            });
          });
        }
        p.push({
          name: v.meta.name,
          path: v.path,
        });
        return p;
      }, []);
      return breadCrumbsList;
    },
  },
  methods: {
    getAvatarUrl() {
      return `${window.PROJECT_CONFIG.avatar_site}/${this.user.username}/avatar.jpg`;
    },
  },
};
</script>
