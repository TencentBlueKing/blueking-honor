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
import pytest

from bk_honor.awards.models.managers import AvailablePeriodManager


class TestApprovalTimeSpanManager:
    @pytest.mark.parametrize(
        "sample,expected",
        [
            (
                [
                    {"started_at": "1", "ended_at": "3"},
                    {"started_at": "2", "ended_at": "4"},
                ],
                ((1, 4),),
            ),
            (
                [
                    {"started_at": "1", "ended_at": "2"},
                    {"started_at": "4", "ended_at": "6"},
                    {"started_at": "5", "ended_at": "6"},
                    {"started_at": "5", "ended_at": "7"},
                    {"started_at": "6", "ended_at": "7"},
                    {"started_at": "8", "ended_at": "9"},
                ],
                ((1, 2), (4, 7), (8, 9)),
            ),
            # 模拟倒序
            pytest.param(
                [
                    {"started_at": "9", "ended_at": "2"},
                ],
                ((1, 2),),
                marks=pytest.mark.xfail(raises=ValueError),
            ),
        ],
    )
    def test_merge(self, sample, expected):
        for index, interval in enumerate(AvailablePeriodManager._merge_periods(sample)):
            assert (interval.begin, interval.end) == expected[index - 1]

    class FakePeriod:
        class FakeTimeField:
            def __init__(self, value):
                self.value = value

            def timestamp(self):
                return self.value

            def __str__(self):
                return self.value

            def __repr__(self):
                return self.value

        def __init__(self, started_at, ended_at):
            self.started_at = self.FakeTimeField(started_at)
            self.ended_at = self.FakeTimeField(ended_at)

        def __str__(self):
            return f"Period({self.started_at},{self.ended_at})"

        def __repr__(self):
            return str(self)

    @pytest.mark.parametrize(
        "samples,expected",
        [
            (
                (("", [FakePeriod("1", "2")]), ("", [FakePeriod("3", "4")])),
                (),
            ),
            (
                (("", [FakePeriod("2", "5")]), ("", [FakePeriod("1", "3")])),
                ((2, 3),),
            ),
            (
                (
                    ("", [FakePeriod("1", "2"), FakePeriod("4", "6"), FakePeriod("7", "9"), FakePeriod("10", "13")]),
                    ("", [FakePeriod("3", "4"), FakePeriod("5", "6"), FakePeriod("7", "8"), FakePeriod("9", "12")]),
                ),
                ((5, 6), (7, 8), (10, 12)),
            ),
            (
                (
                    ("foo", [FakePeriod("1653897600", "1654675199")]),
                    ("bar", [FakePeriod("1653897600", "1656489599")]),
                ),
                ((1653897600, 1654675199),),
            ),
        ],
    )
    def test_get_intersection(self, samples, expected):
        assert len(AvailablePeriodManager._intersection_periods(samples)) == len(expected)
        for index, interval in enumerate(AvailablePeriodManager._intersection_periods(samples)):
            assert (interval.begin, interval.end) == expected[index - 1]
