from django.forms import ModelForm
from .models import Author, Category, Post, PostCategory, User
from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

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


class BasicSignupForm(SignupForm):
    def save(self, request):
        user = super(BasicSignupForm, self).save(request)
        common_group = Group.objects.get(name='common')
        common_group.user_set.add(user)
        return user