from django.db import models
from django.contrib.auth.models import User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group
from datetime import datetime
from django.core.validators import MinValueValidator
from django.urls import reverse
from django.core.cache import cache
from django.utils.translation import gettext as _


POSITIONS = [('news', 'Новости'), ('post', 'Статьи')]
# Create your models here.


class Author(models.Model):
    user_rating = models.IntegerField(default=1)

    username = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True)

    def update_rating(self):
        self.user_rating = 0
        rate = 0
        for i in Post.objects.filter(author=self.username_id).values():
            rate += i['post_rating'] * 3

        c = Comment.objects.filter(in_user=self.username_id)

        for i in c.values():
            rate += i['comment_rating']

        for i in range(len(c.values())):
            for j in Comment.objects.filter(in_post=c.values()[i]['in_post_id']).values():
                rate += j['comment_rating']

        self.user_rating += rate
        if self.user_rating < 0:
            self.user_rating = 0
        self.save()

    def __str__(self):
        u = User.objects.get(author=self.username_id)
        return u.username


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, help_text=_('category_name'))
    subscribers = models.ManyToManyField(User)

    def __str__(self):
        return self.name.title()


class Post(models.Model):
    post_category = models.CharField(
        max_length=4, choices=POSITIONS, default='post')
    time_in = models.DateTimeField(auto_now_add=True)
    post_head = models.CharField(max_length=255)
    post_text = models.TextField(default='Текст отсутствует')
    post_rating = models.IntegerField(default=1)

    author = models.ForeignKey(
        Author, on_delete=models.CASCADE, default=User.objects.get(username='test').id)
    category = models.ManyToManyField(Category, through='PostCategory')

    def like(self):
        self.post_rating += 1
        self.save()

    def dislike(self):
        self.post_rating -= 1
        self.save()

    def preview(self):
        tmp_str = self.post_text[0:124] + '...'
        return tmp_str

    def __str__(self):
        return f'{self.post_head.title()}: {self.post_category.title()}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post{self.pk}')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class Comment(models.Model):
    comment_text = models.TextField(default='Текст отсутствует')
    time_in = models.DateTimeField(auto_now_add=True)
    comment_rating = models.IntegerField(default=1)

    in_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    in_user = models.ForeignKey(User, on_delete=models.CASCADE)

    def like(self):
        self.comment_rating += 1
        self.save()

    def dislike(self):
        self.comment_rating -= 1
        self.save()
