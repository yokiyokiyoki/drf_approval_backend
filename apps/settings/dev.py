from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'micro_service_message',
        'HOST': '9.134.14.199',  # 数据库地址
        'PORT': 3306,  # 端口
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'yoki!@#$',  # 数据库密码
    }
}
