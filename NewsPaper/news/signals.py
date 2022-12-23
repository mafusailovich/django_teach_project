from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from datetime import datetime
from .models import Post, Category, User, PostCategory
#from .func import user_notification
from .tasks import notification


def notify_created(sender, instance, action, **kwargs):
    if action == 'post_add':
        return notification.delay(instance.id, instance.post_head, instance.post_text)
        #user_notification(instance.id, instance.post_head, instance.post_text)


@receiver(post_save, sender=Post)
def notify_subscribers(sender, instance, created, **kwargs):
    if created:
        return m2m_changed.connect(notify_created, sender=PostCategory)
    else:
        #user_notification(instance)
        return notification.delay(instance.id, instance.post_head, instance.post_text)

