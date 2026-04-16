<div align="center">

# HireFlow

**HR-платформа полного цикла подбора персонала**

Единое окно для кандидатов, HR и руководителей: отклики, Kanban, видеоинтервью, AI-конструктор резюме и уведомления в Telegram — из одной коробки.

[Возможности](#возможности) · [Стек](#стек) · [Быстрый старт](#быстрый-старт) · [Архитектура](#архитектура) · [Безопасность](#безопасность) · [Лицензия](#лицензия)

</div>

---

## О проекте

HireFlow разработан в рамках хакатона как MVP платформы для автоматизации найма. Закрывает все функциональные и нефункциональные требования технического задания (см. [tz/ТЗ.md](tz/%D0%A2%D0%97.md)) и добавляет сверху несколько killer-фич:

- **AI-Конструктор резюме** — четырёхшаговый wizard с потоковой генерацией на Gemini и контекстом из профиля.
- **Импорт выписки СТД-Р** — загрузил PDF с Госуслуг, и опыт работы заполнен за 10 секунд.
- **Real-time Kanban** — drag-and-drop стадий найма с синхронизацией через WebSocket.
- **Встроенные видеозвонки** — LiveKit крутится в Docker-сети, токен выпускается бэкендом.
- **Telegram-бот** — единая шина уведомлений для HR, руководителей и кандидатов.
- **Multi-model AI fallback** — автоматическое переключение между Gemini 2.5 → 1.5 → Pro.

---

## Возможности

### Роли и доступ
| Роль | Что может |
|---|---|
| **Кандидат** | Регистрация, профиль с 20+ полями, загрузка документов, AI-генерация резюме, отклик на вакансии, отслеживание статусов, подтверждение интервью |
| **HR** | База кандидатов с фильтрацией по 8+ параметрам, Kanban-доска вакансии, назначение собеседований, внутренние заметки, календарь, обработка запросов от руководителей |
| **Руководитель** | Доступ только к своим кандидатам (IDOR-фильтр в БД), запрос интервью, форма отзыва с 4 критериями оценки |
| **Администратор** | Управление пользователями и ролями, блокировки, статистика, справочники, логи действий |

### Ключевые функции
- JWT-аутентификация с блокировкой аккаунтов
- 10 статусов кандидата с историей переходов
- Чат HR ↔ кандидат через WebSocket
- Notifications bus — один вызов рассылает в WS и Telegram
- Экспорт резюме в PDF со стабильной разбивкой на страницы
- Файлохранилище на MinIO (S3-совместимое)
- Security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Защита от XSS (DOMPurify), SQLi (SQLAlchemy ORM), IDOR (role-based фильтры)

---

## Стек

**Frontend:** Vue 3 · Pinia · Tailwind CSS · Vite · Lucide · vue-draggable-plus · DOMPurify

**Backend:** FastAPI · SQLAlchemy 2 async · Alembic · Pydantic v2 · asyncpg · httpx · pdfplumber

**Инфраструктура:** PostgreSQL 16 · MinIO · LiveKit · Docker Compose

**AI & интеграции:** Google Gemini (2.5-flash / 1.5-flash / 1.5-pro / pro) · Telegram Bot API

**Безопасность:** JWT · bcrypt · CSP/HSTS middleware · RBAC-guards на роутерах

---

## Быстрый старт

### Требования
- Docker 24+
- Docker Compose v2
- Ключ Google Gemini API ([aistudio.google.com](https://aistudio.google.com/))
- Telegram-бот через [@BotFather](https://t.me/BotFather) *(опционально, для уведомлений)*

### Установка

```bash
# 1. Клонируем
git clone https://github.com/<user>/hireflow.git
cd hireflow

# 2. Заполняем переменные окружения
cp .env.example .env
# → открываем .env и подставляем GEMINI_API_KEY, TELEGRAM_BOT_TOKEN

# 3. Поднимаем всё
docker compose up -d

# 4. Ждём healthcheck и запускаем seed
docker exec hakaton-ural-backend-1 python seed.py
```

После этого:
- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000 (Swagger: http://localhost:8000/docs)
- **MinIO Console:** http://localhost:9001 (minioadmin / minioadmin)
- **PostgreSQL:** localhost:5433 (hr / hr_pass / hrdb)

### Demo-аккаунты

| Роль | Email | Пароль |
|---|---|---|
| Админ | `admin@hireflow.ru` | `admin123` |
| HR | `hr_expert@hireflow.ru` | `hr_pass` |
| Руководитель | `tech_lead@hireflow.ru` | `mgr_pass` |
| Кандидат | `alex_dev@mail.ru` | `candidate` |

Полный набор сценариев — в [credentials.md](credentials.md).

---

## Архитектура

```
┌────────────────────────────────────────┐
│          Vue 3 SPA  (:5173)            │
│   Pinia · Tailwind · WebSocket client  │
└──────────────────┬─────────────────────┘
                   │ HTTPS + WebSocket
                   ▼
┌────────────────────────────────────────┐
│          FastAPI  (:8000)              │
│   JWT · Async · 15 роутеров · RBAC     │
│   Security-headers middleware          │
└──┬────────┬────────┬────────┬────────┬─┘
   │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌──────┐ ┌─────────┐ ┌──────┐ ┌────────┐
│ PG16 │ │MinIO │ │ LiveKit │ │Gemini│ │Telegram│
│      │ │ S3   │ │ (WebRTC)│ │ API  │ │  Bot   │
└──────┘ └──────┘ └─────────┘ └──────┘ └────────┘
```

- **Stateless backend** — горизонтально масштабируется, JWT без сессий.
- **Service layer** — `notifications.py`, `s3.py`, `telegram_bot.py`, AI-fallback логика отделены от роутеров.
- **Async-first** — asyncpg, httpx, async Gemini SDK; event loop не блокируется.
- **Миграции** — Alembic, `backend/alembic/versions/`.
- **Seed** — `backend/seed.py` создаёт 15 пользователей, 6 вакансий, 14 откликов, 7 интервью.

### Структура
```
.
├── backend/
│   ├── alembic/              # миграции
│   ├── app/
│   │   ├── models/           # SQLAlchemy модели (15+)
│   │   ├── routers/          # FastAPI endpoints (15 модулей)
│   │   ├── schemas/          # Pydantic-схемы
│   │   ├── services/         # AI, S3, Telegram, notifications
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── deps.py           # get_current_user, require_role
│   │   └── main.py           # app + CORS + security headers
│   ├── seed.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── views/            # candidate/ · hr/ · manager/ · admin/ · chat/
│   │   ├── components/       # AppLayout, AppSidebar
│   │   ├── stores/           # Pinia
│   │   ├── router/
│   │   └── api/
│   └── package.json
├── tz/                       # Техническое задание
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Безопасность

Реализованы все требования раздела 5.2 ТЗ:

| Угроза | Реализация |
|---|---|
| **SQL Injection** | SQLAlchemy ORM с параметризованными запросами, raw SQL отсутствует |
| **XSS** | DOMPurify.sanitize на AI-выводе и пользовательском контенте, Vue эскейпит по умолчанию |
| **CSRF** | JWT передаётся в `Authorization`-заголовке, не в cookie |
| **IDOR** | Менеджеры видят только назначенных им кандидатов через JOIN по интервью в БД-запросе |
| **RBAC** | `require_role(...)` на каждом чувствительном роуте |
| **Password** | bcrypt с per-user salt, блокировка через `is_active` |
| **Headers** | CSP · HSTS · X-Frame-Options · X-Content-Type-Options через middleware |
| **JWT** | TTL + ревокация через блокировку аккаунта |

---

## REST API

Swagger UI: `http://localhost:8000/docs`

Основные разделы:
- `/api/auth` — регистрация и логин
- `/api/candidates` — профили, поиск, AI-генерация, импорт СТД-Р
- `/api/vacancies` — вакансии
- `/api/applications` — отклики и Kanban-статусы
- `/api/interviews` — назначение и подтверждение
- `/api/interview-requests` — запросы от руководителей
- `/api/feedbacks` — отзывы и оценки
- `/api/documents` — загрузка в MinIO
- `/api/messages` — чат и WebSocket-уведомления
- `/api/livekit` — выпуск токенов для видеокомнат
- `/api/admin` — управление пользователями и статистика
- `/api/notes` — внутренние заметки HR

---

## Разработка

```bash
# Backend hot-reload (при изменениях в backend/app)
docker compose restart backend

# Миграция после изменения моделей
docker exec hakaton-ural-backend-1 alembic revision --autogenerate -m "описание"
docker exec hakaton-ural-backend-1 alembic upgrade head

# Frontend hot-reload работает автоматически через Vite (:5173)

# Пересборка seed-данных
docker exec hakaton-ural-backend-1 python seed.py

# Линтер backend
docker exec hakaton-ural-backend-1 ruff check app/
```

---

## Roadmap

- [ ] SSO через Госуслуги (ESIA)
- [ ] Redis pub/sub для WebSocket в horizontal scale
- [ ] Покрытие pytest 80%+
- [ ] Мобильный клиент (OpenAPI-контракт готов)
- [ ] Публикация OpenAPI в отдельный SDK-пакет
- [ ] Более гибкий конструктор scorecard (сейчас фиксированные 4 критерия)

---

## Лицензия

MIT — см. [LICENSE](LICENSE) *(или укажите вашу лицензию перед публикацией)*.

---

<div align="center">
<sub>Сделано на хакатоне · 2026</sub>
</div>
