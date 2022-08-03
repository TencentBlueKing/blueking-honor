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
  <div class="page-index">
    <div class="swiper">
      <bk-swiper :pics="pics" :loop-time="5000"></bk-swiper>
    </div>
    <award-swiper type="apply" :list="applyList"></award-swiper>
    <div class="swiper-divide"></div>
    <award-swiper type="record" :list="recordList" :is-record-fetched="isRecordFetched"></award-swiper>
  </div>
</template>

<script>
import AwardSwiper from '@/components/award-swiper';

export default {
  components: {
    AwardSwiper,
  },
  data() {
    return {
      applyList: [],
      recordList: [],
      isRecordFetched: false,
      pics: [{}], // 轮播图
    };
  },
  created() {
    this.$store.dispatch('award/getIndexAwards', { page_size: 100 }).then((res) => {
      const list = res?.awards || [];

      this.pics = list.reduce((prev, next) => {
        const { url } = next.award_slideshow[0] || {};
        const { id, status } = next;
        const link = this.$router.resolve({
          name: 'apply',
          query: { id },
        }).href;
        if (status === 'started' && url) {
          const item = { url, link };
          return prev.concat(item);
        }
        return prev;
      }, []);

      const statusMap = {
        started: 1,
        pending: 2,
        unapplicable: 3,
        expired: 4,
      };
      this.applyList = list.sort((a, b) => statusMap[a.status] - statusMap[b.status]);
    });
    this.$store.dispatch('award/getIndexSummaries', { page_size: 100 }).then((res) => {
      const list = res?.summaries || [];
      const recordList = list.reduce(
        (prev, cur) => {
          const year = cur?.year;
          if (prev.find(item => item.id === year)) {
            prev.find(item => item.id === year).list.push(cur);
            return prev;
          }
          const record = {
            id: year,
            name: `${year}奖项回顾`,
            list: [cur],
          };
          return prev.concat(record);
        },
        [],
      );
      this.recordList = recordList.sort((a, b) => a.id - b.id);
      this.isRecordFetched = true;
    });
  },
};
</script>

<style lang="postcss" scoped>
.page-index {
  margin-bottom: -50px;
}

.swiper {
  display: flex;
  width: 100%;
  height: 680px;
}

.swiper-divide {
  height: 60px;
}

>>> .bk-swiper-index {
  bottom: 180px;
}
</style>
