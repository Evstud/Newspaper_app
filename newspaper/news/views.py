from sqlite3 import Timestamp
from django.shortcuts import render
from gc import get_objects
import imp
from os import truncate
from django.views.generic import FormView, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.mail import send_mail, EmailMultiAlternatives
from django.utils.text import Truncator
from django.core.paginator import Paginator
from datetime import date, timedelta, time, datetime
from django.contrib import messages


from django.template.loader import render_to_string

from collections.abc import Iterable

from .forms import CategoryForm, PostForm, PersonForm, AuthorForm
from .models import Post, PostCategory, User, Category, Author
from .filters import PostFilter


class CategoryDetailView(ListView):
    model = Category
    template_name = 'news_by_categories/news_by_categories.html'
    context_object_name = 'publications'
    queryset = Category.objects.all()
    paginate_by = 10
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_categories'] = PostCategory.objects.all()
        context['pk_category'] = self.kwargs['pk']
        category = Category.objects.get(id=self.kwargs['pk'])
        context['category'] = category.catName
        if self.request.user.is_authenticated:
            context['is_not_subscribed'] = not self.request.user.category_set.filter(catName=category.catName).exists()
        else: 
            context['message'] = '!!! После авторизации здесь появится кнопка для подписки на данную категорию !!!'
        return context


    def get_queryset(self):
        category = Category.objects.get(id=self.kwargs['pk'])
        publications = category.post_set.all()
        return publications
    

@login_required
def subscribe_me(request, pk):
    user = request.user
    category_for_subscribe = Category.objects.get(id=pk)
    if not request.user.category_set.filter(id=pk).exists():
        category_for_subscribe.subscribers.add(user)
    return redirect('/news/')

class PostsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.filter(publicationType='NI').order_by('-publicationDate')
    paginate_by = 10


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_categories'] = PostCategory.objects.all()
        context['author_user'] = self.request.user
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    template_name = 'post_create.html'
    form_class = PostForm
    
    
    def post(self, request, *args, **kwargs):
        author_req = request.user
        startdate = datetime.now()
        enddate = startdate - timedelta(days=1)
        all_posts_by_day = Post.objects.filter(publicationDate__range=[enddate, startdate])
        authors_id = [i.get('authorUser') for i in list(Author.objects.values('authorUser'))]
        if author_req.id in authors_id:    
            author_user = Author.objects.get(authorUser_id=author_req.id)
            author_posts_by_day = [i for i in all_posts_by_day if author_req.author.id == i.author.id]
            if len(author_posts_by_day) < 3:
                article = Post(
                    author=author_user,
                    publicationText=request.POST['publicationText'],
                    publicationType=request.POST['publicationType'],
                    publicationTitle=request.POST['publicationTitle'],
                    )
                article.save()
                pc_objs=request.POST.getlist('postCategory')
                article.postCategory.set(pc_objs)
            else:
                print('too much')

        else: 
            author_user = Author.objects.create(authorUser_id=author_req.id)
            article = Post(
                    author=author_user,
                    publicationText=request.POST['publicationText'],
                    publicationType=request.POST['publicationType'],
                    publicationTitle=request.POST['publicationTitle'],
                    )
            article.save()
            pc_objs=request.POST.getlist('postCategory')
            article.postCategory.set(pc_objs)
                  
        return redirect('/news/')



class PostListSearch(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news_search'
    queryset = Post.objects.filter(publicationType='NI').order_by('-publicationDate')
    paginate_by = 5

    
    def get_filter(self):
        return PostFilter(self.request.GET, queryset=super().get_queryset())

    def get_queryset(self):
        return self.get_filter().qs
    
    def get_context_data(self, *args, **kwargs):
        return {**super().get_context_data(*args, **kwargs), 'filter':self.get_filter()}

class PostUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = ('news.change_post', )
    template_name = 'post_create.html'
    form_class = PostForm

    def get_object(self, **kwargs):
        id = self.kwargs.get('pk')
        return Post.objects.get(pk=id)

class PostDeleteView(DeleteView):
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/news/'

class PostDetailView(DetailView):
    template_name = 'post_detail.html' 
    queryset = Post.objects.all()
    success_url = '/news/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_categories'] = PostCategory.objects.all()
        return context

@method_decorator(login_required, name='dispatch')
class PersonCreateView(CreateView):
    template_name = 'person_create.html'
    form_class = PersonForm
    success_url = '../add/'

class AuthorCreateView(CreateView):
    template_name = 'author_create.html'
    form_class = AuthorForm
    success_url = '../add/'

class CategoryCreateView(CreateView):
    template_name = 'category_create.html'
    form_class = CategoryForm
    success_url = '../add/'

class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'authorised_user.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_author'] = not self.request.user.groups.filter(name = 'authors').exists()
        context['categories_subscribed'] = self.request.user.category_set.values('catName')
        return context

@login_required
def upgrade_me(request):
    user = request.user
    author_group = Group.objects.get(name='authors')
    if not request.user.groups.filter(name='authors').exists():
        author_group.user_set.add(user)
    return redirect('/news/')


# class PerAutView(TemplateView):
#     template_name = 'person_create.html'

#     def get(self, request, *args, **kwargs):
#         person_form = PersonForm(self.request.GET or None)
#         author_form = AuthorForm(self.request.GET or None)
#         context = self.get_context_data(**kwargs)
#         context['person_form'] = person_form
#         context['author_form'] = author_form
#         return self.render_to_response(context)

# class PersonCreateView(CreateView):
#     form_class = PersonForm
#     template_name = 'person_create.html'
#     success_url = ''

#     # def post(self, request, *args, **kwargs):
#     #     person_form = self.form_class(request.POST)
#     #     # author_form = AuthorForm()
#     #     if person_form.is_valid():
#     #         person_form.save()
#     #         return self.render_to_response(
#     #             self.get_context_data(
#     #                 success=True
#     #             )
#     #         )
#     #     else:
#     #         return self.render_to_response(
#     #             self.get_context_data(
#     #                 person_form=person_form,
#     #                 # author_form=author_form
#     #             )
#     #         )

# class AuthorCreateView(CreateView):
#     form_class = AuthorForm
#     template_name = 'person_create.html'
#     success_url = ''

#     # def post(self, request, *args, **kwargs):
#     #     author_form = self.form_class(request.POST)
#     #     # person_form = PersonForm()
#     #     if author_form.is_valid():
#     #         author_form.save()
#     #         return self.render_to_response(
#     #             self.get_context_data(
#     #                 success=True
#     #             )
#     #         )
#     #     else:
#     #         return self.render_to_response(
#     #             self.get_context_data(
#     #                 author_form=author_form,
#     #                 # person_form=person_form
#     #             )
#     #         )


# class PerAutView(TemplateView):
#     person_create_form = PersonForm
#     author_create_form = AuthorForm
#     category_create_form = CategoryForm
#     template_name = 'person_create.html'

    
#     def post(self, request):
#         post_data = request.POST or None
#         person_form = self.person_create_form(post_data, prefix='post')
#         author_form = self.author_create_form(post_data, prefix='author')
#         category_form = self.category_create_form(post_data, prefix='category')

#         context = self.get_context_data(person_form=person_form, author_form=author_form, category_form=category_form)

#         if person_form.is_valid():
#             self.form_save(person_form)
#             return self.render_to_response(context)
#             # person_form.save()
#         elif author_form.is_valid():
#             self.form_save(author_form)
#             return self.render_to_response(context)
#             # author_form.save()
#         elif category_form.is_valid():
#             self.form_save(category_form)
#             return self.render_to_response(context)
#         else:
#             pass

#         return self.render_to_response(context)

#     def form_save(self, form):
#         obj = form.save()
#         messages.success(self.request, "{} saved successfully".format(obj))
#         return obj
    
#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)
