from django.forms import ModelForm
from .models import Author, Category, Post, PostCategory, User

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'publicationType', 'publicationTitle', 'publicationText', 'postCategory']


class PersonForm(ModelForm):
    class Meta:
        model = User
        fields = ['username']


class AuthorForm(ModelForm):
    class Meta:
        model = Author
        fields = ['authorUser']


class CategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = ['catName']