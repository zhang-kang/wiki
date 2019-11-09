import datetime
import hashlib
import json
import time

import jwt
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
from user.models import Userprofile

    #登录
def tokens(request):
    if request.method != 'POST':
        result = {'code':20101,'error':'Please use POST'}
        return JsonResponse(result)
    json_str = request.body
    #TODO 检查参数是否存在
    json_obj = json.loads(json_str)
    username = json_obj.get('username')
    password = json_obj.get('password')
    #找用户
    users = Userprofile.objects.filter(username=username)
    if not users:
        result = {'code':20102,'error':'The username or password is error'}
        return JsonResponse(result)
    user = users[0]

    pm = hashlib.md5()
    pm.update(password.encode())
    if user.password != pm.hexdigest():
        result = {'code':20103,'error':'The username or password is error!!'}
        return JsonResponse(result)
    #生成token

    #同一时间只允许一个用户登录
    now_datetime = datetime.datetime.now()  #获取当前时间

    user.login_time = now_datetime          #将最新时间保存在数据库
    user.save()
    token = make_token(username,str(now_datetime))


    result = {'code': 200, 'username': username,'data':{'token':token.decode()}}
    return JsonResponse(result)


def make_token(username,now_datetime,exp = 3600*24):
    #生成token
    # exp = 3600*24
    key = '1234567ab'

    now_t = time.time()
    payload = {'username':username,'exp':int(now_t + exp),'login_time':now_datetime}
    return jwt.encode(payload,key,algorithm='HS256')
    # result = {'code':200,'username':username,'data':{'token':wtoken}}
    # return JsonResponse(result)


































