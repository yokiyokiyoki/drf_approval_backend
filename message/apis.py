# 系统类型


import sys
import json
import os
import logging
import io
import cgi
import time
import uuid

# 配置类型
from rest_framework.settings import api_settings
from django.conf import settings


# django
import django
from django.http import HttpResponse, StreamingHttpResponse, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.http.multipartparser import MultiPartParser as DjangoMultiPartParser
from django.views.decorators.csrf import csrf_exempt
from django.http.multipartparser import Parser, parse_header

# 第三方库
import xml.etree.cElementTree as ET
import requests
from jwt import decode as jwt_decode
from hashlib import sha256, sha1


from message.lib.Cipher import Base62Cipher
from message.lib.JWTAuthentication import Authentication as JWTAuthentication
from message.lib.Batch import BatchGenericViewSet, BatchMixin
from message.lib.WXBizMsgCrypt import WXBizMsgCrypt

# model

from django.forms.models import model_to_dict
from message.models import WechatSubscribeInfo
from message import models, serializers
from django.contrib.auth import get_user_model


# rest_framework
from rest_framework import filters, mixins, generics
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework import status
from rest_framework import filters
from rest_framework import mixins, generics
from rest_framework.views import APIView

from rest_framework.parsers import BaseParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

# 日志设置
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
User = get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = serializers.MyTokenObtainPairSerializer

    '''
    重写post方法
    '''

    def post(self, request, *args, **kwargs):
        data = request.data
        token_ser = self.get_serializer(data=request.data)
        try:
            token_ser.is_valid(raise_exception=True)

        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(token_ser.validated_data, status=status.HTTP_200_OK)


class UserListView(generics.GenericAPIView):
    serializer_class = serializers.UserSerializer
    authentication_classes = (
        JWTTokenUserAuthentication,
    )
    permission_classes = (IsAuthenticated, )

    # 重写权限，post无须
    def get_permissions(self):
        if self.request.method == 'POST':
            return []
        else:
            return [IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        user_obj_list = User.objects.all()
        user_ser = self.get_serializer(user_obj_list, many=True)

        filter_backends = (filters.SearchFilter,)
        return Response({
            'status': 200,
            'msg': 'ok',
            'results': user_ser.data
        })

    def post(self, request, *args, **kwargs):
        data = request.data

        user_ser = self.get_serializer(data=data)

        if user_ser.is_valid():
            # 校验通过，完成新增
            user_obj = user_ser.save()
            return Response({
                'status': 200,
                'msg': 'ok',
                'results': self.get_serializer(user_obj).data
            })
        else:
            # 校验失败
            return Response({
                'status': -1,
                'msg': user_ser.errors,
            })
