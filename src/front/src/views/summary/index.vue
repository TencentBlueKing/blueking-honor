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
  <div class="summary">
    <img class="banner" src="./../../images/summary.jpg">
    <h2 class="title">{{$route.query.year}} {{$route.query.name}}</h2>
    <card v-for="item in list" :key="item.id" :fetch-data="fetchData" :award="item"></card>
  </div>
</template>

<script>
import Card from './card.vue';
export default {
  components: {
    Card,
  },
  data() {
    return {
      list: [],
    };
  },
  created() {
    this.fetchData();
  },
  methods: {
    fetchData() {
      const { year, id } = this.$route.query;
      this.$store.dispatch('award/getAwardSummaries', { year, policy_id: id }).then((res) => {
        const list = res.results || [];
        const yearList = list.filter(item => !item.award); // 年度奖项列表
        const sortList = list.filter(item => item.award).sort((a, b) => a.award.quarter - b.award.quarter);
        this.list = sortList.concat(yearList);
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
.summary {
  width: 1366px;
  margin: 0 auto;

  .banner {
    width: 100%;
  }

  .title {
    text-align: center;
  }
}
</style>
