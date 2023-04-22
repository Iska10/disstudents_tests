from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('articles/<int:article_id>', show_article, name='article'),
    path('login', login, name='login'),
    path('logout', logout, name='logout')
]
