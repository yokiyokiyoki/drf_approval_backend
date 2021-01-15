from django.urls import path, re_path, include
from django.conf.urls import url


from message import apis

urlpatterns = [
    # 自定义token
    path('auth/get_token/', apis.MyTokenObtainPairView.as_view()),

    path('users/', apis.UserListView.as_view()),
    path('messages/', apis.UniversalMessagesView.as_view()),
    # app

    path('wechat/template_messages', apis.WechatTemplateMessagesView.as_view()),

    # 微信验证

    path('wechat/dataCallback/', apis.WechatTemplateMessagesView.as_view()),
]
