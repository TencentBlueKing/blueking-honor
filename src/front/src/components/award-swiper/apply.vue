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
    <div class="award-content">
      <div>奖项名：{{card.name}}</div>
      <div>周期：{{card.year}} Q{{card.quarter}}</div>
      <div>类别：{{card.policy.name}}</div>
      <div>截止时间：{{card.ended_at | formatDate('date')}}</div>
    </div>
    <div class="award-apply" v-if="card.status === 'started'" @click="handleApply">申报</div>
    <div class="award-apply disabled">{{STATUS_ENUM[card.status]}}</div>
  </section>
</template>

<script>
import { STATUS_ENUM } from '@/common/constants';
export default {
  name: 'Apply',
  props: {
    card: Object,
  },
  data() {
    return {
      STATUS_ENUM,
    };
  },
  methods: {
    handleApply() {
      this.$router.push({
        name: 'apply',
        query: {
          id: this.card.id,
        },
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
.award-card {
  width: 310px;
  height: 220px;
  margin: 0 6px;
  font-size: 14px;
  line-height: 24px;
  color: #fff;
  background: #3b3e5e;
  flex: 0 0 310px;

  .award-content {
    height: 160px;
    padding: 32px 20px;
    background: url('./../../images/spark.png') right top no-repeat;
  }

  .award-apply {
    display: flex;
    height: 60px;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    background: #3a84ff;
    justify-content: center;
    align-items: center;

    &:hover {
      background: #699df4;
    }

    &.disabled {
      cursor: not-allowed;
      background: #979ba5;
    }
  }
}

</style>
