"""
Tencent is pleased to support the open source community by making 蓝鲸智云PaaS平台社区版 (BlueKing PaaS Community
Edition) available.
Copyright (C) 2017-2021 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at
http://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
from intervaltree import Interval, IntervalTree


class EnhancedIntervalTree(IntervalTree):
    """加强版区间树"""

    @classmethod
    def from_tuples(cls, tups):
        """
        Create a new IntervalTree from an iterable of 2- or 3-tuples,
         where the tuple lists begin, end, and optionally data.
        """
        ivs = [Interval(*t) for t in tups]
        return cls(ivs)

    def intersection_split(self, begin, end) -> 'EnhancedIntervalTree':
        """
        将区间树中的重叠区间拆分成多个区间树
        """
        ivs = set()

        for iv in sorted(self, key=lambda x: x.begin):
            if iv.begin <= begin:
                if iv.end <= begin:
                    continue

                if iv.end >= end:
                    ivs.add(Interval(begin, end))
                    continue

                ivs.add(Interval(begin, iv.end))
            else:
                if iv.begin >= end:
                    continue

                if iv.end >= end:
                    ivs.add(Interval(iv.begin, end))
                    continue

                ivs.add(Interval(iv.begin, iv.end))

        return EnhancedIntervalTree(ivs)

    def range_intersection(self, other: 'EnhancedIntervalTree') -> 'EnhancedIntervalTree':
        """
        计算两个区间树的交集
        交集树计算前需要保证两个区间树的区间均为升序排列，且进行过 merge_overlapping 操作
        """
        ivs: set = set()
        for iv in self:
            overlaps = EnhancedIntervalTree(other.overlap(iv.begin, iv.end))
            intersection = overlaps.intersection_split(iv.begin, iv.end)

            ivs = ivs.union(intersection)

        return EnhancedIntervalTree(ivs)
