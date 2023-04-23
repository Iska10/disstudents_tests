from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('articles/<int:article_id>', show_article, name='article'),
    path('tests/<int:test_id>', show_test, name='test'),
    path('tests/<int:test_id>/questions', show_question, name='question'),
    path('answer', make_answer, name='make_answer'),
    path('tests/<int:test_id>/result', result, name='show_result'),
    path('login', login, name='login'),
    path('logout', logout, name='logout')
]
