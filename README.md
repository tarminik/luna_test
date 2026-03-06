# Luna — Справочник организаций

REST API справочник организаций, зданий и видов деятельности. Тестовое задание — [условия](TASK.md).

## Стек

- Python 3.13, FastAPI, SQLAlchemy (async), Alembic
- PostgreSQL 16
- Docker Compose

## Быстрый старт

Требуется: Docker и Docker Compose.

```bash
git clone https://github.com/tarminik/luna_test.git
cd luna_test
docker compose up
```

При первом запуске Docker автоматически скачает готовый образ приложения из GitHub Container Registry и поднимет PostgreSQL. Миграции и тестовые данные применяются автоматически.

Если хотите собрать образ из исходников (вместо скачивания готового):

```bash
docker compose up --build
```

После запуска:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API эндпоинты

Все эндпоинты требуют заголовок `X-API-Key`.

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/organizations/{id}` | Организация по ID |
| GET | `/organizations/search?name=...` | Поиск организации по имени |
| GET | `/organizations/search/in_radius?lat=...&lon=...&radius_m=...` | Организации в радиусе |
| GET | `/organizations/search/in_rect?lat_min=...&lon_min=...&lat_max=...&lon_max=...` | Организации в прямоугольнике |
| GET | `/buildings/search/in_radius?lat=...&lon=...&radius_m=...` | Здания в радиусе |
| GET | `/buildings/search/in_rect?lat_min=...&lon_min=...&lat_max=...&lon_max=...` | Здания в прямоугольнике |
| GET | `/buildings/{id}/organizations` | Организации в здании |
| GET | `/activities/{id}/organizations` | Организации по виду деятельности (рекурсивно) |

## Авторизация

Все запросы требуют заголовок:

```
X-API-Key: luna-dev-key-12345
```

Без заголовка или с неверным ключом — ответ `401 Unauthorized`.

## Примеры запросов

```bash
# Организация по ID
curl -H "X-API-Key: luna-dev-key-12345" http://localhost:8000/organizations/1

# Поиск по имени
curl -H "X-API-Key: luna-dev-key-12345" "http://localhost:8000/organizations/search?name=ООО"

# Здания в радиусе 500м от точки
curl -H "X-API-Key: luna-dev-key-12345" \
  "http://localhost:8000/buildings/search/in_radius?lat=55.7558&lon=37.6173&radius_m=500"

# Организации по виду деятельности (включая дочерние)
curl -H "X-API-Key: luna-dev-key-12345" http://localhost:8000/activities/1/organizations
```

## Локальная разработка

Требуется PostgreSQL и Python 3.13+.

```bash
# Установка зависимостей
pip install .

# Миграции и тестовые данные
alembic upgrade head
python -m app.seed

# Запуск
uvicorn app.main:app --reload
```

Настройки (через переменные окружения или файл `.env`):

| Переменная | По умолчанию | Описание |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/luna` | Строка подключения к PostgreSQL |
| `API_KEY` | `luna-dev-key-12345` | Статический API-ключ для авторизации |
