import hashlib
import json
import time
import jwt
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render
from user.models import Userprofile
# from . import models
from tools.logging_check import logging_check
# Create your views here.
from wtoken.views import make_token

#注册
@logging_check('PUT')
def users(request,username=None):

    if request.method == 'GET':
        if username:
            users = Userprofile.objects.filter(username = username)
            user = users[0]
            #TODO 没用户  返回对用的提示
            #拿具体用户数据
            #有查询字符串[?nickname=1]  or  没查询字符串
            if request.GET.keys():
                #查询字符串
                data = {}
                print(request.GET.keys())
                for k in request.GET.keys():
                    if hasattr(user,k):
                        #过滤字段  若是密码  则跳出此次循环
                        if k == 'password':
                            continue
                        v = getattr(user,k)
                        data[k] = v
                res = {'code':200,'username':username,'data':data}
                return JsonResponse(res)

            else:
                #无查询字符串
                users = Userprofile.objects.filter(username=username)
                #print(users) #<QuerySet [<Userprofile: Userprofile object>]>拿出来的是QuerySet对象
                user = users[0]#拿出来的是：<Userprofile: Userprofile object>
                res = {'code':200,'username':username,'data':{'nickname':user.nickname,
                                                              'sign':user.sign,
                                                              'info':user.info,
                                                              'avatar':str(user.avatar)}}
            #拿具体用户数据
            return JsonResponse(res)

        else:
            #拿全部数据
            all_users = Userprofile.objects.all()   #拿全量数据
            users_data = []
            for user in all_users:
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign     #个人签名
                dic['info'] = user.info     #此乃个人描述
                users_data.append(dic)
            res = {'code':200,'data':users_data}
            return HttpResponse(res)

    #注册用户
    elif request.method == 'POST':
        #创建用户
        json_str = request.body  #获取到的数据为字节串的字典b'{"username":"132","email":"1321","password_1":"1321"}',
        json_obj = json.loads(json_str)         #将json格式的数据转为字典
        # json_obj返回的数据格式{'username': '林培竹', 'email': '123456@qq.com', 'password_1': '123', 'password_2': '1321'}
        username = json_obj.get('username')
        password_1 = json_obj.get('password_1')
        password_2 = json_obj.get('password_2')
        email = json_obj.get('email')
        # nickname = json_obj.get('nickname')
        if not username or not password_1 or not password_2:
            return JsonResponse({'code':10101,'error':'Please give me username～'})
        if not email:
            return JsonResponse({'code':10102,'error':'请输入邮箱'})
        if password_1 != password_2:
            return JsonResponse({'code':10103,'error':'The password is error!'})
        #TODO 检查json dict 中的key 是否存在
        old_user = Userprofile.objects.filter(username  = username)
        if old_user:
            result = {'code':10104,'error':'用户名已存在'}
            return JsonResponse(result)
        #生成散列的密码
        pm = hashlib.md5()
        pm.update(password_1.encode())#加密动作，无返回值    pm.hexdigest()是取返回值
        #创建用户
        try:    #避免同时注册
            Userprofile.objects.create(username=username,password=pm.hexdigest(),nickname=username,email=email)
        except Exception as e:
            print('------create error------')
            print(e)
            result = {'code':10105,'error':'The username is already existed!!'}
            return JsonResponse(result)
        #生成令牌token
        token = make_token(username)    #设置token的携带用户名和过期时间
        result = {'code':200,'data':{'token':token.decode()},'username':username}
        return JsonResponse(result)

    # 更新 修改用户信息
    elif request.method == 'PUT':
        #更新     http://127.0.0.1:8000/v1/users/username
        if not username:
            res = {'code':10108,'error':'请输入具体用户'}
            return JsonResponse(res)
        json_str = request.body                 #PUT获取数据的方法，同POST
        #TODO 空body判断
        json_obj = json.loads(json_str)         #拿json串
        nickname = json_obj.get('nickname')
        info = json_obj.get('info')
        sign = json_obj.get('sign')
        #更新

        # users = Userprofile.objects.filter(username = username)
        # user = users[0]

        user = request.user
        #当前请求  token用户 修改自己的数据
        if user.username != username:
            result = {'code':10109,'error':'The username is error !'}
            return JsonResponse(result)
        to_update = False
        if user.nickname or user.info or user.sign: #判断用户是否有改动  避免数据做大量无效的动作
            to_update = True
        if to_update:
            #做更新    拿出每一条数据做更新
            user.nickname = nickname
            user.sign = sign
            user.info = info
            user.save() #保存
            # user.update(username = username,info=info,sign=sign,nickname=nickname)
        res = {'code':200,'username':username}
        return JsonResponse(res)

    return JsonResponse({'code': 200})

@logging_check('POST')
def users_avatar(request,username):
    #处理头像上传
    if request.method != 'POST':
        return JsonResponse({'code':10110,'error':'Please use POST'})
    user = request.user
    if user.username != username:
        result = {'code':10109,'error':'The username is error!'}
        return JsonResponse(result)
    user.avatar = request.FILES['avatar']
    user.save()
    return JsonResponse({'code':200,'username':username})




# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Imd1b3hpYW9uYW8iLCJleHAiOjE1NzMyOTc0MDMsImxvZ2luX3RpbWUiOiIyMDE5LTExLTA4IDE5OjAzOjIzLjQ1ODAwMiJ9.zBis9sYft5XWgrrWzZPpnw5mYIki0NjtivUaKMpfaA8
# eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VybmFtZSI6Imd1b3hpYW9uYW8iLCJleHAiOjE1NzMyOTc2NjksImxvZ2luX3RpbWUiOiIyMDE5LTExLTA4IDE5OjA3OjQ4Ljk3MTM2NiJ9.dyZEWMZ7t6IA8TWQ_vsDRZgToDW0ua-_vIKGT8gC9l4




















