# SimpleBank API

REST API для банковских операций с Django REST Framework.

## 📋 Оглавление

- [Технологии](#технологии)
- [Структура проекта](#структура-проекта)
- [API Endpoints](#api-endpoints)
- [Запуск проекта](#запуск-проекта)
- [Тестирование](#тестирование)

---

## 🛠 Технологии

- **Python 3.13**
- **Django 5.2.8** - web framework
- **Django REST Framework 3.16.1** - REST API
- **PostgreSQL 16** - database
- **JWT (Simple JWT)** - authentication
- **Docker & Docker Compose** - containerization
- **Poetry** - dependency management
- **Pytest** - testing
- **Ruff** - linting & formatting
- **Mypy** - type checking

---

## 📁 Структура проекта
```
SimpleBank/
├── apps/
│   ├── account/
│   │   ├── migrations/
│   │   ├── views/
│   │   ├── serializers/
│   │   ├── tests/
│   │   └── models.py
│   └── transaction/
├── simplebank/
│   └── settings/
├── docker-compose.yml
├── Dockerfile
├── Makefile
└── pyproject.toml
```

---

## 🚀 API Endpoints

### Auth
- **POST** `/api/auth/sign_up/` — Регистрация нового пользователя
- **POST** `/api/auth/login/` — Авторизация пользователя
- **GET** `/api/auth/health/` — Health check
- **POST** `/api/auth/refresh/` — Перевыпуск access token

### Account
- **GET** `/api/auth/balance/` — Получение баланса (требует JWT)

### Transactions
- **POST** `/api/transactions/transfer` — Перевод денег между счетами (требует JWT)
- **GET** `/api/transactions/` — История транзакций с фильтрацией (требует JWT)

---

## 🏃 Запуск проекта

### 1. Клонируйте репозиторий
```bash
git clone git@github.com:CostGamer/SimpleBank.git
cd SimpleBank
```

### 2. Создайте `.env` файл
```bash
cp .env.example .env
```

### 3. Запустите проект через Docker
```bash
make up
```

API будет доступно на: **http://localhost:8000**

Swagger документация: **http://localhost:8000/api/docs/**

---

## 📝 Makefile команды
```bash
make help         # Показать все команды
make up           # Запустить Docker контейнеры
make down         # Остановить контейнеры
make down-clean   # Остановить и удалить volumes
make test         # Запустить тесты
make logs         # Показать логи
```

---

## 🧪 Тестирование
```bash
# Запуск всех тестов
make test
```

---

## 👤 Автор

[CostGamer](https://github.com/CostGamer)
