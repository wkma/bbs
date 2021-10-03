from django.shortcuts import render, redirect, HttpResponse
from app01.forms import MyForm
from app01 import models
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.decorators import login_required  # 登录装饰器
from django.db.models import Count, F  # 导入聚合函数  F查询
from django.db.models.functions import TruncMonth  
from bs4 import BeautifulSoup  # 处理html页面，xss攻击
import os
from test12_bbs import settings
from utils.mypage import Pagination
from django.core.paginator import Paginator
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO


def bootstrapcs(request):
    return render(request, 'bootstrapceshi.html')


def register(request):
    form_obj = MyForm()
    if request.method == 'POST':
        back_dic = {'code': 1000, 'msg': ''}  # 与ajax交互而定义一个字典
        # 校验数据是否合法
        form_obj = MyForm(request.POST)  # 只接收form1字段进行校验
        username = request.POST.get('username')
        # 判断数据是否合法
        if form_obj.is_valid():
            # print(form_obj.cleaned_data)  #{'username': 'wang', 'password': '123', 'confirm_password': '123', 'email': 'wwwwww@xx.com'}
            clean_data = form_obj.cleaned_data  # 将校验通过的数据字典赋值给一个变量
            # 将字典里面的confirm_password删除
            clean_data.pop('confirm_password')  # {'username': 'wang', 'password': '123', 'email': 'wwwwww@xx.com'}
            # 用户头像
            file_obj = request.FILES.get('avatar')
            # 针对用户头像一定要判断是否传值 不能直接添加到字典里去
            if file_obj:
                clean_data['avatar'] = file_obj
            # 操作数据库进行保存
            models.UserInfo.objects.create_user(**clean_data)
            if models.Blog.objects.exclude(site_name=username):
                res = models.Blog.objects.create(site_name=username, site_title=username,
                                                 site_theme=str(username) + ".css")
                res.save()
                models.UserInfo.objects.filter(username=username).update(blog_id=res.id)
            back_dic['url'] = '/login/'
        else:
            back_dic['code'] = 2000
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)

    return render(request, 'register.html', locals())


def login(request):
    if request.method == "POST":
        # print(request.POST)
        back_dic = {'code': 1000, 'msg': ''}
        username = request.POST.get('username')
        password = request.POST.get('password')
        code = request.POST.get('code')
        # 1先校验验证码是否正确,忽略大小写
        if request.session.get('code').upper() == code.upper():
            # 2校验用户名与密码是否正确
            user_obj = auth.authenticate(request, username=username, password=password)
            if user_obj:
                # 保存用户状态
                auth.login(request, user_obj)
                back_dic['url'] = '/'
            else:
                back_dic['code'] = 2000
                back_dic['msg'] = '用户名或密码错误'
        else:
            back_dic['code'] = 3000
            back_dic['msg'] = '验证码错误'
        return JsonResponse(back_dic)
    return render(request, 'login.html')


"""
Image:生成图片
ImageDraw：能够在图片上乱涂画
ImageFont  控制字体样式
"""

"""
内存管理模块
BytesIO：临时帮你存储数据 返回的时候数据是二进制
StringIO：临时帮你存储数据 返回的时候数据是字符串
"""
import random


def random_colour():
    return random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)


def get_code(request):
    # 推导步骤1：直接获取后端现成的图片二进制数据发送给前端
    # with open(r'static/img/345.jpg','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤2.利用pillow模块动态产生图片
    # img_obj = Image.new('RGB', (430, 35), random_colour())
    # #先将图片保存起来
    # with open('xxx.png','wb') as f:
    #     img_obj.save(f,'png')
    # #再将图片对象取出来
    # with open('xxx.png','rb') as f:
    #     data = f.read()
    # return HttpResponse(data)

    # 推导步骤3：文件存储繁琐IO操作效率低 借助于内存管理器模块
    # img_obj = Image.new('RGB',(400,50),random_colour())
    # io_obj = BytesIO()  #生成一个内存管理器模块 可以看成是文件句柄
    # img_obj.save(io_obj,'png')
    # return HttpResponse(io_obj.getvalue())  #从内存管理器中读取二进制的图片返回给前端

    # 最终步骤：写图片验证码
    img_obj = Image.new('RGB', (400, 50), random_colour())
    img_draw = ImageDraw.Draw(img_obj)  # 产生一个画笔对象
    img_font = ImageFont.truetype('static/font/alipu.ttf', 30)  # 字体样式 大小

    # 随机验证码 五位数的随机验证码 数字 小写字母 大写字母
    code = ''
    for i in range(5):
        random_upper = chr(random.randint(65, 90))
        random_lower = chr(random.randint(97, 122))
        random_int = str(random.randint(0, 9))
        # 从上面三个里面随机选一个
        tmp = random.choice([random_lower, random_upper, random_int])
        # 将随机字符串写入到图片上
        # 一个一个字写可以可知间隙，依次完全生成好了就无法控制间隙
        img_draw.text((i * 50 + 60, 0), tmp, random_colour(), img_font)
        # 拼接随机字符串
        code += tmp
    # print(code)
    # 随机验证码在登录的视图函数里面需要用到 要比对 所以要找地方存起来并在视图函数可以拿到
    request.session['code'] = code
    io_obj = BytesIO()
    img_obj.save(io_obj, 'png')
    return HttpResponse(io_obj.getvalue())


def home(request, *wargs):
    # 查询本网站所有数据
    article_queryset = models.Article.objects.all().order_by("-create_time")
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_queryset.count())
    page_queryset = article_queryset[page_obj.start:page_obj.end]
    return render(request, 'home.html', locals())


@login_required
def set_password(request):
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == "POST":
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                if new_password == confirm_password:
                    request.user.set_password(new_password)
                    request.user.save()
                    back_dic['msg'] = '修改成功'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '两次密码不一致'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '原密码错误'
    return JsonResponse(back_dic)


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/')


def site(request, username, **kwargs):
    """
    :param request:
    :param username:
    :param kwargs:如果该参数有值意味着对article_list做额外的筛选操作
    :return:
    """
    # 先校验当前用户名对应的个人站点是否存在
    user_obj = models.UserInfo.objects.filter(username=username).first()
    # 如果用户不存在则返回404页面
    if not user_obj:
        return render(request, 'error.html')
    blog = user_obj.blog
    # 常看当前个人站点的所有文章
    article_list = models.Article.objects.filter(blog=blog).order_by("-id")  # queryset对象，侧边栏的筛选其实就是对article_list再进一步筛选

    # 1查询当前用户所有的分类以及分类下的文章数
    category_list = models.Category.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list(
        'name', 'count_num', 'pk')
    # print(category_list)  <QuerySet [('数学建模培养', 1), ('王的分类', 2), ('python', 2), ('前端', 1)]>
    # 2查询当前用户所有的标签及标签下的文章数
    tag_list = models.Tag.objects.filter(blog=blog).annotate(count_num=Count('article__pk')).values_list('name',
                                                                                                         'count_num',
                                                                                                         'pk')
    # 3按照年月统计所有的文章
    date_list = models.Article.objects.filter(blog=blog).annotate(month=TruncMonth('create_time')) \
        .values('month').annotate(count_num=Count('pk')).values_list('month', 'count_num')
    # print(date_list)
    if kwargs:
        # print(kwargs)  #{'condition': 'tag', 'param': '1'}
        condition = kwargs.get('condition')
        param = kwargs.get('param')
        # 判断用户想要根据说明条件筛选数据
        if condition == 'category':
            article_list = article_list.filter(category_id=param)
        elif condition == 'tag':
            article_list = article_list.filter(tags__pk=param)
        else:
            year, month = param.split('-')  # 解压赋值。例如2020-12 [2020,12]
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    return render(request, 'site.html', locals())


def article_detail(request, username, article_id):
    """
    需要校验username和article_id是否存在，但是我们这里先只完成正确情况

    :param request:
    :param username:
    :param article_id:
    :return:
    """
    # 1先获取文章对象
    user_obj = models.UserInfo.objects.filter(username=username).first()
    blog = user_obj.blog
    article_obj = models.Article.objects.filter(pk=article_id, blog__userinfo__username=username).first()
    if not article_obj:
        return render(request, 'error.html')

    # 获取当前文章所有评论
    comment_list = models.Comment.objects.filter(article=article_obj)

    return render(request, 'article_detail.html', locals())


import json


def up_or_down(request):
    """
    1校验用户是否登录
    2判断当前文章是否是用户自己写的（自己不能给自己点赞）
    3判断当前用户是否已经给当前文章点过了
    4操作数据库
    :param request:
    :return:
    """
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        # 1判断当前用户是否登录

        if request.user.is_authenticated:
            article_id = request.POST.get('article_id')
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)  # 将Json格式转化为python
            # 2判断当前文章是否是当前用户自己写的 根据文章查文章对象 根据文章对象查作者，跟request.user_id比对
            article_obj = models.Article.objects.filter(pk=article_id).first()
            if not article_obj.blog.userinfo == request.user:
                # 3校验当前用户是否已经点了
                is_click = models.UpAndDown.objects.filter(user=request.user, article=article_obj)
                if not is_click:
                    # 4操作数据库，记录数据  要同步操作普通字段
                    # 判断当前用户点了赞还是踩 从而决定给那个字段+1
                    if is_up:
                        # 给点赞数加一
                        models.Article.objects.filter(pk=article_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功1'
                    else:
                        # 给点踩+1
                        models.Article.objects.filter(pk=article_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                    # 操作点赞表
                    models.UpAndDown.objects.create(user=request.user, article=article_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '你已经点过了，不能再点了'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '不能自行点击'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '请先<a href="/login/">登录</a>'
        return JsonResponse(back_dic)


from django.db import transaction  # 使用事务


def comment(request):
    # 自己也可以给自己文章评论内容
    if request.is_ajax():
        back_dic = {'code': 1000, 'msg': ''}
        if request.method == 'POST':
            if request.user.is_authenticated:
                article_id = request.POST.get('article_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                # 直接操作评论表存储数据   两张表,article,comment
                with transaction.atomic():
                    models.Article.objects.filter(pk=article_id).update(comment_num=F('comment_num') + 1)
                    models.Comment.objects.create(user=request.user, article_id=article_id, content=content,
                                                  parent_id=parent_id)
                back_dic['msg'] = '评论成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = "用户未登陆"
            return JsonResponse(back_dic)


@login_required
def backend(request):
    article_list = models.Article.objects.filter(blog=request.user.blog).order_by("-id")
    category_num = models.Category.objects.filter(blog=request.user.blog).count()
    category_list = models.Category.objects.filter(blog=request.user.blog)
    page_obj = Pagination(current_page=request.GET.get('page', 1), all_count=article_list.count(), per_page_num=5)
    page_queryset = article_list[page_obj.start:page_obj.end]
    return render(request, 'backend/backend.html', locals())


@login_required
def category_create(request):
    if request.method == "POST":
        name = request.POST.get('name')
        obj = models.Category.objects.filter(name=name, blog=request.user.blog).first()
        print(name)
        if not obj and name != "":
            models.Category.objects.create(name=name, blog=request.user.blog)
            return redirect('/backend')
        else:
            return HttpResponse("该分类已经存在<hr>返回<a href='/backend/'>后台管理</a>")
    return render(request, 'backend/add_category.html', locals())


def category_update(request, id):
    category_id = models.Category.objects.filter(pk=id).first()
    if request.method == "POST":
        name = request.POST.get('name')
        obj = models.Category.objects.filter(name=name, blog=request.user.blog).first()
        if not obj and name != "":
            models.Category.objects.filter(pk=id).update(name=name, blog=request.user.blog)
            return redirect('/backend')
        else:
            return HttpResponse("该分类已经存在<hr>返回<a href='/backend/'>后台管理</a>")
    return render(request, 'backend/update_category.html', locals())


@login_required
def category_delete(request, delete_id):
    models.Category.objects.filter(pk=delete_id).delete()
    return redirect('/backend')


@login_required
def add_article(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'html.parser')
        # 获取所有数据
        for tag in soup.find_all():  # 获取标签字符串所有的标签对象
            # print(tag.name)
            if tag.name == "script":
                # 针对script标签，直接删除标签
                tag.decompose()
        # 文章简介,先直接切取150个字符
        # desc = content[0:150]
        # 2截取文本150个
        desc = soup.text[0:150] + "..."
        if content == "" or title == "":
            return redirect('/add/article/')
        else:
            Article_obj = models.Article.objects.create(
                title=title,
                content=str(soup),
                desc=desc,
                category_id=category_id,
                blog=request.user.blog
            )
            # 文章和标签关系表,半自动因此需手动操作
            article_obj_list = []
            for i in tag_id_list:
                article_obj_list.append(models.Article_Tag(article=Article_obj, tag_id=i))  # 生成对象并添加到列表

            # 批量插入数据
            models.Article_Tag.objects.bulk_create(article_obj_list)
            # 跳转到后台管理页面
            return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, 'backend/add_article.html', locals())


def upload_image(request):
    # 用户写文章上传的图片也算静态资源 也应该放在media文件夹下
    back_dic = {'error': 0, }  # 先提前定义返回给编辑器的数据格式
    if request.method == "POST":
        # 获取用户上传的图片对象
        # print(request.FILES)
        file_obj = request.FILES.get('imgFile')
        # 手动拼接存储文件的路径
        file_dir = os.path.join(settings.BASE_DIR, 'media', 'article_img')
        # 优化操作 先判断当前文件夹是否存在 不存在则自动创建
        if not os.path.isdir(file_dir):
            os.mkdir(file_dir)  # 创建一层目录结构  article_img
        # 拼接图片的完整路径
        file_path = os.path.join(file_dir, file_obj.name)
        with open(file_path, 'wb') as f:
            for line in file_obj:
                f.write(line)
        back_dic['url'] = '/media/article_img/%s' % file_obj.name
    return JsonResponse(back_dic)


@login_required
def set_avatar(request):
    if request.method == "POST":
        file_obj = request.FILES.get('avatar')
        # models.UserInfo.objects.filter(pk=request.user.pk).update(avatar=file_obj)  #不会再自动加avatar前缀
        user_obj = request.user
        user_obj.avatar = file_obj
        user_obj.save()
        # 1自己手动加前缀
        # 2换一种更新方式
        return redirect('/')
    blog = request.user.blog
    username = request.user.username
    return render(request, 'set_avatar.html', locals())


@login_required
def article_delete(request, delete_id):
    models.Article.objects.filter(pk=delete_id).delete()
    return redirect('/backend/')


@login_required
def update_article(request, edit_id):
    edit_obj = models.Article.objects.filter(pk=edit_id).first()
    article = models.Article.objects.filter(id=edit_id).first()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'html.parser')
        # 获取所有的数据
        for tag in soup.find_all():  # 获取标签字符串所有的标签对象
            # print(tag.name)
            if tag.name == "script":
                # 针对script标签，直接删除标签
                tag.decompose()
        desc = soup.text[0:150] + "..."
        if content == "" or title == "":
            return redirect('/add/article/')
        else:
            Article_obj = models.Article.objects.filter(pk=edit_id).update(
                title=title,
                content=str(soup),
                desc=desc,
                category_id=category_id,
                blog=request.user.blog
            )
            models.Article_Tag.objects.filter(article__id=edit_id).delete()  # 先删除，后创建
            article_obj_list = []
            for i in tag_id_list:
                article_obj_list.append(models.Article_Tag(article_id=edit_id, tag_id=i))  # 生成对象并添加到列表
            # 批量插入数据
            models.Article_Tag.objects.bulk_create(article_obj_list)
            # 跳转到后台管理页面
            return redirect('/backend/')

    category_list = models.Category.objects.filter(blog=request.user.blog)
    tag_list = models.Tag.objects.filter(blog=request.user.blog)

    return render(request, 'backend/update_article.html', locals())

# 记录日志+分页
# def log(request):
#     log_num = models.Log.objects.count()
#     page_num_int = int(request.GET.get('page', 1))
#     log_list = models.Log.objects.all()
#     paginator = Paginator(log_list, 10)
#     if paginator.num_pages > 9:
#         if page_num_int - 4 < 1:
#             page_range = range(1, 9)
#         elif page_num_int + 4 > paginator.num_pages:
#             page_range = range(paginator.num_pages - 8, paginator.num_pages + 1)
#         else:
#             page_range = range(page_num_int - 4, page_num_int + 4)
#     else:
#         page_range = paginator.page_range
#     page = paginator.page(page_num_int)
#     return render(request, 'Log.html',
#                   {'page_range': page_range, 'page': page, 'page_num_int': page_num_int, 'log_num': log_num, 'start': 1,
#                    'end': paginator.num_pages})
