import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from news.models import User,Post
from datetime import datetime,timedelta
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


def my_job():
    # Your job processing logic here...
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


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            my_job,
            trigger=CronTrigger(day_of_week="tue", hour="18", minute="16"),#(day="*/7"),  # Every 10 seconds
            id="my_job",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")