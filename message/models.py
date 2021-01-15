
from django.contrib.auth.models import AbstractBaseUser
from django.db import models
from django.apps import apps
import django

from message.lib.SnowFlake import IdWorker, GenerateId
from message.lib.dynamic_model import MonthShardMixin


def gen_id():
    '''
    雪花算法生成id，不用uuid，太长了且无序
    '''
    worker = IdWorker(GenerateId.get_data_center_id(),
                      GenerateId.get_work_id(), 0)
    id = worker.get_id()
    return id


# Create your models here.
"""
 该类是用来生成数据库的 必须要继承models.Model
"""


class WechatSubscribeInfo(models.Model):
    '''订阅信息表'''
    GENDER_CHOICES = (
        (2, 'female'),
        (1, 'male'),
        (0, 'unknown')
    )
    uid = models.BigIntegerField(primary_key=True, default=gen_id, unique=True)
    unionid = models.CharField(max_length=256, default='')
    openid = models.CharField(max_length=256, default='')
    nickname = models.CharField(max_length=512)
    avatar_url = models.CharField(max_length=512)

    def __str__(self):
        return str(self.uid)

    class Meta:
        db_table = "message_wechat_subscribe"


class MessagesRecord(models.Model, MonthShardMixin):

    uid = models.BigIntegerField(primary_key=True, default=gen_id, unique=True)
    create_time = models.DateTimeField(auto_now_add=True)
    user = models.IntegerField(
        help_text="用户id", blank=True, null=True, default=0)
    msg_type = models.CharField(
        help_text="消息类型", blank=True, null=True, default=0, max_length=64)
    sender = models.CharField(
        help_text="发送", blank=True, null=True, max_length=512)
    to = models.CharField(help_text="接收", blank=True,
                          null=True, max_length=512)
    cc = models.CharField(help_text="抄送", blank=True,
                          null=True, max_length=512)
    bcc = models.CharField(help_text="密送", blank=True,
                           null=True, max_length=512)
    title = models.CharField(help_text="标题", null=True,
                             blank=True, max_length=256)
    content = models.TextField(help_text="正文内容", null=True, blank=True)

    msg_result = models.TextField(help_text="第三方返回内容", null=True, blank=True)

    class Meta:
        abstract = True

        db_table = "message_record"
