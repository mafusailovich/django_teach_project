from django import forms
from .models import Post
from django.core.exceptions import ValidationError
from datetime import datetime


class PostForm(forms.ModelForm):
    post_head = forms.CharField(min_length=5, label='Название статьи/новости')
    post_text = forms.CharField(widget=forms.Textarea,label='Текст')

    class Meta:
        model = Post
        fields = [
            'post_head',
            'post_text',
            'category'
        ]

    def clean(self):

        cleaned_data = super().clean()
        post_text = cleaned_data.get("post_text")
        post_head = cleaned_data.get("post_head")

        if post_head == post_text:
            raise ValidationError(
                "Описание не должно быть идентично названию."
            )

        return cleaned_data
