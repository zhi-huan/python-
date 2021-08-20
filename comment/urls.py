# _*_coding:utf_8_*_
# @Time :2021/4/3010:11
# Author :焕
# @File :urls.py
from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    # 发表评论
    path('post-comment/<int:article_id>/', views.post_comment, name='post_comment'),
    #处理二级回复
    path('post-comment/<int:article_id>/<int:parent_comment_id>', views.post_comment, name='comment_reply'),
    ]