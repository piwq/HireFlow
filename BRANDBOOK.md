# HireFlow — Brand Book

## Концепция
Современная HR-платформа. Тёмная тема — основная (premium, tech-friendly).
Светлая — вторичная (для офисного использования).

---

## Цвета

### Тёмная тема (dark)
| Токен | Hex | Применение |
|---|---|---|
| `bg-base` | `#0D0F1A` | Основной фон страниц |
| `bg-surface` | `#151827` | Карточки, панели |
| `bg-elevated` | `#1E2235` | Модалки, дропдауны |
| `border` | `#2A2F4A` | Границы элементов |
| `text-primary` | `#E2E8F0` | Основной текст |
| `text-secondary` | `#94A3B8` | Подписи, метки |
| `text-muted` | `#4B5563` | Плейсхолдеры |

### Светлая тема (light)
| Токен | Hex | Применение |
|---|---|---|
| `bg-base` | `#F8FAFC` | Основной фон |
| `bg-surface` | `#FFFFFF` | Карточки |
| `bg-elevated` | `#F1F5F9` | Панели |
| `border` | `#E2E8F0` | Границы |
| `text-primary` | `#0F172A` | Основной текст |
| `text-secondary` | `#475569` | Подписи |
| `text-muted` | `#94A3B8` | Плейсхолдеры |

### Акцентные цвета (одинаковы для обеих тем)
| Токен | Hex | Применение |
|---|---|---|
| `accent` | `#6366F1` | Индиго — основной акцент, кнопки |
| `accent-hover` | `#4F46E5` | Hover-состояние |
| `accent-glow` | `rgba(99,102,241,0.3)` | Focus ring, glow эффект |

### Статусы (Kanban)
| Статус | Цвет | Hex |
|---|---|---|
| Новый | Синий | `#3B82F6` |
| Скрининг | Янтарный | `#F59E0B` |
| Интервью | Фиолетовый | `#8B5CF6` |
| Нанят | Изумрудный | `#10B981` |
| Отказ | Красный | `#EF4444` |

---

## Типографика

**Шрифт:** `Inter` (Google Fonts)
```html
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
```

| Роль | Size | Weight | Применение |
|---|---|---|---|
| Display | 24px | 700 | Заголовки страниц |
| Heading | 18px | 600 | Заголовки секций |
| Body | 14px | 400 | Основной текст |
| Label | 13px | 500 | Метки форм |
| Caption | 12px | 400 | Вспомогательный текст |
| Micro | 11px | 500 | Бейджи, теги |

---

## Компоненты

### Input
```
dark: bg-[#1E2235] border-[#2A2F4A] text-slate-100
      focus: border-indigo-500 ring-2 ring-indigo-500/30
light: bg-white border-slate-200 text-slate-900
       focus: border-indigo-500 ring-2 ring-indigo-500/20
```

### Button (Primary)
```
bg-indigo-600 hover:bg-indigo-500 text-white font-medium
px-4 py-2 rounded-lg transition-all
hover: shadow-lg shadow-indigo-500/25
```

### Button (Ghost)
```
dark: text-slate-400 hover:text-slate-200 hover:bg-white/5
light: text-slate-600 hover:text-slate-900 hover:bg-slate-100
```

### Card
```
dark: bg-[#151827] border border-[#2A2F4A] rounded-xl
light: bg-white border border-slate-200 rounded-xl shadow-sm
```

### Badge (статус)
```
Новый:     bg-blue-500/15    text-blue-400
Скрининг:  bg-amber-500/15   text-amber-400
Интервью:  bg-violet-500/15  text-violet-400
Нанят:     bg-emerald-500/15 text-emerald-400
Отказ:     bg-red-500/15     text-red-400
```

---

## Layout — App Shell

```
+--sidebar (240px)--+--------main content---------+
| Logo              |  Header (breadcrumb + user)  |
| Navigation items  |                              |
|  - Dashboard      |  Page content                |
|  - Candidates     |                              |
|  - Interviews     |                              |
|                   |                              |
| [theme toggle]    |                              |
| [logout]          |                              |
+-------------------+------------------------------+
```

Sidebar только для HR и Manager. Кандидат — простой layout без sidebar.

---

## Иконки
Библиотека: `lucide-vue-next` (легковесная, SVG, отлично выглядит)
```
npm install lucide-vue-next
```

---

## Эффекты
- **Hover на карточках:** subtle translate-y + shadow
- **Focus inputs:** indigo glow (box-shadow)  
- **Sidebar active item:** левая полоска accent + bg highlight
- **Transition:** `transition-all duration-200` везде
- **Kanban cards:** drop shadow при перетаскивании (встроено в vue-draggable)
