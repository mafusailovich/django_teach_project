from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category


def user_notification(post_id, post_head, post_text):
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
                                         'category': ','.join(cat_list), 'text': post_text, 'id':post_id} )
        msg = EmailMultiAlternatives(
            subject=f'Уведомление о подписке',
            body=f'Здравствуйте, {subscriber.username}. Появилась новая статья в вашем любимом разделе.',
            from_email='test1@sch1935.site',
            to=[subscriber.email],
        )
        msg.attach_alternative(html_content, "text/html")

        msg.send()

