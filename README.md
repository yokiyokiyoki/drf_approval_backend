# 开始

使用 drf 快速构建一个审批系统，celery 构建定时任务

# 本地开发

```bash
# 安装相关包
pip3 install -r requirements.txt

# 本地运行 8000端口
python3 manage.py runserver

# 本地运行 8001端口
python3 manage.py runserver 0.0.0.0:8001

#安装新包后锁住版本
pip3 freeze > requirements.txt
```

# 目录配置

## 应用

message 是一个应用

### 中间件

主要是程序异常时候捕获，返回响应

### lib 工具库

工具库

### apps

主要放配置，分成 dev 环境配置和 prod 环境配置

```bash
#如何获取运行时配置
from rest_framework.settings import api_settings
from django.conf import settings
```

# 数据库

## 分表

请看 dynamic_model.py，同时需要设置 model 的 meta 类 abstract=true。目前可以按月分表

# 鉴权

使用 jwt 进行鉴权-djangorestframework_simplejwt（具体配置在 base.py）

# 部署

## 配置

相关配置在 conf 文件夹下，目标是容器化

```bash
$ docker build -t csighub.tencentyun.com/yorkieli/codedog_user_backend:v1 -f conf/stke/Dockerfile .

$ docker push csighub.tencentyun.com/yorkieli/codedog_user_backend:v1
```
