
## 奖项yaml 配置格式
###奖项申报表单 json
```yaml
apiVersion: v1
kind: RawAppInfo          # 类型判断
spec:
  bindPolicy: "XXX奖"      # 绑定的奖项策略
  fields:
    - key: "name"         # 关键字
      label: "名称"        # 标签
      type: "bk-input"    # 参数类型，input表单输入格式
      default: ""         # 默认值
      required: true      # 是否必填
      placeholder: "名称"  # 表单元素的占位文本.默认显示
      rules:              # 定义表单项的校验规则
        - max: 100        # 输入框限制字数长度
          message: "不超过100个字"   # 输入框字数长度限制提示语
          trigger: "blur"
    - key: "member_selector"
      label: "人员选择器"
      type: "bk-tag-input"
      allow-create: true 
      placeholder: ""
      default: []
      required: true
    - key: "description"
      label: "事迹描述"
      type: "bk-input"
      default: ""
      required: true
      placeholder: "500字以内"
      componentType: "textarea"
      rules:
        - max: 500
          message: "不超过500个字"
          trigger: "blur"
    - key: "upload"
      label: "附件"
      type: "award-upload"
      default: ""
      required: true

  user_groups:
    # TODO: 初审环节审批人角色 根据场景设置
    - key: "gm"
      label: "部门GM"
      default: []
      required: true
      type: "bk-tag-input"
      allow-create: true
```

###奖项沉淀表单 json
```yaml
apiVersion: v1
kind: SummaryInfo    # 奖项沉淀表单信息
spec:
  # TODO: 奖项沉淀页面表单json格式参照
  - key: "title"      # 关键字
    label: "标题"      # 标签
    type: "bk-input"  # 参数类型，input表单输入格式
    default: ""       # 默认值
    required: true    # 是否必填
    placeholder: "标题"  # 表单元素的占位文本.默认显示
    rules:              # 定义表单项的校验规则
      - max: 100        # 输入框限制字数长度
        message: "不超过100个字"   # 输入框字数长度限制提示语
        trigger: "blur"  # 失焦时会触发校验
  - key: "introduction"
    label: "介绍"
    type: "bk-input"
    componentType: "textarea"   # 长文本输入框
    default: ""
    required: true
    placeholder: "2000字以内"
  - key: "team_members"
    label: "团队成员列表"
    type: "bk-tag-input"
    allow-create: true
    placeholder: ""
    default: [ ]
    required: true
  - key: "upload"
    label: "附件"
    type: "award-upload"
    default: ""
    required: true
```

###奖项级别
```yaml
apiVersion: v1
kind: LevelSet
spec:
  # TODO：根据具体奖项设置级别
  - key: "company"    # 关键字
    name: "公司级"     # 名称
    sort: 1           # 排序
  - key: "department"
    name: "部门级"
    sort: 2
```

### 用户组
```yaml
apiVersion: v1
kind: UserGroupSet
spec:
  # 设置不同类型的角色
  - key: "admin"        # 关键字
    name: "系统管理员"    # 名称
    type: "system"      # 类型，根据实际场景设置
  - key: "award_liaison"
    name: "奖项接口人"
    type: "fixed"
  - key: "application_liaison"
    name: "申报接口人"
    type: "fixed"
  - key: "applicant"
    name: "申报人"
    type: "fixed"
    
  - key: "project_liaison"
    name: "项目接口人"
  - key: "project_manager"
    name: "项目经理"
  - key: "initial_reviewer"
    name: "初审评委"
  - key: "professional_reviewer"
    name: "专业评委"
  - key: "final_reviewer"
    name: "终审评委"

  # TODO: 初审环节审批人员 (可根据场景自行设置)
  - key: "gm"
    name: "GM"
    type: "specific"
```