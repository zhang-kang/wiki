import json

from django.http import JsonResponse
from django.shortcuts import render

from message.models import Message
from tools.logging_check import logging_check


# Create your views here.
from topic.models import Topic


@logging_check('POST')
def messages(request,topic_id):
    if request.method == 'POST':
        json_str = request.body
        json_obj = json.loads(json_str)
        content = json_obj.get('content')
        parent_id = json_obj.get('parent_id',0)
        #TODO  参数检查

        #检车topic是否存在
        try:
            topic = Topic.objects.get(id=topic_id)
        except Exception as e:
            return JsonResponse({'code':40101,'error':'No topic'})
        #第一种方案  可以直接对外键属性赋值  对象
        Message.objects.create(content=content,parent_message=parent_id,publisher=request.user,topic=topic)
        #第二种方案  用外键值  赋值给  外键字段名
        # Message.objects.cerate(content=content,parent_message=parent_id,publisher=request.user,topic_id=topic_id)

        return JsonResponse({'code':200})

    if request.method == 'GET':
        #http://127.0.0.1:8000/v1/messages/<topic_id>
        # all_m = Message.objects.all()         此方法会显示全部留言
        all_m = Message.objects.filter(topic_id=int(topic_id))  #此方法只显示对应文章id的数据
        all_list = []
        for m in all_m:
            d = {}
            d['id'] = m.id
            d['content'] = m.content
            d['parent_message'] = m.parent_message
            d['publisher'] = m.publisher.username
            d['topic'] = m.topic.id
            all_list.append(d)
        return JsonResponse({'code':200,'data':all_list})



















