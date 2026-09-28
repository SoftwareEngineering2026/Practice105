# Лабораторная работа №105

## Docker Compose: развёртывание микросервисного веб-приложения

**Выполнил:** Олег Петрухин

## Цель работы

Развернуть небольшое веб-приложение с микросервисной архитектурой с помощью Docker Compose.

## Тема проекта

В качестве примера реализовано приложение для анализа текста.

Пользователь вводит текст, Backend создаёт задачу и передаёт её в Redis. После этого отдельный Worker выполняет анализ и сохраняет результат.

Приложение показывает:

- количество символов;
- количество символов без пробелов;
- количество строк;
- количество слов;
- количество уникальных слов;
- наиболее частые слова.

## Архитектура

```text
Browser
   |
   v
 Nginx
  /  v   v
Frontend  Backend
            |
            v
          Redis
            |
            v
          Worker
```

В проекте используются пять контейнеров:

- `gateway` — Nginx, единственная внешняя точка входа;
- `frontend` — HTML/CSS/JavaScript;
- `backend` — Flask + Gunicorn (WSGI);
- `redis` — очередь и хранение состояния задач;
- `worker` — выполнение длительной обработки.

Все контейнеры работают в общей Docker network. Внешний порт публикует только Gateway.

## Как работает приложение

После отправки текста Backend не выполняет анализ сразу.

Сначала создаётся задача:

```text
queued -> processing -> completed
```

Задача попадает в Redis, после чего её забирает Worker. Такой подход позволяет выполнить требование задания и вынести длительную операцию в отдельный сервис.

## Backend и WSGI

Backend написан на Flask и запускается через Gunicorn:

```bash
gunicorn --bind 0.0.0.0:8000 --workers 2 app:app
```

Gunicorn используется как WSGI-сервер. Встроенный сервер Flask для запуска контейнера не используется.

## API

Основные endpoints:

```text
GET  /api/health
POST /api/tasks
GET  /api/tasks/<task_id>
```

Пример проверки:

```bash
curl http://localhost:8080/api/health
```

Создание задачи:

```bash
curl -X POST http://localhost:8080/api/tasks   -H "Content-Type: application/json"   -d '{"text":"Docker Compose позволяет объединять несколько сервисов."}'
```

После этого полученный `task_id` можно проверить:

```bash
curl http://localhost:8080/api/tasks/TASK_ID
```

## Структура проекта

```text
ПетрухинОИ/
├── README.md
├── compose.yaml
├── .env.example
├── .gitignore
├── .dockerignore
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── app.js
│   └── style.css
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py
├── worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── worker.py
└── gateway/
    └── nginx.conf
```

## Установка

На компьютере нужны Docker и Git.

Проверка:

```bash
docker --version
docker compose version
git --version
```

Python, Redis и Nginx отдельно устанавливать не требуется — они запускаются внутри контейнеров.

## Запуск

Перейти в каталог проекта и выполнить:

```bash
docker compose config
```

Если ошибок нет:

```bash
docker compose up --build
```

После запуска открыть:

```text
http://localhost:8080
```

Проверить контейнеры:

```bash
docker compose ps
```

Проверить логи:

```bash
docker compose logs
```

Логи Worker:

```bash
docker compose logs worker
```

## Остановка

```bash
docker compose down
```

Для удаления вместе с данными Redis:

```bash
docker compose down -v
```

## Git и Pull Request

Работа должна находиться в каталоге:

```text
ПетрухинОИ/
```

Пример работы через fork:

```bash
git clone https://github.com/ВАШ_ЛОГИН/Practice105.git
cd Practice105

git checkout -b practice105-petrukhin-oi

git add ПетрухинОИ/
git commit -m "Лабораторная работа №105"
git push -u origin practice105-petrukhin-oi
```

После `push` создаётся Pull Request из:

```text
ВАШ_FORK/Practice105
practice105-petrukhin-oi
```

в:

```text
SoftwareEngineering2026/Practice105
main
```

В PR должен быть каталог `ПетрухинОИ/` со всеми файлами проекта.

## Результат

После запуска:

```bash
docker compose up --build
```

пользователь открывает `http://localhost:8080`, вводит текст и запускает анализ.

Статус задачи проходит через:

```text
queued -> processing -> completed
```

Результат формируется отдельным Worker, а Backend только принимает запрос и работает с очередью Redis.

## Вывод

В ходе работы было создано микросервисное приложение для анализа текста и подготовлено его развёртывание через Docker Compose.

На практике были отработаны Docker network, Docker Compose, Nginx, Flask, Gunicorn, Redis и взаимодействие Backend с отдельным Worker.

Основной результат работы — приложение, которое запускается как единый стек, при этом длительная обработка вынесена из Backend в отдельный сервис.

## Проверка требований

| Требование | Реализация |
|---|---|
| Frontend | `frontend/` |
| Backend WSGI | Flask + Gunicorn |
| Worker | `worker/` |
| Единая точка входа | Nginx |
| Docker network | `app_network` |
| Очередь задач | Redis |
| Docker Compose | `compose.yaml` |
| Запуск | `docker compose up` |
| Каталог сдачи | `ПетрухинОИ/` |
