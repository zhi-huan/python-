# _*_coding:utf_8_*_
# @Time :2021/4/3010:09
# Author :焕
# @File :forms.py
from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']