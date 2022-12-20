from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save,m2m_changed,pre_save
from django.dispatch import receiver
from datetime import datetime
from .models import Post, Category, User, PostCategory


def user_notification(instance):
    cat_list = Post.objects.get(pk=instance.id).category.values()
    cat_list = [cat_list[i]['name'] for i in range(len(cat_list))]  # получаем список категорий
    subscribers_list = []
    for cat_name in cat_list:
        subscribers = Category.objects.get(name=cat_name).subscribers.all()  # выбираем подписчиков данной категории
        for subscriber in subscribers:
            subscribers_list.append(subscriber)
    subscribers_list = set(subscribers_list)
    for subscriber in subscribers_list:
        html_content = render_to_string('email_create.html',
                                        {'username': subscriber.username, 'head': instance.post_head,
                                         'category': ','.join(cat_list), 'text': instance.post_text, 'id':instance.id} )
        msg = EmailMultiAlternatives(
            subject=f'Уведомление о подписке',
            body=f'Здравствуйте, {subscriber.username}. Появилась новая статья в вашем любимом разделе.',
            from_email='test1@sch1935.site',
            to=[subscriber.email],
        )
        msg.attach_alternative(html_content, "text/html")

        msg.send()


def notify_created(sender, instance, action, **kwargs):
    if action == 'post_add':
        user_notification(instance)

@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        m2m_changed.connect(notify_created, sender=PostCategory)
    else:
        user_notification(instance)


