from django import template
from django.db.models import Count

from tests.models import *

register = template.Library()


# получить список всех опубликованных на сайте статей
@register.simple_tag()
def get_articles():
    return Article.objects.filter(is_published=True)


# получить список категорий тестов
@register.simple_tag()
def get_categories():
    categories = []
    for category in Category.objects.filter(is_published=True):
        # добавляем только те тесты, которые опубликованы
        # и у которых есть хотя бы 1 вопрос и ответ
        category.tests = Test.objects.annotate(num_questions=Count('question'), num_answers=Count('question__answer'))\
            .filter(is_published=True, category=category, num_questions__gte=1, num_answers__gte=1)
        categories.append(category)
    return categories
