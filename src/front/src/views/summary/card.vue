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
  <div class="card">
    <div class="left">
      <div class="content" :class="{ 'more': showMore }">
        <p class="header">{{award.award ? award.award.name : `${award.year}年度${$route.query.name}`}}</p>
        <p class="team">{{award.details.material_title}}</p>
        <p class="team">{{award.details.winning_team_name}}</p>
        <p class="detail">
          <b>事迹介绍：</b>{{award.details.deeds_introduction}}
        </p>
        <p class="member">
          <b>团队成员：</b>
          <span
            v-for="item in award.details.team_members"
            class="user"
            :key="item"
            @click="handleGoRecord(item)">
            {{item}};
          </span>
        </p>
      </div>
      <p @click="showMore = !showMore" class="show-more">
        {{ showMore ? '收起' : '查看全部'}}
        <bk-icon class="f18" :type="showMore ? 'angle-up' : 'angle-down'" />
      </p>
      <p class="pt10">
        <bk-button @click="handleLike" :class="{ 'active': award.liked }">点赞 {{award.like_count || ''}}</bk-button>
      </p>
    </div>
    <div class="right">
      <img class="image" :src="award.details.upload[0].url">
    </div>
  </div>
</template>

<script>
export default {
  props: {
    award: Object,
    fetchData: Function,
  },
  data() {
    return {
      showMore: false,
      isActive: true,
    };
  },
  methods: {
    handleLike() {
      const params = { ...this.award,
        liked: !this.award.liked,
      };
      this.$store.dispatch('award/likeAward', params).then((res) => {
        this.$bkMessage({ theme: 'success', message: `${this.award.liked ? '取消' : ''}点赞成功` });
        this.fetchData();
      });
    },
    handleGoRecord(name) {
      this.$router.push({
        name: 'records',
        query: {
          user: name,
        },
      });
    },
  },
};
</script>

<style lang="postcss" scoped>
.card {
  padding: 50px;
  margin: 10px 0;
  background: #fff;
  border-radius: 10px;

  .left,
  .right {
    display: inline-block;
  }

  .left {
    width: 60%;
    padding-right: 30px;
    font-size: 14px;
    vertical-align: top;

    .header,
    .team {
      font-size: 18px;
      font-weight: bold;
      line-height: 32px;
    }

    .header {
      color: #e2cd8b;
    }

    .content {
      max-height: 233px;
      min-height: 233px;
      overflow: hidden;
      line-height: 24px;

      &.more {
        max-height: none;
        overflow: auto;
      }
    }

    .member {
      word-break: break-word;

      .user {
        cursor: pointer;

        &:hover {
          color: #699df4;
        }
      }
    }

    .show-more {
      padding: 10px;
      text-align: right;
      cursor: pointer;

      &:hover {
        color: #699df4;
      }
    }

    .active {
      color: #3a84ff;
      border-color: #3a84ff;
    }
  }

  .right {
    width: 39%;

    .image {
      width: 520px;
      height: 320px;
    }
  }
}

</style>
