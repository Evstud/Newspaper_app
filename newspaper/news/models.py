from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Sum


class Author(models.Model):
    authorUser = models.OneToOneField(User, on_delete = models.CASCADE)
    authorRanking = models.IntegerField(default = 0)

    def update_rating(self):
        postRan = self.post_set.all().aggregate(postRanking=Sum('publicationRanking'))
        pRan = 0
        pRan += postRan.get('postRanking')

        commentRan = self.authorUser.comment_set.all().aggregate(commentRanking=Sum('commentRanking'))
        cRan = 0
        cRan += commentRan.get('commentRanking')

        self.authorRanking = pRan * 3 + cRan
        self.save()
    
    def __str__(self):
        return f'{self.authorUser.username}'


class Category(models.Model):
    catName = models.CharField(max_length = 255, unique = True)

    def __str__(self):
        return f'{self.catName}'


class Post(models.Model):
    article = 'AR'
    newsItem = 'NI'

    PUBLICATION_TYPES = [
        (article, 'Статья'),
        (newsItem, 'Новость'),
    ]

    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    publicationType = models.CharField(max_length = 2, choices = PUBLICATION_TYPES, default = article)
    publicationDate = models.DateTimeField(auto_now_add = True)
    publicationTitle = models.CharField(max_length = 255)
    publicationText = models.TextField()
    publicationRanking = models.IntegerField(default = 0)

    postCategory = models.ManyToManyField(Category, through = 'PostCategory')

    def like(self):
        self.publicationRanking += 1
        self.save()

    def dislike(self):
        self.publicationRanking -= 1
        self.save()

    def preview(self):
        return self.publicationText[0:124] + '...'
    
    def get_absolute_url(self):
        return f'/news/{self.id}'

    def __str__(self):
        return f'{self.id}{self.author.Author.authorUser.username}'
        

class PostCategory(models.Model):
    postCatPost = models.ForeignKey(Post, on_delete = models.CASCADE)
    postCatCategory = models.ForeignKey(Category, on_delete = models.CASCADE)


class Comment(models.Model):
    commentPost = models.ForeignKey(Post, on_delete = models.CASCADE)
    commentUser = models.ForeignKey(User, on_delete = models.CASCADE)
    commentText = models.TextField()
    commentDate = models.DateTimeField(auto_now_add = True)
    commentRanking = models.IntegerField(default = 0)

    def like(self):
        self.commentRanking += 1
        self.save()

    def dislike(self):
        self.commentRanking -= 1
        self.save()