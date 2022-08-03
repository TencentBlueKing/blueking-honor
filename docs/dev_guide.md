# 开发指引

## 文件目录释义
```text
├── docs  # 文档
└── src
    ├── api  # Saas 后端代码
    └── front  #  SaaS 前端代码 
```

本地开发时，你需要分别为两个模块——SaaS 前端、SaaS 后端-—创建开发环境。

在开始开发前，你需要为整个项目安装并初始化 `pre-commit`， 

``` bash
pre-commit install
```

目前我们使用了四个工具: `isort`、`black`、`flake8`、`mypy`，它们能保证你的每一次提交都符合我们预定的开发规范。

## 如何在本地开启服务

### 本地安装 Python 依赖并拉起后端进程

前端开发同学请跳过此步骤

```shell
# 运行本地项目需要确认是否从 yaml 中加载奖项策略添加到数据库
python manage.py load_policies_from_yaml
```


```shell
# 在本地启动后端进程，需要提前 poetry install
make run-backend
```

### 本地构建镜像并拉起容器

```shell

# 构建镜像，同时会构建前端内容
# 当本地代码更新后，需要再次构建
make build

# 将镜像更新到远端仓库
make push

# arm64 机器需要额外安装 buildx
# 需要注意，此时会包括 build & push 两个操作
make buildx

# 拉起容器，首次启动会尝试拉取镜像，等待时间稍长
make run

# 构建并拉起，
# 启动后会在项目路径下创建 .services 路径，其中会包括 mysql 存储文件
make start
```

本地 `http://localhost:8007` 即可访问系统或者 `http://localhost:8007/swagger/` 访问 API 文档。

如果本地不再需要该服务，可以删除容器：
```shell
make stop
```
剩余的镜像请通过 docker 命令手动删除。

## 如何构造本地开发测试数据

对于通过 Python 拉起后端进程，在 `src/api/` 下执行命令

```shell
python manage.py load_dev_data
```

对于通过容器拉起后端服务的，需要通过 docker 来执行相关指令

```shell
# 获取容器 ID
# 如果无法拿到容器 ID，请使用 docker ps -a 检查是否正在运行
# 或者手动获取容器 ID
docker ps | grep bk-honor | awk '{print $1}'
# 执行加载奖项策略
docker exec -it {web 容器 ID} python manage.py load_policies_from_yaml
# 执行数据加载指令
docker exec -it {web 容器 ID} python manage.py load_dev_data --applicants {奖项申请人池,建议填写自己用户名} --liaisons foo,bar --staffs ooo,qqq
# 执行数据加载指定-创建多条申报完成的奖项内容，并且创建奖项沉淀内容
docker exec -it {web 容器 ID} python manage.py load_dev_data --applicants {奖项申请人池,建议填写自己用户名} --liaisons qqq,www,eee --staffs rrr,ttt,yyy --material_title 标题1,标题2 --winning_team_name ddd,fff --deeds_introduction kkk,fff,ggg --team_members {奖项申请人池,建议填写自己用户名} --funding_sys_name 经费系统名称1,经费系统名称2
```

执行后，会按照 `make load` 指令注入的策略数据，构造有一定随机性的测试数据，主要包括：
- Award 奖项数据
- Application 申报数据
- Stage & Step 流程数据

运行结束后，会输出类似字样：
```
Award created: 64, Application created: 116
```

**建议不要重复执行此指令**，因为会导致产生大量数据，反而给开发造成不便。


### 为什么不自动加载？

因为测试数据仅供开发使用，不宜集成到特定流程中，由开发者有意识地手动控制更好。