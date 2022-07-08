# from django.shortcuts import render
from django.views.generic import FormView, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib.auth.models import Group
from django.contrib.auth.mixins import PermissionRequiredMixin

from .forms import CategoryForm, PostForm, PersonForm, AuthorForm
from .models import Post, PostCategory
from .filters import PostFilter


class PostsList(ListView):
    model = Post
    template_name = 'news.html'
    context_object_name = 'news'
    queryset = Post.objects.filter(publicationType='NI').order_by('-publicationDate')
    paginate_by = 10


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post_categories'] = PostCategory.objects.all()
        return context


class PostCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    template_name = 'post_create.html'
    form_class = PostForm


class PostListSearch(ListView):
    model = Post
    template_name = 'news_search.html'
    context_object_name = 'news_search'
    queryset = Post.objects.filter(publicationType='NI').order_by('-publicationDate')
    paginate_by = 5

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset())
    #     return context
    
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
