from django.conf.urls import url
from . import views


urlpatterns = [
    #http://127.0.0.1;800/v1/users
    #http://127.0.0.1;800/v1/tokens
    url(r'^$',views.users),

    #http://127.0.0.1:8000/v1/users/<username>  路由分组匹配格式（？<对应名>）
    url(r'^/(?P<username>\w{1,11})$',views.users),

    url(r'^/(?P<username>\w{1,11})/avatar$', views.users_avatar),

]













