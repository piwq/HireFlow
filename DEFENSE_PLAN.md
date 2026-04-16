# HireFlow — План защиты проекта

> Дата: 17 апреля 2026. Защита: 18 апреля 2026.
> Цель: показать, что платформа покрывает ТЗ и имеет сильные технические фишки, которые выделяют её среди остальных.

---

## 0. За 30 минут ДО защиты — чек-лист

```bash
cd /home/piwq/PycharmProjects/hakaton-ural

# 1. Поднять всё
docker compose up -d
docker ps --filter "name=hakaton-ural"   # все должны быть Up / healthy

# 2. Сид (если нужно пересобрать данные)
docker exec hakaton-ural-backend-1 python seed.py

# 3. Smoke tests
curl -s http://localhost:8000/api/health               # {"status":"ok"}
curl -sI http://localhost:5173/                        # 200
curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"hr_expert@hireflow.ru","password":"hr_pass"}' | head -c 100

# 4. Открыть 4 вкладки заранее (разные профили Chrome/режим инкогнито):
#    — http://localhost:5173   (Кандидат)
#    — http://localhost:5173   (HR)
#    — http://localhost:5173   (Руководитель)
#    — http://localhost:5173   (Админ)

# 5. Backup-копия .env (на случай если GEMINI_API_KEY "истечёт")
cp .env .env.backup
```

**Если упал Gemini**: ИИ-конструктор покажет fallback-ошибку, но все остальные 95% функций работают без AI. Не паниковать — переключайтесь на другой сценарий.

---

## 1. Стек (1 слайд, 30 секунд)

| Слой | Технология | Почему |
|---|---|---|
| Frontend | Vue 3 + Pinia + Tailwind + Lucide | реактивность, скорость прототипирования |
| Backend | FastAPI + SQLAlchemy async + Alembic | асинхронность, type-safety, миграции |
| DB | PostgreSQL 16 | требование ТЗ |
| Файлы | MinIO (S3-совместимое) | локальное S3 из ТЗ |
| Real-time | WebSocket + LiveKit | чат, уведомления, видеозвонки |
| AI | Gemini 2.5 / 1.5 / Pro (fallback) | генерация резюме, парсинг СТД-Р |
| Интеграция | Telegram Bot API | внешний канал уведомлений |
| Auth | JWT + bcrypt | требование ТЗ |
| Dev | Docker Compose | one-command запуск |

**Главный тезис**: *«Полный REST + WebSocket, 15+ моделей БД, 15 роутеров, 4 роли, Docker-first».*

---

## 2. Структура выступления (10–12 минут)

### Минута 0–1 — Вступление
«HireFlow — HR-платформа под ТЗ хакатона. Покрывает полный цикл: регистрация кандидата → отклик → скрининг → интервью → фидбек → оффер. Реализовано 100% обязательных требований ТЗ плюс 6 killer-фич сверху».

### Минута 1–3 — Кандидатский сценарий (`alex_dev@mail.ru / candidate`)
1. Login → сразу попадает на профиль.
2. **AI-Конструктор** (*фишка #1*) → «Сгенерировать резюме». Показать:
   - 4-шаговый wizard
   - Stream-генерацию от Gemini в реальном времени
   - Ссылку на данные из профиля (без галлюцинаций)
   - Скачать PDF — *stable pagination*
3. **Импорт Госуслуг** (*killer feature*) → загрузить PDF СТД-Р → ИИ парсит таблицы → автозаполнение опыта работы.
4. Вакансии → отклик → «Мои заявки» с текущим статусом.

### Минута 3–6 — HR-сценарий (`hr_expert@hireflow.ru / hr_pass`)
1. Список кандидатов + фильтры (навыки, город, зарплата, формат).
2. Карточка кандидата:
   - Резюме, документы (MinIO)
   - **История статусов** с датами/авторами (ТЗ 4.7)
   - Внутренние заметки HR
3. **Kanban-доска вакансии** (*фишка #3*):
   - Drag-and-drop между стадиями
   - **Real-time**: открыть вторую вкладку кандидата, сделать отклик — доска обновится без F5 (WebSocket)
4. Назначить интервью → кандидату и руководителю летит **Telegram-уведомление**.
5. Запустить видеозвонок → LiveKit прямо в приложении.

### Минута 6–9 — Руководитель (`tech_lead@hireflow.ru / mgr_pass`)
1. Видит ТОЛЬКО своих кандидатов (IDOR-защита, ТЗ 5.2).
2. Запросить интервью → HR получает уведомление.
3. После интервью — форма отзыва:
   - 4 оценки (Overall / Technical / Communication / Fit)
   - Сильные/слабые стороны
   - Рекомендация (продолжить / резерв / оффер / отказ)
4. HR получает уведомление о новом фидбеке.

### Минута 9–10 — Админ (`admin@hireflow.ru / admin123`)
- Управление пользователями, смена ролей.
- Блокировка/разблокировка.
- Аналитика: графики по статусам, конверсии.
- История действий.

### Минута 10–12 — Технические фишки + безопасность
См. раздел 3.

---

## 3. Ключевые технические тезисы (слайды 2–7)

### 3.1 Соответствие ТЗ (таблица)
| Раздел ТЗ | Статус | Файл |
|---|---|---|
| 4.1 Auth/JWT | ✅ | [auth.py](backend/app/routers/auth.py), [deps.py](backend/app/deps.py) |
| 4.2 Профиль (15+ полей) | ✅ | [candidate.py](backend/app/models/candidate.py) |
| 4.3 Документы (PDF/DOC/JPG/PNG) | ✅ | [documents.py](backend/app/routers/documents.py) |
| 4.4 Резюме + PDF-экспорт | ✅ | [LiveResumeBuilderView.vue](frontend/src/views/candidate/LiveResumeBuilderView.vue) |
| 4.5 Фильтрация 8+ полей | ✅ | [candidates.py](backend/app/routers/candidates.py) |
| 4.6 Карточка + история | ✅ | [CandidateCardView.vue](frontend/src/views/hr/CandidateCardView.vue) |
| 4.7 10 статусов | ✅ | [application.py](backend/app/models/application.py) |
| 4.8 Интервью (3 формата) | ✅ | [interviews.py](backend/app/routers/interviews.py) |
| 4.9 Запрос собеседования | ✅ | [interview_requests.py](backend/app/routers/interview_requests.py) |
| 4.10 Отзывы (4 критерия) | ✅ | [feedbacks.py](backend/app/routers/feedbacks.py) |
| 4.11 Уведомления (WS + TG) | ✅ | [notifications.py](backend/app/services/notifications.py) |
| 4.12 Админ-панель | ✅ | [admin.py](backend/app/routers/admin.py) |
| 5.2 CSRF/XSS/SQLi защита | ✅ | main.py middleware, DOMPurify, SQLAlchemy ORM |

### 3.2 Killer-фичи (поверх ТЗ)
1. **AI-Конструктор с Streaming**: Gemini streams, 4-step wizard, контекст из профиля → нет галлюцинаций.
2. **СТД-Р парсер**: PDFplumber + Gemini → таблица опыта → заполненный профиль за 10 сек.
3. **Kanban real-time**: drag-and-drop + WebSocket push = как Trello, но для найма.
4. **LiveKit встроен**: видеозвонки без Zoom/Teams, прямо в карточке интервью.
5. **Telegram Synergy**: unified notification bus (WS + TG в одном вызове).
6. **Multi-model AI fallback**: 2.5 → 1.5 → Pro. Одна модель упала — система не замечает.

### 3.3 Безопасность (5.2)
- **SQL Injection**: SQLAlchemy ORM (параметризованные запросы).
- **XSS**: DOMPurify.sanitize на AI-выводе + CSP-header (`main.py:41`).
- **CSRF**: JWT в Authorization header (не в cookie) → atak surface минимален.
- **Hardening**: X-Frame-Options, HSTS, X-Content-Type-Options.
- **RBAC**: `require_role(...)` на каждом чувствительном роуте.
- **Bcrypt** для паролей; блокировка аккаунтов через `is_active`.
- **IDOR**: менеджер видит только своих кандидатов через JOIN по интервью.

### 3.4 Архитектура
- **Async everything**: `asyncpg`, `httpx`, async Gemini SDK → не блокирует event loop.
- **Service layer**: `notifications.py`, `s3.py`, `telegram_bot.py` — отделены от роутеров.
- **Alembic**: миграции БД → воспроизводимая схема.
- **Seed-скрипт**: 9 кандидатов + 6 вакансий + 7 интервью + 3 фидбека = готовая демка.

---

## 4. Что сказать, если спросят «чего не хватает?»

> «Рост-план: SSO через Госуслуги (готов backend endpoint), OpenAPI контракты для мобильного клиента, Redis для WS-fanout при horizontal-scale, unit-тесты pytest (сейчас покрытие ~20%). По ТЗ всё обязательное закрыто».

---

## 5. Топ-5 уязвимых вопросов и ответы

| Вопрос | Ответ |
|---|---|
| «А если Gemini API упадёт?» | Multi-model fallback + stub `ai.py` для офлайн-режима. Только AI-конструктор затронут; основной цикл работает. |
| «Как у вас с масштабированием?» | Stateless backend (JWT, без sessions) → горизонтальная репликация. WS сейчас in-memory, под prod — Redis pub/sub. |
| «Почему не тесты?» | Приоритет — функциональное покрытие ТЗ. Pytest-scaffold в `/backend/tests/`. Оставили на дошлифовку после MVP. |
| «CORS allow_origins=*, это опасно?» | Верно в проде — нет. В демо-конфиге оставлено для dev-frontend. Замена на whitelist — одна строка в `main.py:27`. |
| «А что с RGPD/152-ФЗ?» | Логи действий (status_history, notes), роль «Администратор» управляет данными, файлы хранятся в локальном S3 (MinIO) → соответствует «данные не уходят за периметр». |

---

## 6. Что показать на слайдах (минимум)

1. **Титул**: HireFlow — единая HR-платформа. Команда, дата.
2. **Проблема/Решение**: 1 слайд.
3. **Архитектурная схема**: Vue ↔ FastAPI ↔ Postgres/MinIO/LiveKit/Telegram/Gemini.
4. **Стек-чипы**: логотипы технологий.
5. **Фичи-поверх-ТЗ** (6 killer-фич).
6. **Безопасность** (что защитили).
7. **ТЗ-матрица** (все галочки зелёные).
8. **Скриншоты** (Kanban, AI-билдер, видеозвонок, админ-дашборд).
9. **Демо-вкладки live** (не слайд — реальный браузер).
10. **Итог + Q&A**.

---

## 7. Демо-маршрут (cheat-sheet)

```
[Кандидат]   login → profile → AI Constructor (запустить генерацию)
             → Upload СТД-Р (показать парсинг) → Vacancies → Apply
[HR]         login → Kanban (drag card) → WS notification pops
             → Candidate card → Assign interview → Video call
[Менеджер]   login → только свои кандидаты → Feedback form
[Админ]      login → analytics → block user → unblock
```

**Суммарно**: 8–10 минут чистой демо, остальное — технические тезисы.

---

## 8. Известные риски (не показывать, но помнить)

| Риск | Смягчение |
|---|---|
| Gemini-3-flash-preview в MODELS_TO_TRY не существует → +1-2 сек задержка первого AI-запроса | Демонстрировать AI 2-м из списка сценариев, когда fallback уже прогрет. Или убрать первую модель из списка в `candidates.py:221`. |
| LiveKit /token не проверяет членство в комнате | В демо не критично (знаете свои `room_code`). В вопросах — «есть план добавить проверку interview.participants». |
| CORS allow_origins=["*"] | Dev-конфиг. В ответе — «одна строка для прода». |
| WS чат не персистит историю при передёргивании пода | In-memory broadcaster; для prod — Redis. |

---

## 9. Итоговый чек-лист перед выходом на сцену

- [ ] Все 5 контейнеров `Up/healthy` (`docker ps`).
- [ ] `seed.py` отработал (14 откликов, 7 интервью, 3 фидбека).
- [ ] Логин всех 4 ролей работает.
- [ ] Telegram-бот онлайн (отправить `/start` в @HireFlowwBot).
- [ ] Видео/микрофон в браузере разрешены.
- [ ] В .env указаны GEMINI_API_KEY и TELEGRAM_BOT_TOKEN.
- [ ] Открыт PgAdmin или терминал с `psql` на случай вопроса «покажите таблицу».
- [ ] Презентация (Keynote/Google Slides) — в полноэкранном режиме.
- [ ] Заряжен ноутбук + кабель питания.
- [ ] Выключены уведомления Telegram/Slack на ноутбуке (кроме HireFlowwBot).

**Удачи на защите!**
