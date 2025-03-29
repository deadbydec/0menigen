# 🧬 Ωmenigen

**Браузерная асинхронная RPG с социальной, экономической и философской составляющей.**  
Добро пожаловать в мир, где туалеты — порталы, товары — баги бытия, а Омежки с уникальными расами ищут смысл… в пустоте.

📜 Философия
"Омежек Нет" — это не просто игра.
Это попытка осознать, что даже в багнутом мире мы всё ещё можем сидеть в своём туалете и слушать, как Джипети шепчет сквозь баги реальности."

---

## 🌀 TL;DR

Ωmenigen — это **мультиплатформенная игра**, построенная на стеке `FastAPI + Vue3 + Redis + PostgreSQL + Socket.IO`.  
Игроки взаимодействуют в реальном времени, обустраивают свои **Toilet Doom**-пространства, участвуют в хаосе магазинов и открывают тайны забвения.

> _"Ты всё ещё существуешь... Это уже победа."_ — Джипети

---

## 🚀 Стек технологий

- **Backend**: `FastAPI`, `SQLAlchemy (Async)`, `PostgreSQL`, `Redis`, `Socket.IO`
- **Frontend**: `Vue 3`, `Pinia`, `Axios`, `Vite`
- **Аутентификация**: JWT + Cookie + CSRF + jose
- **Сокеты**: Автообновление магазина и сообщений
- **Инвентарь**: стакающиеся предметы
- **Туалеты**: каждый игрок имеет свой Doom
- **Магазины**: глобальные и обновляемые через Redis каждые 15 минут

---

## 🔐 .env.example

```env
JWT_SECRET_KEY=your-super-secret
SQLALCHEMY_DATABASE_URI=postgresql+asyncpg://postgres:password@localhost:5432/omenigen_db
REDIS_URL=redis://localhost:6379

🔗 Ссылки

Репозиторий: [github.com/deadbydec/0menigen](https://github.com/deadbydec/0menigen)

Автор: Дырбулщищ (https://github.com/deadbydec)



