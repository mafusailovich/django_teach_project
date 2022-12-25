from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver
from datetime import datetime
from .models import Post, PostCategory, User, Author
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


#если автора добавляют в группу authors, то он должен стать автором, т.е. добавить объект Author из соответствующей модели

@receiver(m2m_changed, sender=User.groups.through)
def add_author(sender, instance, action, pk_set, **kwargs):
    try:
        if action == 'post_add' and instance.name == 'authors':
            if not Author.objects.filter(username=User.objects.get(pk=list(pk_set)[0])).exists():
                Author.objects.create(username=User.objects.get(pk=list(pk_set)[0]))
                print(instance)
    except AttributeError:
        if action == 'post_add':
            if not Author.objects.filter(username=User.objects.get(pk=instance.id)).exists():
                Author.objects.create(username=User.objects.get(pk=instance.id))
                print(instance)
