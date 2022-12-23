from celery import shared_task
import time
from datetime import datetime,timedelta

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category, User



@shared_task
def notification(post_id, post_head, post_text):
    cat_list = Post.objects.get(pk=post_id).category.values()
    cat_list = [cat_list[i]['name'] for i in range(len(cat_list))]  # получаем список категорий
    subscribers_list = []
    for cat_name in cat_list:
        subscribers = Category.objects.get(name=cat_name).subscribers.all()  # выбираем подписчиков данной категории
        for subscriber in subscribers:
            subscribers_list.append(subscriber)
    subscribers_list = set(subscribers_list)
    for subscriber in subscribers_list:
        html_content = render_to_string('email_create.html',
                                        {'username': subscriber.username, 'head': post_head,
                                         'category': ','.join(cat_list), 'text': post_text, 'id': post_id})
        msg = EmailMultiAlternatives(
            subject=f'Уведомление о подписке',
            body=f'Здравствуйте, {subscriber.username}. Появилась новая статья в вашем любимом разделе.',
            from_email='test1@sch1935.site',
            to=[subscriber.email],
        )
        msg.attach_alternative(html_content, "text/html")

        msg.send()


@shared_task
def week_news():
    last_week_date = (datetime.now()-timedelta(days=7)).date() #дата неделей раньше
    post_week_list = Post.objects.filter(time_in__gt=last_week_date) #статьи за прошлую неделю
    user_list = set(User.objects.filter(category__isnull=False)) #только пользователи, которые подписаны
    #так как после данной фильтрации получается список с кучей одинаковых записей, то избавляюсь при помощи множества
    for user in user_list:
        user_c = user.category_set.all().values()
        user_c = [i['id'] for i in user_c]

        post_list_for_user = []
        for p in post_week_list:
            for j in p.category.values():
                if j['id'] in user_c:
                    post_list_for_user.append(p)
                    break

        html_content = render_to_string('email_create_r.html',
                                        {'username': user.username, 'posts': post_list_for_user})

        msg = EmailMultiAlternatives(
            subject=f'Список статей за неделю',
            body=f'Здравствуйте, {user.username}. Появилась новая статья в вашем любимом разделе.',
            from_email='test1@sch1935.site',
            to=[user.email],
        )
        msg.attach_alternative(html_content, "text/html")

        msg.send()
