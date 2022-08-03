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
  <div class="award">
    <div class="award-content" :class="{ 'apply': type === 'apply' }">
      <div class="swiper"
           :class="{ 'transition': isTransition, 'award-content-card': list.length <= 4 }"
           :style="{ transform: `translateX(${imageTransfer}px)` }"
           @transitionend="transitionend">
        <component
          :is="type"
          v-for="(card, index) in dataList"
          :key="index"
          :card="card">
        </component>
        <div
          v-if="type === 'record' && isRecordFetched && !dataList.length">
          更多精彩奖项沉淀事迹，敬请期待
        </div>
      </div>
    </div>
    <template v-if="list.length > 4">
      <span class="swiper-nav nav-prev" @click="changeIndex(currentIndex - 1)">
        <i class="swiper-nav-icon"></i>
      </span>
      <span class="swiper-nav nav-next" @click="changeIndex(currentIndex + 1)">
        <i class="swiper-nav-icon"></i>
      </span>
    </template>
  </div>
</template>

<script>
import Apply from './apply.vue';
import Record from './record.vue';

export default {
  components: {
    Apply,
    Record,
  },
  props: {
    type: String,
    list: Array,
    isRecordFetched: Boolean,
  },
  data() {
    return {
      realWidth: 322,
      currentIndex: 4,
      isTransition: this.list.length > 4,
      isChanged: true,
    };
  },
  computed: {
    dataList() {
      const first = this.list.slice(0, 4);
      const last = this.list.slice(-4);
      return this.list.length > 4 ? [...last, ...this.list, ...first] : this.list;
    },
    imageTransfer() {
      const indexMove = this.realWidth * this.currentIndex;
      return this.list.length > 4 ? -indexMove : 0;
    },
  },
  methods: {
    changeIndex(index) {
      if (!this.isChanged) return;
      this.isTransition = true;
      this.isChanged = false;
      this.currentIndex = index;
    },
    transitionend() {
      this.isChanged = true;
      const picLength = this.dataList.length;
      if (this.currentIndex <= 0) {
        this.isTransition = false;
        this.currentIndex = picLength - 8;
      } else if (this.currentIndex >= picLength - 4) {
        this.isTransition = false;
        this.currentIndex = 4;
      }
    },
  },
};
</script>

<style lang="postcss" scoped>
.award {
  position: relative;
}

.award-content {
  position: relative;
  top: -160px;
  max-width: 1288px;
  margin: 0 auto;
  overflow: hidden;

  &.apply {
    height: 220px;
  }

  .swiper {
    display: flex;

    &.transition {
      transition: .5s ease-in-out;
    }
  }

  .award-content-card {
    display: flex;
    justify-content: center;
  }
}

.swiper-nav {
  position: absolute;
  top: -65px;
  display: block;
  width: 42px;
  height: 42px;
  cursor: pointer;
  background: #4c4c4c;
  border-radius: 50%;

  .swiper-nav-icon {
    position: absolute;
    top: 9px;
    left: 13px;
    width: 20px;
    height: 20px;
    border-bottom: 2px solid #fff;
    border-left: 2px solid #fff;
  }

  &:hover {
    background: #fff;

    .swiper-nav-icon {
      border-color: #000;
    }
  }

  &.nav-prev {
    left: calc(50% - 690px);
    transform: rotate(45deg);
  }

  &.nav-next {
    right: calc(50% - 690px);
    transform: rotate(225deg);
  }
}
</style>
