# Knowledge control for students with disabilities
Проект "Информационная система контроля знаний обучающихся с ограниченными возможностями здоровья"

## Требования
- [Python 3.9.x](https://www.python.org/downloads/)
- [Git](https://git-scm.com)
- [Cloudinary](https://cloudinary.com)

## Деплой проекта

### 1. Склонировать репозиторий. 
```
git clone https://github.com/Iska10/disstudents_tests.git
```
### 2. Создание виртуальной среды.
Переходим в папку с проектом и выполняем команду:
```
python -m venv venv
```
Активируем виртуальную среду:
```
.\venv\Scripts\activate
```
Подгружаем зависимости проекта (пакеты):
```
pip install -r requirements.txt
```
### 3. Настройка проекта (env, миграции, статичные файлы).

Переходим в папку приложения.
```
cd disstudents_tests_site
```

Создаем файл настроек окружения из копии:
```
cp disstudents_tests_site\.env.dist disstudents_tests_site\.env
```
*(или просто вручную скопировать файл `.env.dist` и переименовать в `.env`)*

Указываем настройки в этом файле, в том числе данные для подключения к облачному сервису-хранилищу медиа Cloudinary:
```
# при включенном дебаге - возможные ошибки выводятся
DEBUG=False

# Cloudinary
CLOUDINARY_NAME="your name"
CLOUDINARY_API_KEY="your api key"
CLOUDINARY_API_SECRET="your api secret"
```

Для настройки и заполнения базы данных с помощью миграций выполняем команды:
```
python manage.py makemigrations
python manage.py migrate
```

Генерируем статичные файлы:
```
python manage.py collectstatic
```

Создаем пользователя для админ-панели с помощью команды:
```
python manage.py createsuperuser
```

### 4. Запуск.

Запускаем веб-сервер Django через команду:
```
python manage.py runserver 80
```
_____
:white_check_mark: <b>Готово!</b> :+1: :tada: 

Проект запущен и доступен по адресу: `http://localhost/` или `http://127.0.0.1/`


