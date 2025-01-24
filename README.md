# SmartFridge

![mosh-image](https://predprof.olimpiada.ru/images/logo-predporf.svg)

Проект для Московской Предпрофессиональной Олимпиады, [Кейс №2](https://cloud.predprof.olimpiada.ru/index.php/s/Rgcom3K2BHRMqDJ)

## Описание

...

## Начало работы

### Зависимости

_См. `pyproject.toml`_

- **Lang**: Python 3.12+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Pydantic](https://docs.pydantic.dev/latest/), [Aiogram](https://docs.aiogram.dev/en/v3.17.0/)
- **ASGI**: Uvicorn
- **Data management**: Redis, PostgreSQL
- **Dependency management**: [Poetry](https://python-poetry.org/docs/)

### Установка

**Предусловие**: python, poetry

**Настройка `.env`**: Создайте файл `.env` (см. `.env.example`)

1. Установка зависимостей с `poetry`

```shell
poetry install
```

### Запуск

**Предусловие**: python, poetry, docker, alembic, _make_\*

_\*: необязательно_

#### Local development среда

##### 1. Запуск dev среды (database, redis) c помощью `make`

```shell
make dev-compose
```

Или напрямую `docker`'ом

```shell
docker compose -p smart_fridge -f deployment/docker-compose.local.yml up -d --build --remove-orphans
```

Применение миграций к базе данных

```shell
alembic upgrade head
```

##### 2. API-сервис

```shell
poetry run uvicorn smart_fridge.app:app --host 0.0.0.0 --port 8000 --reload --factory
```

API-документация будет доступна по адресу

```shell
http://localhost:8080/docs
```

##### 3. Телеграм-бот (для уведомлений и `cron`-работ)

```shell
python3 smart_fridge/bot.py
```

#### Production среда

...coming soon

## Помощь

Будьте внимательны с портами и хостом в `docker-compose.local.yml` при локальной разработке.
Настоятельно рекомендуем использовать Linux.

## Авторы

...

## Ссылки

Inspiration, code snippets, etc.

- [awesome-readme](https://github.com/matiassingers/awesome-readme)
