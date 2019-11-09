import jwt
from django.http import JsonResponse

from user.models import Userprofile

TOKEN_KEY = '1234567ab'
#校验token
def logging_check(*methods):#需要调用此函数的请求方式
    def _loggin_check(func):
        def wrapper(request,*args,**kwargs):
            #逻辑判断
            #1.判断当前请求是否需要校验
            #2.取出token
            #3.如果需要校验token  如何校验
            if not methods:
                return func(request, *args, **kwargs)
            else:
                if request.method not in methods:
                    return func(request, *args, **kwargs)
            #取出token                      Authorization
            token = request.META.get('HTTP_AUTHORIZATION') #request.META包含所有本次HTTP请求的Header信息
            if not token:
                result = {'code':20104,'error':'Please login'}  #无token
                return JsonResponse(result)

            try:
                res = jwt.decode(token,TOKEN_KEY,algorithms='HS256')
            except Exception as e:
                result = {'code': 20105, 'error': 'Please login'}   #token校验失败
                return JsonResponse(result)
            username  = res['username']

            #取出token里的login_time
            login_time = res.get('login_time')    #取数据库里的tlogin_time

            user = Userprofile.objects.get(username=username)
            if login_time:
                if user.login_time != login_time:   #对比判断
                    result = {'code':20106,'error':'其他人登录了!请重新登录!'}
                    return JsonResponse(result)
            
            request.user = user

            return func(request,*args,**kwargs)
        return wrapper
    return _loggin_check



def get_user_by_request(request):
    #尝试获取用户身份
    #META可拿取http协议原生头  META 也是类字典对象  可使用字典相关方法 注意：http头有可能被django重命名，建议百度
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        #用户没登录
        return None
    try:
        res = jwt.decode(token,TOKEN_KEY,algorithms='HS256')
    except Exception as e:
        return None

    username = res['username']
    users = Userprofile.objects.filter(username=username)
    if not users:
        return None
    return users[0]













































