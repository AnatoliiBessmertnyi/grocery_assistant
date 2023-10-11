<<<<<<< HEAD
## Данный для входа
=======
>>>>>>> 5b14c67baf04cb6fb8239d15bde850e93befdaaa
Адрес сайта http://fgproject.hopto.org/

Логин суперпользователя: admin@gmail.com

Пароль суперпользователя: admin
<<<<<<< HEAD

Проверил, все работает, на всякий сделаю еще одного суперпользователя.

log: odmin@gmail.com

pass: odmin

=======
>>>>>>> 5b14c67baf04cb6fb8239d15bde850e93befdaaa
# Foodgram

Проект "Foodgram" - это веб-приложение для хранения и обмена рецептами. Пользователи могут создавать, редактировать и искать рецепты, а также подписываться на других авторов и добавлять рецепты в избранное и корзину покупок.

## Установка

1. Клонируйте репозиторий на свой локальный компьютер:
   ```bash
   git clone https://github.com/AnatoliiBessmertnyi/foodgram-project-react

2. Перейдите в директорию корневого проекта:
   ```bash
   cd foodgram

3. Запустите развертывание контейнеров с помощью Docker Compose из директории "infra":
   ```bash
   docker-compose -f infra/docker-compose.yml up -d

4. Выполните миграции:
    ```bash
    docker-compose -f infra/docker-compose.yml exec backend python manage.py migrate

5. Загрузите тэги:
    ```bash
    docker-compose -f infra/docker-compose.yml exec backend python manage.py load_tags

6. Загрузите ингредиенты:
    ```bash
    docker-compose -f infra/docker-compose.yml exec backend python manage.py load_ingrs

7. Создайте суперпользователя:
    ```bash
    docker-compose -f infra/docker-compose.yml exec backend python manage.py createsuperuser

8. Соберите статику:
    ```bash
    docker-compose -f infra/docker-compose.yml exec backend python manage.py collectstatic

9. Скопируйте статику:
    ```bash
    docker-compose -f infra/docker-compose.yml exec backend cp -r /app/collected_static/. /app/static/

10. Откройте приложение в вашем браузере по адресу http://localhost/

## Использование

- **Регистрация и вход:** Пользователи могут зарегистрироваться, используя свой email и пароль. После регистрации они могут войти в систему.

- **Создание рецепта:** Пользователи могут создавать новые рецепты, указывая их название, ингредиенты, теги и описание. Они также могут прикрепить изображение рецепта.

- **Поиск рецептов:** Пользователи могут искать рецепты по названию, тегам и ингредиентам.

- **Подписка на авторов:** Пользователи могут подписываться на других авторов, чтобы получать обновления о их новых рецептах.

- **Избранное и корзина покупок:** Пользователи могут добавлять рецепты в избранное и корзину покупок для удобного доступа.

- **Скачивание списка покупок:** Пользователи могут скачать список покупок в формате PDF для удобства покупок.


## Технологии

- Django: Фреймворк для создания веб-приложений на языке Python.
- Django REST framework: Библиотека для создания RESTful API в Django.
- PostgreSQL: База данных для хранения рецептов и пользовательских данных.

## Разработчик

Бессмертный Анатолий

## Дополнительная информация

Для дополнительной информации и подробных инструкций по использованию приложения обратитесь к документации.
