# _*_coding:utf_8_*_
# @Time :2021/4/288:33
# Author :焕
# @File :forms.py
# 引入表单类
from django import forms
# 引入文章模型
from .models import ArticlePost

# 写文章的表单类
class ArticlePostForm(forms.ModelForm):
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'body', 'tags', 'avatar')