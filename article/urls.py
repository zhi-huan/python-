# _*_coding:utf_8_*_
# @Time :2021/4/2717:15
# Author :焕
# @File :urls.py
# 引入path
from django.urls import path

# 正在部署的应用的名称
from article import views

app_name = 'article'

urlpatterns = [
    path('article-list/', views.article_list, name='article_list'),
    path('article-about/', views.article_about, name='article_about'),
    path('article-list/', views.article_list_example, name='article_list_example'),
    # 文章详情
    path('article-detail/<int:id>/', views.article_detail, name='article_detail'),
    # 写文章
    path('article-create/', views.article_create, name='article_create'),
    # 删除文章
    path('article-delete/<int:id>/', views.article_delete, name='article_delete'),
    #安全删除文章
    path(
        'article-safe-delete/<int:id>/',
        views.article_safe_delete,
        name='article_safe_delete'
    ),
    # 更新文章
    path('article-update/<int:id>/', views.article_update, name='article_update'),
    # 详情类视图
    path('detail-view/<int:pk>/', views.ArticleDetailView.as_view(), name='detail-view'),
    # 创建类视图
    path('create-view/', views.ArticleCreateView.as_view(), name='create_view'),
    # 点赞 +1
    path(
        'increase-likes/<int:id>/',
        views.IncreaseLikesView.as_view(),
        name='increase_likes'
    ),
    # 列表类视图
    path('list-view/', views.ArticleListView.as_view(), name='list_view'),

]