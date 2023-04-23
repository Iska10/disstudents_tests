from django.contrib import admin
from django.forms import TextInput
from .models import *
from django.utils.safestring import mark_safe
from admin_auto_filters.filters import AutocompleteFilter
import nested_admin
from django.contrib.admin import AdminSite, StackedInline
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from admin_numeric_filter.admin import NumericFilterModelAdmin, SingleNumericFilter, RangeNumericFilter

# переопределяем класс AdminSite чтобы определить свой метод сортировки разделов
# по-умолчанию - по алфавиту. делаем так - чтобы по мере добавления сущностей в этом файле
class MyAdminSite(AdminSite):

    def get_app_list(self, request):
        """
        Return a sorted list of all the installed apps that have been
        registered in this site.
        """
        app_dict = self._build_app_dict(request)

        # Sort the apps alphabetically.
        app_list = sorted(app_dict.values(), key=lambda x: x['name'].lower())

        # Sort the models alphabetically within each app.
        #for app in app_list:
        #    app['models'].sort(key=lambda x: x['name'])

        return app_list


admin.site = MyAdminSite()


# определяем поведение сущности "статья" в админке
class ArticleAdmin(admin.ModelAdmin):
    fields = ('title', 'image', 'image_preview', 'content', 'is_published')
    list_display = ('id', 'title', 'image_preview', 'is_published', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title')
    readonly_fields = ('image_preview', 'created_at', 'updated_at')

    # отрисовываем загруженное изображение в списке и на форме
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                '<img src="{0}" width="50" height="50" style="object-fit:contain" />'.format(obj.image.url))
        else:
            return '(Не загружено)'
    image_preview.short_description = 'Изображение'


admin.site.register(Article, ArticleAdmin)


# определяем поведение сущности "категория" в админке
class CategoryAdmin(admin.ModelAdmin):
    fields = ('title', 'is_published')
    list_display = ('id', 'title', 'is_published', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title')
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(Category, CategoryAdmin)


# определяем фильтр по категориям
class CategoryFilter(AutocompleteFilter):
    title = 'Категория' # display title
    field_name = 'category' # name of the foreign key field


# определяем функционал для inline-редактирования связи "вопрос-ответ-тест"
class AnswerInline(nested_admin.NestedStackedInline):
    model = Answer
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '150'})}
    }


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '150'})}
    }
    extra = 0
    inlines = [AnswerInline]


# определяем поведение сущности "тест" в админке
class TestAdmin(nested_admin.NestedModelAdmin):
    inlines = [QuestionInline]
    fields = ('title', 'category', 'description', 'is_published')
    list_select_related = ('category',)
    list_display = ('id', 'title', 'category', 'is_published', 'created_at', 'updated_at')
    list_display_links = ('id', 'title')
    search_fields = ('id', 'title', 'category__title')
    readonly_fields = ('created_at', 'updated_at')
    list_filter = (
        CategoryFilter,
        ('is_published', admin.BooleanFieldListFilter)
    )


admin.site.register(Test, TestAdmin)


# определяем фильтр по тестам
class TestFilter(AutocompleteFilter):
    title = 'Тест' # display title
    field_name = 'test' # name of the foreign key field


# определяем поведение сущности "вопросы к тестам" в админке
# class QuestionAdmin(admin.ModelAdmin):
#     inlines = [AnswerInline]
#     fields = ('test', 'text', 'description')
#     list_select_related = ('test',)
#     list_display = ('id', 'test', 'text_preview', 'created_at', 'updated_at')
#     list_display_links = ('id', 'text_preview')
#     search_fields = ('id', 'text', 'test__title')
#     readonly_fields = ('created_at', 'updated_at')
#     list_filter = (TestFilter, )
#
#     # сокращаем текст вопроса при выводе в списках
#     def text_preview(self, obj):
#         if obj.text:
#             if len(obj.text) > 75:
#                 return obj.text[:75] + "..."
#             else:
#                 return obj.text
#         return ""
#     text_preview.short_description = 'вопрос'
#
#
# admin.site.register(Question, QuestionAdmin)


# class QuestionFilter(AutocompleteFilter):
#     title = 'Вопрос' # display title
#     field_name = 'question' # name of the foreign key field
#
#
# class AnswerAdmin(admin.ModelAdmin):
#     fields = ('question', 'text', 'is_correct')
#     list_select_related = ('question',)
#     list_display = ('id', 'question', 'text', 'is_correct', 'created_at', 'updated_at')
#     list_display_links = ('id', 'text')
#     search_fields = ('id', 'text')
#     readonly_fields = ('created_at', 'updated_at')
#     list_filter = (QuestionFilter, )
#
#
# admin.site.register(Answer, AnswerAdmin)

# определяем фильтр по пользователям
class UserFilter(AutocompleteFilter):
    title = 'Пользователь' # display title
    field_name = 'user' # name of the foreign key field


# определяем функционал для inline-редактирования связи "вопрос-ответ-тест"
class UserAnswerInline(StackedInline):
    model = UserAnswer
    extra = 0
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size': '150'})}
    }

    # логика выбора доступных вопросов и ответов только из завершенного пользователем теста
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        user_result_id = request.resolver_match.kwargs.get('object_id')
        if user_result_id:
            user_result = UserResult.objects.get(pk=user_result_id)
            questions = Question.objects.filter(test__id=user_result.test_id)
            if db_field.name == "question":
                kwargs["queryset"] = questions
            if db_field.name == "answer":
                kwargs["queryset"] = Answer.objects.filter(question_id__in=questions)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# определяем поведение сущности "результаты пользователей" в админке
class UserResultAdmin(NumericFilterModelAdmin):
    fields = ('user', 'test', 'result')
    list_display_links = ('result', )
    list_select_related = ('user', 'test')
    list_display = ('user', 'test', 'completed_at', 'result')
    search_fields = ('user__username', 'test__title')
    list_filter = (
        UserFilter, TestFilter,
        ('result', RangeNumericFilter),
        ('result', SingleNumericFilter)
    )

    # запрещаем изменять сущность "ответы пользователя" при создании сущности "результаты пользователя"
    def get_inlines(self, request, obj=None):
        if obj:
            return [UserAnswerInline]
        else:
            return []

    # def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
    #     context.update({
    #         'show_save': False,
    #         'show_save_and_continue': False,
    #         'show_save_and_add_another': False,
    #         'show_delete': False
    #     })
    #     return super().render_change_form(request, context, add, change, form_url, obj)


admin.site.register(UserResult, UserResultAdmin)

#Регистрируем стандартные модели
admin.site.register(Group, GroupAdmin)
admin.site.register(User, UserAdmin)
