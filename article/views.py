import markdown
# 引入redirect重定向模块
from django.shortcuts import render, redirect
# 引入HttpResponse
from django.http import HttpResponse

# 导入数据模型ArticlePost
from django.views import View

from .forms import ArticlePostForm
from .models import ArticlePost
# 引入User模型
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
# 引入分页模块
from django.core.paginator import Paginator
from django.db.models import Q
from comment.models import Comment
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView
from .models import ArticleColumn
from comment.forms import CommentForm

def article_list(request):
    # 从 url 中提取查询参数
    search = request.GET.get('search')
    order = request.GET.get('order')
    column = request.GET.get('column')
    tag = request.GET.get('tag')
    user = request.GET.get('user')


    # 初始化查询集
    article_list = ArticlePost.objects.all()
    # 搜索查询集
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(body__icontains=search)
        )
    else:
        search = ''

    # 栏目查询集
    if column is not None and column.isdigit():
        article_list = article_list.filter(column=column)

    # 标签查询集
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 作者查询集
    if user:
        article_list = article_list.filter(user=user)

    # 查询集排序
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')

    paginator = Paginator(article_list, 5)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 需要传递给模板（templates）的对象
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)
# 文章详情
def article_detail(request, id):

    article = ArticlePost.objects.get(id=id)
    # 取出文章评论
    comments = Comment.objects.filter(article=id)
    # 浏览量 +1
    article.total_views += 1
    article.save(update_fields=['total_views'])
    # 修改 Markdown 语法渲染
    md = markdown.Markdown(
                                     extensions=[
                                         # 包含 缩写、表格等常用扩展
                                         'markdown.extensions.extra',
                                         # 语法高亮扩展
                                         'markdown.extensions.codehilite',
                                         # 目录扩展
                                         'markdown.extensions.toc',
                                     ])
    article.body = md.convert(article.body)
    comment_form = CommentForm()
    # 添加comments上下文
    context = {'article': article, 'toc': md.toc, 'comments': comments,
               'comment_form': comment_form,
               }

    return render(request, 'article/detail.html', context)

# 检查登录
@login_required(login_url='/userprofile/login/')
# 写文章的视图
def article_create(request):
    # 判断用户是否提交数据
    if request.method == "POST":
        article_post_form = ArticlePostForm(request.POST, request.FILES)

        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存数据，但暂时不提交到数据库中
            new_article = article_post_form.save(commit=False)
            # 此时请重新创建用户，并传入此用户的id
            new_article.author = User.objects.get(id=request.user.id)

            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])

            # 将新文章保存到数据库中
            new_article.save()
            article_post_form.save_m2m()
            # 完成后返回到文章列表
            return redirect("article:article_list")
        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    # 如果用户请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        # 返回模板
        return render(request, 'article/create.html', context)


# 删除文章，此方式有 csrf 攻击风险
# 删文章
def article_delete(request, id):
    # 根据 id 获取需要删除的文章
    article = ArticlePost.objects.get(id=id)
    # 调用.delete()方法删除文章
    article.delete()
    # 完成删除后返回文章列表
    return redirect("article:article_list")

# 安全删除文章
def article_safe_delete(request, id):
    if request.method == 'POST':
        article = ArticlePost.objects.get(id=id)
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("仅允许post请求")

# 介绍自己
def article_about(request):
    return render(request, 'article/about.html')


# 更新文章
def article_update(request, id):
    """
    更新文章的视图函数
    通过POST方法提交表单，更新titile、body字段
    GET方法进入初始表单页面
    id： 文章的 id
    """

    # 获取需要修改的具体文章对象
    article = ArticlePost.objects.get(id=id)
    # 过滤非作者的用户
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")
    # 判断用户是否为 POST 提交表单数据
    if request.method == "POST":
        # 将提交的数据赋值到表单实例中
        article_post_form = ArticlePostForm(data=request.POST)
        # 判断提交的数据是否满足模型的要求
        if article_post_form.is_valid():
            # 保存新写入的 title、body 数据并保存
            article.title = request.POST['title']
            article.body = request.POST['body']

            if request.POST['column'] != 'none':
                article.column = ArticleColumn.objects.get(id=request.POST['column'])
            else:
                article.column = None
            if request.FILES.get('avatar'):
                article.avatar = request.FILES.get('avatar')

            article.tags.set(*request.POST.get('tags').split(','), clear=True)

            article.save()
            # 完成后返回到修改后的文章中。需传入文章的 id 值
            return redirect("article:article_detail", id=id)

        # 如果数据不合法，返回错误信息
        else:
            return HttpResponse("表单内容有误，请重新填写。")

    # 如果用户 GET 请求获取数据
    else:
        # 创建表单类实例
        article_post_form = ArticlePostForm()
        # 赋值上下文，将 article 文章对象也传递进去，以便提取旧的内容
        context = { 'article': article, 'article_post_form': article_post_form }
        # 将响应返回到模板中
        columns = ArticleColumn.objects.all()
        context = {
            'article': article,
            'article_post_form': article_post_form,
            'columns': columns,
            'tags': ','.join([x for x in article.tags.names()]),
        }
        return render(request, 'article/update.html', context)



class ArticleDetailView(DetailView):
    """
    文章详情类视图
    """
    queryset = ArticlePost.objects.all()
    context_object_name = 'article'
    template_name = 'article/detail.html'

    def get_object(self):
        """
        获取需要展示的对象
        """
        # 首先调用父类的方法
        obj = super(ArticleDetailView, self).get_object()
        # 浏览量 +1
        obj.total_views += 1
        obj.save(update_fields=['total_views'])
        return obj

class ArticleCreateView(CreateView):
    model = ArticlePost

    fields = '__all__'
    # 或者只填写部分字段，比如：
    # fields = ['title', 'content']
    template_name = 'article/create_by_class_view.html'

# 点赞数 +1
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = ArticlePost.objects.get(id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')


def article_list_example(request):
    """
    与下面的类视图做对比的函数
    简单的文章列表
    """
    if request.method == 'GET':
        articles = ArticlePost.objects.all()
        context = {'articles': articles}
        return render(request, 'article/list.html', context)



class ContextMixin:
    """
    Mixin
    """
    def get_context_data(self, **kwargs):
        # 获取原有的上下文
        context = super().get_context_data(**kwargs)
        # 增加新上下文
        context['order'] = 'total_views'
        return context


class ArticleListView(ContextMixin, ListView):
    """
    文章列表类视图
    """
    # 查询集的名称
    context_object_name = 'articles'
    # 模板
    template_name = 'article/list.html'

    def get_queryset(self):
        """
        查询集
        """
        queryset = ArticlePost.objects.filter(title='Python')
        return queryset
