/*
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
*/
/**
 * @file 按需引入 bk-magic-vue 组件
 * @author
 */

/* eslint-disable import/no-duplicates */

import {
  bkAnimateNumber,
  bkBadge, bkButton, bkCard,
  bkCheckbox, bkCheckboxGroup, bkClickoutside, bkCol, bkCollapse, bkCollapseItem, bkColorPicker, bkContainer,
  bkDatePicker, bkDialog, bkDropdownMenu, bkException, bkForm,
  bkFormItem, bkInfoBox, bkInput, bkLoading, bkMemberSelector, bkMessage, bkNavigation, bkNavigationMenu,
  bkNavigationMenuItem, bkNotify, bkOption, bkOptionGroup, bkPagination, bkPopconfirm,
  bkPopover, bkProcess, bkProgress, bkRadio, bkRadioGroup, bkRate, bkRoundProgress, bkRow, bkSearchSelect, bkSelect,
  bkSideslider, bkSlider, bkSteps, bkSwiper, bkSwitcher, bkTab, bkTable, bkTableColumn, bkTabPanel, bkTagInput,
  bkTimeline,   bkTimePicker, bkTooltips, bkTransfer, bkTree,
  bkUpload,   bkVirtualScroll } from 'bk-magic-vue';
import Vue from 'vue';

// bkDiff 组件体积较大且不是很常用，因此注释掉。如果需要，打开注释即可
// import { bkDiff } from 'bk-magic-vue'

// components use
Vue.use(bkBadge);
Vue.use(bkButton);
Vue.use(bkCheckbox);
Vue.use(bkCheckboxGroup);
Vue.use(bkCol);
Vue.use(bkCollapse);
Vue.use(bkCollapseItem);
Vue.use(bkContainer);
Vue.use(bkDatePicker);
Vue.use(bkDialog);
Vue.use(bkDropdownMenu);
Vue.use(bkException);
Vue.use(bkForm);
Vue.use(bkFormItem);
Vue.use(bkInput);
Vue.use(bkMemberSelector);
Vue.use(bkNavigation);
Vue.use(bkNavigationMenu);
Vue.use(bkNavigationMenuItem);
Vue.use(bkOption);
Vue.use(bkOptionGroup);
Vue.use(bkPagination);
Vue.use(bkPopover);
Vue.use(bkProcess);
Vue.use(bkProgress);
Vue.use(bkRadio);
Vue.use(bkRadioGroup);
Vue.use(bkRoundProgress);
Vue.use(bkRow);
Vue.use(bkSearchSelect);
Vue.use(bkSelect);
Vue.use(bkSideslider);
Vue.use(bkSlider);
Vue.use(bkSteps);
Vue.use(bkSwitcher);
Vue.use(bkTab);
Vue.use(bkTabPanel);
Vue.use(bkTable);
Vue.use(bkTableColumn);
Vue.use(bkTagInput);
Vue.use(bkPopconfirm);
Vue.use(bkTimePicker);
Vue.use(bkTimeline);
Vue.use(bkTransfer);
Vue.use(bkTree);
Vue.use(bkUpload);
Vue.use(bkSwiper);
Vue.use(bkRate);
Vue.use(bkAnimateNumber);
Vue.use(bkVirtualScroll);
Vue.use(bkColorPicker);
Vue.use(bkCard);

// bkDiff 组件体积较大且不是很常用，因此注释了。如果需要，打开注释即可
// Vue.use(bkDiff)

// directives use
Vue.use(bkClickoutside);
Vue.use(bkTooltips);
Vue.use(bkLoading);

// Vue prototype mount
Vue.prototype.$bkInfo = bkInfoBox;
Vue.prototype.$bkMessage = bkMessage;
Vue.prototype.$bkNotify = bkNotify;
