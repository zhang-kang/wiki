from django.db import models

# Create your models here.
from user.models import Userprofile


class Topic(models.Model):
    # id = models.IntegerField(primary_key=True,verbose_name='文章序号')
    title = models.CharField(max_length=50,verbose_name='文章种类')
    #tec技术类文章  or  no - tec非技术类文章
    category = models.CharField(max_length=20,verbose_name='博客的分类')
    #public  公开博客  or  private私有博客
    limit = models.CharField(max_length=10,verbose_name='文章权限')
    introduce = models.CharField(max_length=90,verbose_name='博客简介')
    content = models.TextField(verbose_name='博客内容')
    created_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    updated_time = models.DateTimeField(auto_now=True,verbose_name='更新时间')
    author = models.ForeignKey(Userprofile)
    class Meta:
        db_table = 'topic'
















