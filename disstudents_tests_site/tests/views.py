from django.contrib.auth import authenticate, logout as do_logout, login as do_login
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from tests.forms import LoginForm, AnswerForm
from tests.models import *


# главная страница сайта
def index(request):
    return render(request, 'tests/index.html', {'title': 'Главная'})


# страница статьи
def show_article(request, article_id):
    # получаем статью и проверяем что она опубликована на сайте
    article = get_object_or_404(Article, pk=article_id, is_published=True)
    return render(request, 'tests/article.html', {
        'title': article.title, 'article': article
    })


# страница теста
def show_test(request, test_id):

    # получаем данные текущей сессии
    is_testing = request.session.get('is_testing', False)
    test_current_id = request.session.get('test_id', False)
    question_id = request.session.get('question_id', False)

    # если тестирование уже проходит и юзер пытается зайти на главную страницу теста
    if is_testing and test_current_id and question_id and test_current_id == test_id:
        # делаем редирект на страницу текущего вопроса
        return redirect('question', test_id)

    # получаем данные по тесту и проверяем что его категория опубликована
    test = get_object_or_404(Test, pk=test_id, category__is_published=True)
    return render(request, 'tests/test.html', {
        'title': test.title, 'test': test, 'is_testing': is_testing
    })


# метод для очистки данных (о прохождении теста) для текущей сессии
def clear_test(request):
    request.session.pop("test_id", None)
    request.session.pop("is_testing", None)
    request.session.pop("question_id", None)
    request.session.pop("question_number", None)
    request.session.pop("answers", None)


# страница вопроса теста
@login_required
def show_question(request, test_id):
    # начать новый тест (не закончив другой)
    if test_id != request.session.get('test_id', False):
        clear_test(request)

    # определяем текущий вопрос
    saved_question = request.session.get('question_id', False)
    if not saved_question:
        # если он не сохранен - значит тест только начался (берем 1-й вопрос)
        questions = Question.objects.filter(test=test_id, test__category__is_published=True)
        if not questions:
            # проверяем что в тесте вообще есть вопросы
            return redirect('index')
        question = questions[0]
    else:
        # иначе достаем текущий вопрос
        question = get_object_or_404(Question, pk=saved_question, test__category__is_published=True)

    # выставляем статус что тестирование проходит
    request.session['is_testing'] = True
    request.session['test_id'] = test_id
    request.session['question_id'] = question.id

    # узнаем порядковый номер текущего вопроса
    number = request.session.get('question_number', 1)
    total = Question.objects.filter(test=test_id).count()

    # отрисовываем страницу с текущим вопросом
    return render(request, 'tests/question.html', {
        'title': question.test.title, 'question': question, 'number': number,
        'total': total, 'width': int(number / total * 100),
        'answers': Answer.objects.filter(question=question.id)
    })


# логика обработки ответа на вопрос в тесте
def make_answer(request):

    # проверяем что была отправлена форма
    form = AnswerForm(request.POST)
    if request.method != 'POST':
        return redirect('index')
    if not form.is_valid():
        # если ответ не был выбран - делаем возврат на ту же страницу вопроса
        return redirect('question', request.session.get('test_id'))

    # сохраняем ответ пользователя
    question_id = request.session.get('question_id', False)
    answers = request.session.get('answers', {})
    answers[question_id] = form.cleaned_data['answer']
    request.session['answers'] = answers

    # инкриминируем порядковый номер вопроса
    number = request.session.get('question_number', 1)
    number += 1
    request.session['question_number'] = number

    # все вопросы теста
    test = request.session.get('test_id')
    questions = Question.objects.filter(test=test)
    if number <= questions.count():
        # если тест не закончился - определяем следующий вопрос
        next_question = questions[number - 1]
        request.session['question_id'] = next_question.id
        return redirect('question', test)

    # иначе - считаем результат
    user_result = 0
    test_answers = Answer.objects.filter(question__in=questions, is_correct=True)
    for q, answer in answers.items():
        correct_answer = test_answers.filter(question=q)
        if correct_answer.exists() and correct_answer[0].id == answer:
            user_result += 1

    # сохраняем результат в базу данных
    user_result_created = UserResult(
        user=request.user, test_id=int(test),
        result=int(user_result/questions.count()*100)
    )
    user_result_created.save()

    # сохраняем ответы пользователя на каждый вопрос
    for q, answer in answers.items():
        UserAnswer(
            user_result=user_result_created, question_id=q, answer_id=answer
        ).save()

    # очищаем данные о текущем прохождении теста и отправляем на страницу результата
    clear_test(request)
    return redirect('show_result', test, user_result_created.id)


# страница результатов прохождения теста
@login_required
def result(request, test_id, result_id):
    # получаем результаты заданного теста для текущего пользователя
    user_result = get_object_or_404(
        UserResult, pk=result_id, user=request.user, test=test_id
    )
    answers = []
    i = 0
    correct = 0

    for answer in UserAnswer.objects.filter(
        user_result=user_result
    ):
        # выставляем каждому ответу/вопросу порядковый номер
        i += 1
        answer.num = i
        # и выставляем признак каждому ответу - был ли он правильный
        try:
            answer.correct = Answer.objects.get(
                question=answer.question,
                is_correct=True
            )
            answer.is_correct = answer.correct.id == answer.answer_id
        except Answer.DoesNotExist:
            answer.is_correct = False

        if answer.is_correct:
            correct += 1
        answers.append(answer)

    # определяем результирующее сообщение
    message = ''
    for m in ResultMessage.objects.all():
       if m.result_from <= user_result.result <= m.result_to:
           message = m

    # выводим страницу с результатами по тесту
    return render(request, 'tests/result.html', {
        'result': user_result, 'title': user_result.test.title,
        'answers': answers, 'result_message': message,
        'total': len(answers), 'correct': correct
    })


# страница профиля пользователя
@login_required
def show_profile(request):
    results = []
    # получаем все результаты всех прохождений тестов пользователя
    for res in UserResult.objects.filter(user=request.user).order_by('-completed_at'):
        try:
            res.correct = 0
            answers = UserAnswer.objects.filter(user_result=res)
            res.total = answers.count()
            for answer in answers:
                answer.correct = Answer.objects.get(
                    question=answer.question,
                    is_correct=True
                )
                # в пределах теста для каждого ответа определяем был ли он правильный
                # и считаем общее кол-во правильных ответов
                answer.is_correct = answer.correct.id == answer.answer_id
                if answer.is_correct:
                    res.correct += 1
        except Answer.DoesNotExist:
            pass
        results.append(res)

    # отображаем страницу профиля
    return render(request, 'tests/profile.html', {
        'title': 'Результаты',
        'results': results
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


# обработка страницы 404 ошибки (не найдено)
def page_not_found(request, exception):
    return render(request, 'tests/404.html')

