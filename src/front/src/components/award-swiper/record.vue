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
  <section class="award-card">
    <div class="card-name">{{card.name}}</div>
    <div class="card-list" v-for="item in card.list" :key="item.id">
      <span @click="handleGoSummary(item.id, item.year, item.name)">{{item.name}}</span>
    </div>
  </section>
</template>

<script>
export default {
  name: 'Record',
  props: {
    card: Object,
  },
  methods: {
    handleGoSummary(id, year, name) {
      this.$router.push({
        name: 'summary',
        query: { id, year, name },
      });
    },
  },

};
</script>

<style lang="postcss" scoped>
.award-card {
  width: 310px;
  padding-bottom: 8px;
  margin: 0 6px;
  font-size: 16px;
  line-height: 24px;
  background: #fff;
  flex: 0 0 310px;

  .card-name {
    display: flex;
    height: 45px;
    padding-left: 20px;
    margin-bottom: 10px;
    font-size: 20px;
    font-weight: bold;
    border-bottom: 1px solid #989898;
    align-items: center;
  }

  .card-list {
    padding-left: 20px;
    line-height: 24px;
    cursor: pointer;

    &:hover {
      color: #3a84ff;
    }
  }
}

</style>
