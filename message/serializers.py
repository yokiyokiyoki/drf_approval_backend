from rest_framework import serializers, exceptions
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

from django.contrib.auth.models import update_last_login

from rest_framework.validators import UniqueValidator

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenObtainSerializer, RefreshToken
from .models import MessagesRecord

import moment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text="用户编号", read_only=True)
    username = serializers.CharField(help_text="用户名", min_length=1, max_length=100, error_messages={
        'min_length': '用户名过短',
        'min_length': '用户名过长'
    },
        # 约束唯一
        validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    def validate_username(self, value):
        if 'yoki3' in value.lower():  # 名字中不能出现g
            raise exceptions.ValidationError('名字非法！')
        return value

    def create(self, validated_data):
        date = moment.now().format('YYYY-M-D')
        # 尽量在所有校验规则完毕之后，数据可以直接入库
        return User.objects.create(**validated_data)

    class Meta:
        model = User
        fields = ('id', 'username')


# 自定义payload
class MyTokenObtainPairSerializer(TokenObtainSerializer):
    '''
    重写，因为不需要密码
    '''
    username_field = "username"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(min_length=1)
        self.fields['password'] = serializers.CharField(required=False)

    @ classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = {}
        self.user = User.objects.get(username=attrs["username"])

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        return data
