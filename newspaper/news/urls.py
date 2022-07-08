from django.urls import path
from .views import upgrade_me, IndexView, AuthorCreateView, CategoryCreateView, PersonCreateView, PostUpdateView, PostsList, PostListSearch, PostCreateView, PostDetailView, PostDeleteView
from django.contrib import admin


urlpatterns = [
    path('', PostsList.as_view(), name='main'),
    path('search/', PostListSearch.as_view(), name='post_search'),
    path('add/', PostCreateView.as_view(), name='post_create'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<int:pk>/edit/', PostUpdateView.as_view(), name='post_update'),
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('person_create/', PersonCreateView.as_view(), name='person_create'),
    path('author_create/', AuthorCreateView.as_view(), name='author_create'),
    path('category_create/', CategoryCreateView.as_view(), name='category_create'),
    path('authorised_user/', IndexView.as_view(), name='authorised_user'),
    path('authorised_user/upgrade/', upgrade_me, name = 'upgrade'),
]