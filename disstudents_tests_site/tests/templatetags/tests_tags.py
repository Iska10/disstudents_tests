from django import template
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
        category.tests = Test.objects.filter(category=category)
        categories.append(category)
    return categories
