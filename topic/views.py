import json

from django.http import JsonResponse
from django.shortcuts import render

from message.models import Message
from tools.logging_check import logging_check,get_user_by_request

# Create your views here.
from topic.models import Topic
from user.models import Userprofile


@logging_check('POST','DELETE')
def topics(request, author_id):     #不同用户访问文章的处理 博主自己、访问者
    if request.method == 'GET':
        #获取用户文章数据
        #/v1/topics/guoxiaonao - guoxiaonao的所有文章
        #v1/topics/guoxiaonao?category=tec|no-tec   #查看具体种类
        #v1/topics/guoxiaonao?t_id=1                查看具体文章

        #1.访问当前博客的访问者      visitor
        #2.当前被访问的博客的博主     author
        authors = Userprofile.objects.filter(username=author_id)            #拿到被访问博主的用户名
        if not authors:
            result = {'code':30104,'error':'The author is not existed!!'}   #若无此博主 返回此
            return JsonResponse(result)
        #当前被访问的博客博主
        author = authors[0]
        #访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        t_id = request.GET.get('t_id')
        if t_id:
            t_id = int(t_id)
            # 获取指定文章的详情页
            is_self = False     #生成标记为True 为博主访问自己 ，False为陌生访客访问博主

            if author_id == visitor_username:
                # 博主本人访问自己的博客
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    print('--get t_id error--')
                    print(e)
                    result = {'code': 30108, 'error': 'No topic'}
                    return JsonResponse(result)
            else:
                # 非博主访问当前博客
                try:
                    author_topic = Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code': 30109, 'error': 'No topic visitor !'}
                    return JsonResponse(result)
            # 生成具体返回值(评论留言)
            res = make_topic_res(author, author_topic,is_self)
            return JsonResponse(res)

        else:
            #获取列表页的需求

            category = request.GET.get('category')
            if category in ['tec','no-tec']:
                #按种类筛选
                if author_id == visitor_username:   #博主自己
                    author_topics = Topic.objects.filter(author_id = author_id,category = category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id,limit='public',category=category)
            else:
                #全量  不分种类筛选
                if author == visitor_username:
                    #博主访问自己的博客 返回全部文章
                    author_topics = Topic.objects.filter(author_id=author_id)
                    # res = make_topics_res(author,author_topic)
                    # return JsonResponse(res)
                else:
                    #陌生访客访问他人博客  只返回公开权限的文章
                    author_topics = Topic.objects.filter(author_id=author_id,limit='public')
            res = make_topics_res(author,author_topics)
            return JsonResponse(res)

    if request.method == 'POST':
        author = request.user
        if author.username != author_id:    #校验是否是当前用户
            return JsonResponse({'code':30101,'error':'The author is error'})

        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        #注意xss攻击  （注入js攻击） 将用户输入进行转义
        import html
        title = html.escape(title)  #将用户输入进行转义

        category = json_obj.get('category')
        if category not in ['tec','no-tec']:    #判断是否是指定的两种类型 技术类和非技术类
            return JsonResponse({'code':30102,'error':'Thanks your category is error!!'})
        limit = json_obj.get('limit')
        if limit not in ['public','private']:   #判断是否是指定的两种类型 个人博客和公开博客
            return JsonResponse({'code':30103,'error':'Thanks your category is error!!'})
        #带样式的文章内容
        content = json_obj.get('content')
        #纯文本的文章内容  用于做文章简介的切片
        content_text = json_obj.get('content_text')
        introduce = content_text[:30]
        #创建topic  存入数据库
        Topic.objects.create(title=title,limit=limit,category=category,
                             content=content,introduce=introduce,author=author)
        result = {'code':200,'username':author.username}
        return JsonResponse(result)

    if request.method == 'DELETE':
        #删除博客文章  真删除
        #请求中 携带查询字符串 ？topic_id=3
        #响应{‘code’：200}
        user  = request.user
        if user.username != author_id:
            #检查token中的用户名和前段访问的用户名是否一致
            return JsonResponse({'code':30105,'error':'Your author_id is error'})
        #获取查询字符串
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            return JsonResponse({'code':30106,'error':'Must be give me topic_id!'})
        topic_id = int(topic_id)
        try:    #删除要加 try  以防出错
            topic = Topic.objects.filter(id=topic_id)
        except Exception as e:
            print(e)
            print('------topic delete error------')
            result = {'code':30107,'error':'The topic is not existed!'}
            return JsonResponse(result)
        topic.delete()
        result = {'code':200}
        return JsonResponse(result)



def make_topics_res(author,author_topics):
    res = {'code':200,'data':{}}
    res['data']['nickname'] = author.nickname
    res['data']['topics'] = []
    for topic in author_topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['introduce'] = topic.introduce
        d['category'] = topic.category
        d['created_time'] = topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        d['author'] = author.nickname
        res['data']['topics'].append(d)
    return res
    #上面函数的返回值格式  res  传进去的是两个模型类的对象
# {'code': 200,
#  'data': {'nickname': '郭小闹大风歌',
#   'topics': [{'author': '郭小闹大风歌',
#     'category': 'tec',
#     'created_time': '2019-11-04 10:43:1572835409',
#     'id': 1,
#     'introduce': '是法国还是该函数',
#     'title': '发鬼地方'}]}}

def make_topic_res(author,author_topic,is_self):  #authors是Userprofile模型类的实例化对象，author_topics是Topic模型类的实例化对象

    #获取上一篇文章的id 和title
    if is_self:#博主自己访问
        #next_topic大于当前文章id的第一个
        next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author).first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id,author=author).last()
    else:
        #访客访问当前博客
        next_topic = Topic.objects.filter(id__gt=author_topic.id,author=author,limit='public').first()
        last_topic = Topic.objects.filter(id__lt=author_topic.id,author=author,limit='public').last()
    if next_topic:
        next_id = next_topic.id
        next_title = next_topic.title
    else:
        next_id  = None
        next_title = None

    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None

    #获取下一篇文章的id 和title
    res = {'code': 200, 'data':{}}
    res['data']['title'] = author_topic.title
    res['data']['nickname'] = author.nickname
    res['data']['content'] = author_topic.content
    res['data']['introduce'] = author_topic.introduce
    res['data']['category'] = author_topic.category
    res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
    res['data']['author'] = author.nickname
    res['data']['next_id'] = next_id
    res['data']['next_title'] = next_title
    res['data']['last_id'] = last_id
    res['data']['last_title'] = last_title

    #留言
    #获取当前文章的所有留言
    all_message = Message.objects.filter(topic=author_topic).order_by('-created_time')
    #留言专属容器
    msg_list = []
    #回复专属容器
    reply_home = {}
    m_count = 0
    for message in all_message:
        m_count += 1
        if message.parent_message:

            #回复
            reply_home.setdefault(message.parent_message,[])
            reply_home[message.parent_message].append({
                    'msg_id': message.id,
                    'content': message.content,
                    'publisher': message.publisher.nickname,
                    'publisher_avatar': str(message.publisher.avatar),
                    'created_time': message.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                })
        else:

            #留言
            msg_list.append({
                    'id':message.id,
                    'content':message.content,
                    'publisher':message.publisher.nickname,
                    'publisher_avatar':str(message.publisher.avatar),
                    'created_time':message.created_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'reply':[]})
    #关联  留言及回复
    for m in msg_list:
        if m['id'] in reply_home:
            m['reply'] = reply_home[m['id']]

    res['data']['messages'] = msg_list
    res['data']['messages_count'] = m_count
    return res



















