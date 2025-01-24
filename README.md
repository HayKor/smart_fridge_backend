# SmartFridge

![mosh-image](https://predprof.olimpiada.ru/images/logo-predporf.svg)

Проект для Московской Предпрофессиональной Олимпиады, [Кейс №2](https://cloud.predprof.olimpiada.ru/index.php/s/Rgcom3K2BHRMqDJ)

## Описание

...

## Начало работы

### Зависимости

_См. [`pyproject.toml`](https://github.com/HayKor/smart_fridge_backend/blob/main/pyproject.toml)_

- **Lang**: Python 3.12+
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Pydantic](https://docs.pydantic.dev/latest/), [Aiogram](https://docs.aiogram.dev/en/v3.17.0/)
- **ASGI**: Uvicorn
- **Data management**: Redis, PostgreSQL
- **Dependency management**: [Poetry](https://python-poetry.org/docs/)

### Установка

**Предусловие**: python, poetry

##### 2. Установка зависимостей с `poetry`

```shell
poetry install
```

### Запуск

**Предусловие**: python, poetry, docker, alembic, _make_\*

_\*: необязательно_

#### Local development среда

##### 1. Настройка `.env`

Создайте файл `.env` (см. [`.env.example`](https://github.com/HayKor/smart_fridge_backend/blob/main/.env.example))

```
#.env
SECURITY__SECRET_KEY=f6f1d822c0e4bbcc08a4517ad598c2a3dce8e48d056d97d2521dc16f72440dc7
JWT__ALGORITHM=HS256
JWT__ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT__REFRESH_TOKEN_EXPIRE_DAYS=30
DATABASE__URL=postgresql+asyncpg://user:password@localhost/db
REDIS__URL=redis://localhost:6379?decode_responses=True
BOT__TOKEN=YOUR_TOKEN
```

##### 2. Запуск dev среды (database, redis) c помощью `make`

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

##### 3. API-сервис

```shell
poetry run uvicorn smart_fridge.app:app --host 0.0.0.0 --port 8000 --reload --factory
```

API-документация будет доступна по адресу

```shell
http://localhost:8080/docs
```

##### 4. Телеграм-бот (для уведомлений и `cron`-работ)

```shell
python3 smart_fridge/bot.py
```

#### Production среда

...coming soon

## Помощь

Будьте внимательны с портами и хостом в `docker-compose.local.yml` при локальной разработке.
Настоятельно рекомендуем использовать **Linux/WSL**.

## Авторы

- [Артур Багинян](https://github.com/HayKor/)
- [Гриценко Владислав](https://github.com/Gr1zee)
- [Гришин Илья](https://github.com/ilyaaadfb)
- [Кобцев Андрей](https://github.com/LoneGhostG)
- [Светлана Сердюк](https://github.com/vetkas2023) - фронт-енд

## Ссылки

- [awesome-readme](https://github.com/matiassingers/awesome-readme)
