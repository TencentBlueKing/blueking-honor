

## env
新建  /bk-honor/src/api/bk_honor/settings/.env
加载 env环境配置文件

``` yaml
# 数据库配置
DB_NAME=bk_honor
DB_USER=root
DB_PASSWORD=******
DB_HOST=127.0.0.1
DB_PORT=3306

# 蓝鲸登录配置
BK_LOGIN_URL="***"
BK_LOGIN_API_URL="***"
BK_LOGIN_VERIFY_URI="/user/is_login/"
BK_LOGIN_USER_INFO_URI="/user/get_full_info/"
BK_TOKEN_COOKIE_NAME="bk_token"
CSRF_COOKIE_DOMAIN="***"

# bk-repo文件存储配置
BKREPO_USERNAME=""
BKREPO_BUCKET=""
BKREPO_PRIVATE_BUCKET=""
BKREPO_PUBLIC_BUCKET=""
BKREPO_ENDPOINT_URL="***"
BKREPO_PROJECT="***"
BKREPO_PASSWORD="***"

# ESB配置
BKPAAS_APP_SECRET=""
BK_ESB_BASE_URL="***"

# 奖项申报通知按钮
#FORCE_SILENCE=1

# 审批配置：默认自动审批流转
DEFAULT_STEP_AUTO_EXECUTE=False

ALLOW_SAME_APPLICANT_PER_APPLICATION=False
# 审批配置：是否允许一人审批通过 or 全员审批通过
ANY_PASS=True
```