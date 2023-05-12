from django.contrib.auth.models import User
from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


class Article(models.Model):
    """
    Модель "Статья"

    Attributes:
        title: Наименование
        image: Изображение
        content: Основной контент
        created_at: Дата создания
        updated_at: дата изменения
        is_published: отображается ли на сайте
    """
    title = models.CharField(max_length=255, verbose_name='Наименование')
    image = models.ImageField(upload_to='images/articles/', blank=True, null=True, verbose_name='Изображение')
    description = models.TextField(blank=True, null=True, verbose_name='Краткое содержание')
    content = RichTextUploadingField(blank=True, null=True, verbose_name='Основной контент')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    is_published = models.BooleanField(default=True, verbose_name='Отображать на сайте')

    def __str__(self):
        return self.title

    def get_short_content(self):
        if self.description:
            return self.description
        if len(self.content) > 150:
            return self.content[:150] + "..."
        else:
            return self.content

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'


class Category(models.Model):
    """
    Модель "Категория тестов"

    Attributes:
        title: Наименование
        created_at: Дата создания
        updated_at: дата изменения
        is_published: отображается ли на сайте
    """
    title = models.CharField(max_length=255, verbose_name='Наименование')
    is_published = models.BooleanField(default=True, verbose_name='Отображать на сайте')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Test(models.Model):
    """
    Модель "Тест"

    Attributes:
        title: Название теста
        description: Описание теста
        category: Категория теста
        created_at: Дата создания
        updated_at: дата изменения
        is_published: отображается ли на сайте
    """
    title = models.CharField(max_length=255, verbose_name='Название')
    description = RichTextUploadingField(blank=True, null=True, verbose_name='Описание')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, verbose_name='Категория')
    is_published = models.BooleanField(default=True, verbose_name='Отображать на сайте')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


class Question(models.Model):
    """
    Модель "Вопрос"

    Attributes:
        text: Текст вопроса
        description: Подробное описание
        test: К какому тесту относится
        created_at: Дата создания
        updated_at: дата изменения
    """
    text = models.CharField(max_length=255, verbose_name='Текст вопроса')
    description = RichTextUploadingField(config_name='small', blank=True, null=True, verbose_name='Описание')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name='Тест')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        if len(self.text) > 75:
            return self.text[:75] + "..."
        else:
            return self.text

    class Meta:
        verbose_name = 'Вопрос к тесту'
        verbose_name_plural = 'Вопросы к тестам'


class Answer(models.Model):
    """
    Модель "Ответ на вопрос"

    Attributes:
        text: Текст ответа
        is_correct: является ли ответ правильным
        question: К какому вопросу относится
        created_at: Дата создания
        updated_at: дата изменения
    """
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос теста')
    text = models.CharField(max_length=255, verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    def __str__(self):
        if len(self.text) > 75:
            return self.text[:75] + "..."
        else:
            return self.text

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'


class UserResult(models.Model):
    """
    Модель "Результат пользователя"

    Attributes:
        user: пользователь
        test: тест
        completed_at: дата прохождения
        result: результат
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    test = models.ForeignKey(Test, on_delete=models.CASCADE, verbose_name='Тест')
    completed_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name='Дата прохождения')
    result = models.IntegerField(verbose_name='Результат (%)', default=0, validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])

    class Meta:
        verbose_name = 'Результат'
        verbose_name_plural = 'Результаты пользователей'


class UserAnswer(models.Model):
    """
    Модель "Ответы пользователя"

    Attributes:
        user_result: ссылка на сущность "результат прохождения теста"
        question: вопрос
        answer: ответ пользователя
    """
    user_result = models.ForeignKey(UserResult, on_delete=models.CASCADE, verbose_name='Результат')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, verbose_name='Ответ')

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователя'


class ResultMessage(models.Model):
    """
    Модель "Результирующие сообщения"

    Attributes:
        title: Заголовок результата
        message: Сообщение результата
        result_from: Градация (требуемое кол-во набранных баллов ОТ)
        result_to: Градация (требуемое кол-во набранных баллов ДО)
    """
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    message = models.TextField(blank=True, null=True, verbose_name='Сообщение')
    result_from = models.IntegerField(verbose_name='Результат от', default=0, help_text="Градация (требуемое кол-во набранных баллов ОТ)", validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])
    result_to = models.IntegerField(verbose_name='Результат до', default=0, help_text="Градация (требуемое кол-во набранных баллов ДО)", validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])

    class Meta:
        verbose_name = 'Сообщение результатов'
        verbose_name_plural = 'Сообщения результатов'

    def clean(self):
        if self.result_from > self.result_to:
            raise ValidationError("Градации некорректны")
