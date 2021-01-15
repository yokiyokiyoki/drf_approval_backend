from .base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'micro-service-message',
        'HOST': '11.186.4.242',  # 数据库地址
        'PORT': 3306,  # 端口
        'USER': 'root',  # 数据库用户名
        'PASSWORD': 'cdtiyan!@#123',  # 数据库密码
        'OPTIONS': {'charset': 'utf8mb4'}
    }
}
