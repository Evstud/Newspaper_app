import logging
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.template.loader import render_to_string
from datetime import date, timedelta
from news.models import Post, Category, User
from collections.abc import Iterable
from django.core.mail import EmailMultiAlternatives

 
logger = logging.getLogger(__name__)

def email_sender(email_subscribers, posts_by_categories, category):
    # print(posts_by_categories)
   for subscriber in email_subscribers:
        print('ok')
        html_content = render_to_string(
            'news_by_category_one_week.html',
            {
                'posts_by_categories': posts_by_categories,
                'subscribername': subscriber.username,
                'category': category.catName
            }
        )
                        
        msg = EmailMultiAlternatives(
            subject=f'Posts in that week',
            body='kdkdk',
            from_email='EvgStud@yandex.ru',
            to=[subscriber.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send() 
 
 
# наша задача по выводу текста на экран
def weekly_news():
    #  Your job processing logic here... 
    startdate = date.today()
    enddate = startdate - timedelta(days=7)
    list_of_posts = Post.objects.filter(publicationDate__range=[enddate, startdate])
    # print(list_of_posts, enddate, startdate)
    list_of_categories = Category.objects.all()
    if isinstance(list_of_categories, Iterable):

        for category in list_of_categories:
            posts_by_categories = []
            email_subscribers = []
            emails_of_subscribers = category.subscribers.values('email')
            email_list = list(set([i.get('email') for i in emails_of_subscribers if i.get('email')]))
            user_objs = User.objects.all()
            email_subscribers = [user_objs.get(email=i) for i in email_list]

            if isinstance(list_of_posts, Iterable):

                for post in list_of_posts:
                    postCat_id_list = [i.get('id') for i in post.postCategory.values('id')]

                    if category.id in postCat_id_list:
                        posts_by_categories.append(post)

                email_sender(email_subscribers, posts_by_categories, category)

            else:
                postCat_id_list = [i.get('id') for i in list_of_posts.postCategory.values('id')]

                if category.id in postCat_id_list:
                    posts_by_categories.append(list_of_posts.publicationTitle)

                email_sender(email_subscribers, posts_by_categories, category)

    else:
        posts_by_categories = []
        email_subscribers = []
        emails_of_subscribers = list_of_categories.subscribers.values('email')
        email_list = list(set([i.get('email') for i in emails_of_subscribers if i.get('email')]))
        user_objs = User.objects.all()
        email_subscribers = [user_objs.get(email=i) for i in email_list]

        if isinstance(list_of_posts, Iterable):
            
                for post in list_of_posts:
                    postCat_id_list = [i.get('id') for i in post.postCategory.values('id')]

                    if list_of_categories.id in postCat_id_list:
                        posts_by_categories.append(post.publicationTitle)
                        
                        

                email_sender(email_subscribers, posts_by_categories, category)
        else:
            postCat_id_list = [i.get('id') for i in list_of_posts.postCategory.values('id')]

            if list_of_categories.id in postCat_id_list:
                posts_by_categories.append(list_of_posts.publicationTitle)

            email_sender(email_subscribers, posts_by_categories, category)


        



 
 
# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
 
class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        scheduler.add_job(
            weekly_news,
            trigger=CronTrigger(day_of_week="mon", hour="12", minute="00"),  # Тоже самое что и интервал, но задача тригера таким образом более понятна django
            id="weekly_news",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'weekly_news'.")
 
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
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