![Github actions](https://github.com/ErmolovIvan/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Приложение «Продуктовый помощник»: сайт, на котором пользователи будут публиковать рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Сервис «Список покупок» позволит пользователям создавать список продуктов, которые нужно купить для приготовления выбранных блюд. 

## Авторы
Проект создан: 

- [Ермолов Иван](https://https://github.com/ErmolovIvan/)

## Список технологий

- Django
- Django Rest Framework
- Djoser
- Postgres
- Docker
- Nginx
- docker-compose


## Как запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/ErmolovIvan/foodgram-project-react.git
```

Перейти в папку infra и запустить docker-compose.yaml
(при установленном и запущенном Docker)
```
cd foodgram-project-react/infra
docker-compose up
```

Для пересборки контейнеров выполнять команду:
(находясь в папке infra, при запущенном Docker)
```
docker-compose up -d --build
```

В контейнере web выполнить миграции:

```
docker-compose exec web python manage.py migrate
```

Создать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec web python manage.py collectstatic --no-input
```

Заполнить базу данных ингредиентами:

```
docker-compose exec web python manage.py load_data
```

Создать через админку несколько тегов:

```
http://51.250.24.199/admin/
```
