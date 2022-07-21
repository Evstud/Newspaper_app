from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Post, Category, User
from collections.abc import Iterable
from django.template.loader import render_to_string
from django.utils.text import Truncator
from django.core.mail import EmailMultiAlternatives

@receiver(m2m_changed, sender=Post.postCategory.through)
def notify_subscribers_publication(sender, instance, **kwargs):
    article_post_cat_ids = instance.postCategory.values('id')
    categories_obj=Category.objects.all()
    categories = []
    email_list_di = []

    if isinstance(categories_obj, Iterable):
        for category in categories_obj:
            if isinstance(article_post_cat_ids, Iterable):
                for article_cat_id in article_post_cat_ids:
                    if category.id == article_cat_id.get('id'):
                        email_list_di.extend(category.subscribers.values('email'))
                        categories.append(category.catName)

            else:
                if category.id == article_post_cat_ids.get('id'):
                    email_list_di.extend(category.subscribers.values('email'))
                    categories.append(category.catName)

    else:
        if isinstance(article_post_cat_ids, Iterable):
                for article_cat_id in article_post_cat_ids:
                    if categories_obj.id == article_cat_id.get('id'):
                        email_list_di.extend(category.subscribers.values('email'))
                        categories.append(category.catName)

        else:
            if categories_obj.id == article_post_cat_ids.get('id'):
                email_list_di.extend(category.subscribers.values('email'))
                categories.append(category.catName)

    email_list = list(set([i.get('email') for i in email_list_di if i.get('email')]))
    user_objs = User.objects.all()
    email_subscribers = [user_objs.get(email=i) for i in email_list]

    for subscriber in email_subscribers:

        html_content = render_to_string(
            'news_item_created.html',
            {
                'article': instance,
                'subscribername': subscriber.username,
            }
        )
        
        truncated_text = Truncator(instance.publicationText).chars(50)
        
        msg = EmailMultiAlternatives(
            subject=f'New publication in{categories}',
            body=truncated_text,
            from_email='EvgStud@yandex.ru',
            to=[subscriber.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

  
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        html_content = render_to_string(
            'profile_created_hello.html',
            {
                'user': instance,
            }
        )
        
        msg = EmailMultiAlternatives(
            subject=f'New profile',
            body='Greetings',
            from_email='EvgStud@yandex.ru',
            to=[instance.email]
        )
        msg.attach_alternative(html_content, "text/html")
        msg.send()

