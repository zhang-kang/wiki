import random

from django.db import models

# Create your models here.

def default_sign():
    signs = ['地表最强','和平主义','我爱我家']
    return random.choice(signs)




class Userprofile(models.Model):
    username = models.CharField(max_length=11,primary_key=True,verbose_name='用户名')
    nickname = models.CharField(max_length=30,verbose_name='昵称')
    email = models.EmailField(verbose_name='邮箱')
    password = models.CharField(max_length=32,verbose_name='密码')
    sign = models.CharField(max_length=50,verbose_name='个人签名',default=default_sign)
    info = models.CharField(max_length=150,verbose_name='个人描述',default='')
    created_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    #upload_to  指定存储位置  MEDIA_ROOT + UPLOAD_TO 的值
    #wiki/media/avatar
    avatar = models.ImageField(upload_to='avatar',default='',verbose_name='头像')

    login_time = models.DateTimeField(null=True,verbose_name='用户登录时间')


    class Meta:
        db_table = 'user_profile'






















