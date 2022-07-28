# Yatube
Учебный проект в рамках курса Яндекс.Практикум

## Описание
Yatube - это социальная сеть для блогеров.
Благодаря этому проекту можно будет вести личный блог и взаимодействовать
с другими участниками Yatube - подписываться на любимых авторов,
комментировать записи, а также создавать сообщества с публикациями на
схожие темы.

## Технологии
- Python 3.7
- Django 2.2.19
- Фронтенд реализован с использованием HTML, CSS и фреймворка Bootstrap 5.0

## Установка и запуск проекта в dev-режиме
- Клонируйте репозиторий проекта:
    ```bash
    git clone https://github.com/photometer/yatube-project-bootstrap
    ```
- Не забудьте создать файл ```.env``` и добавить в него ваш ```SECRET_KEY```:
    ```
    SECRET_KEY=Ваш_секретный_ключ
    ```
- В папке проекта установите и активируйте виртуальное окружение 
(рекомендации для Windows):
    ```bash
    python -m venv venv
    . venv/scripts/activate
    ```
- Установите зависимости из файла ```requirements.txt```:
    ```bash
    pip install -r requirements.txt
    ```
- Выполните миграции:
    ```bash
    python yatube/manage.py migrate
    ```
- Создайте суперпользователя:
    ```bash
    python yatube/manage.py createsuperuser
    ```
- *При желании можно собрать статику в указанную в ```settings.py``` папку 
(частично статика уже загружена в репозиторий в виде исключения - часть, 
относящаяся к странице автора)*:
    ```bash
    python yatube/manage.py collectstatic
    ```
- Можно выполнить Unittest-тестирование:
    ```bash
    python yatube/manage.py test
    ```
    или же тестирование с помощью ```pytest```:
    ```bash
    pytest
    ```
- Запустите проект на ПК:
    ```bash
    python manage.py runserver
    ```
- Наполните базу данных в админке (https://localhost/admin) и готово!

## Лицензия
BSD 3

## Автор
Андросова Елизавета
