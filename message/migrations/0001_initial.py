# Generated by Django 3.0.6 on 2021-01-12 03:21

from django.db import migrations, models
import message.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='WechatSubscribeInfo',
            fields=[
                ('uid', models.BigIntegerField(default=message.models.gen_id, primary_key=True, serialize=False, unique=True)),
                ('unionid', models.CharField(default='', max_length=256)),
                ('openid', models.CharField(default='', max_length=256)),
                ('nickname', models.CharField(max_length=512)),
                ('avatar_url', models.CharField(max_length=512)),
            ],
            options={
                'db_table': 'message_wechat_subscribe',
            },
        ),
    ]