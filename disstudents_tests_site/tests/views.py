from django.contrib.auth import authenticate, logout as do_logout, login as do_login
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from tests.forms import LoginForm
from tests.models import *


# главная страница сайта
def index(request):
    return render(request, 'tests/index.html', {'title': 'Главная'})


# страница статьи
def show_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id, is_published=True)
    return render(request, 'tests/article.html', {
        'title': article.title, 'article': article
    })


# логика авторизации
def login(request):
    # если юзер уже авторизован - выходим
    if request.user.is_authenticated:
        return redirect('logout')

    # инициализируем объект формы
    form = LoginForm()

    if request.method == 'POST':
        # если форма была отправлена - заполняем объект данным из POST запроса
        form = LoginForm(request.POST)

        if form.is_valid():
            # валидируем форму
            try:
                # если юзер ввел правильные логин и пароль - авторизуем
                user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                if user is not None:
                    do_login(request, user)
                    # и отправляем на главную страницу
                    return redirect('index')
                else:
                    form.add_error(None, 'Неверные данные!')
            except Exception as e:
                print(str(e))
                form.add_error(None, 'Ошибка при авторизации. Пожалуйста, обратитесь к администратору')
        else:
            form.add_error(None, 'Неверные данные!')

    # иначе отображаем страницу с авторизацией
    return render(request, 'tests/login.html', {'form': form})


# выход (деавторизация)
def logout(request):
    do_logout(request)
    return redirect('index')


def page_not_found(request, exception):
    return render(request, 'tests/404.html')

