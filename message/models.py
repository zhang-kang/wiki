from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import Userprofile


class Message(models.Model):
    content = models.CharField(max_length=50,verbose_name='留言内容')
    created_time = models.DateTimeField(auto_now_add=True,verbose_name='创建时间')
    parent_message = models.IntegerField(default=0,verbose_name='关联的留言ID')
    publisher = models.ForeignKey(Userprofile,verbose_name='留言发布者')
    topic = models.ForeignKey(Topic,verbose_name='文章')
    class Meta:
        db_table = 'message'
















