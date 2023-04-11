from django.db import models
from ckeditor_uploader.fields import RichTextUploadingField

class Article(models.Model):
    """
    Модель "Статья"

    Attributes:
        title: Наименование
        content: Основной контент
        created_at: Дата создания
        updated_at: дата изменения
        is_published: отображается ли на сайте
    """
    title = models.CharField(max_length=255)
    content = RichTextUploadingField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)