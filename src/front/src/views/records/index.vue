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
  <div class="record">
    <section class="pt20" v-for="record in recordList" :key="record.level">
      <p class="honor">{{record.levelName}}荣誉</p>
      <p class="number">
        {{userName || user.username}}已获得{{record.levelName}}荣誉{{(record.list && record.list.length) || 0}}个
      </p>
      <div class="content" v-for="item in record.list || []" :key="item.id">
        <div @click="handleImage(item)" class="award-card small">
          <p>尊敬的
            <span class="user">{{userName || item.english_name}}</span>
            <span v-if="item.chinese_name">({{item.chinese_name}})</span>
          </p>
          <p>感谢您</p>
          <p>为{{item.project_name}}项目</p>
          <p>做出的杰出贡献</p>
          <p>特此授予</p>
          <p class="year">{{item.year}}{{item.quarter ? `年 Q${item.quarter}` : '年度'}}</p>
          <p class="award">{{item.name}}</p>
        </div>
      </div>
    </section>

    <bk-dialog
      v-model="dialogVisible"
      theme="primary"
      width="520"
      :show-footer="false">
      <div class="award-card">
        <p>尊敬的
          <span class="user">{{userName || award.english_name}}</span>
          <span v-if="award.chinese_name">({{award.chinese_name}})</span>
        </p>
        <p>感谢您</p>
        <p>为{{award.project_name}}项目</p>
        <p>做出的杰出贡献</p>
        <p>特此授予</p>
        <p class="year">{{award.year}}{{award.quarter ? `年 Q${award.quarter}` : '年度'}}</p>
        <p class="award">{{award.name}}</p>
      </div>
    </bk-dialog>
  </div>
</template>

<script>
import { mapGetters } from 'vuex';

import { LEVEL_ENUM } from '@/common/constants';

export default {
  data() {
    return {
      recordList: [{}],
      dialogVisible: false,
      award: {},
      userName: this.$route.query.user,
    };
  },
  computed: {
    ...mapGetters(['mainContentLoading', 'user']),
  },
  created() {
    this.$store.dispatch('award/getAwardRecords', { username: this.userName }).then((res) => {
      this.handleList(res?.results);
    });
  },
  methods: {
    handleList(list = []) {
      const defaultList = Object.keys(LEVEL_ENUM).map(item => ({
        level: item,
        levelName: LEVEL_ENUM[item],
        list: [],
      }));
      const recordList = list.reduce((prev, cur) => {
        const { level } = cur;
        prev.find(item => item.level === level).list.push(cur);
        return prev;
      }, defaultList);
      this.recordList = list.length ? recordList : defaultList;
    },
    handleImage(award) {
      this.dialogVisible = true;
      this.award = award;
    },
  },
};
</script>

<style lang="postcss" scoped>
.record {
  width: 80%;
  min-height: calc(100vh - 153px);
  padding: 10px 50px;
  margin: 0 auto;
  background: #fff;

  .honor {
    position: relative;
    font-size: 16px;
    line-height: 32px;
    border-bottom: 1px solid #dcdee5;

    &::after {
      position: absolute;
      bottom: 0;
      left: 0;
      width: 90px;
      height: 2px;
      background: #3a84ff;
      content: '';
    }
  }

  .number {
    padding: 20px 0;
    font-size: 14px;
  }

  .content {
    display: inline-block;
    width: 237px;
    height: 304px;
    margin-right: 15px;
    margin-bottom: 15px;
    vertical-align: top;
    cursor: pointer;
  }
}

.award-card {
  width: 474px;
  height: 608px;
  padding: 150px 40px;
  font-size: 16px;
  font-weight: bold;
  line-height: 46px;
  text-align: center;
  background: url('./../../images/award.jpg') no-repeat;
  background-size: cover;

  .user {
    text-transform: capitalize;
  }

  .year,
  .award {
    font-size: 20px;
    color: #ab7916;
  }

  &.small {
    transform: scale(.5) translate(-50%, -50%);
  }
}

</style>
