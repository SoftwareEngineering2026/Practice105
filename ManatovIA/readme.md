# Генератор паролей

Веб-приложение с микросервисной архитектурой для генерации паролей.

## Архитектура

```
Браузер
   ↓
gateway (Nginx, порт 8080)
   ├── /       → frontend (статический HTML/JS)
   └── /api/*  → backend (Flask WSGI)
                    ↓ HTTP
                 worker (Flask, длинная задача)
```

Сервисы взаимодействуют через внутреннюю сеть Docker. Единственная внешняя точка входа — `gateway`.

## Запуск

```bash
docker compose up --build
```

Приложение доступно по адресу: http://localhost:8080

## Использование

1. Откройте браузер на http://localhost:8080
2. Укажите длину пароля, количество и набор символов
3. Нажмите **Сгенерировать**
4. Дождитесь выполнения фоновой задачи (~4 сек)
5. Скопируйте нужный пароль кнопкой **copy**

## Стек

- Frontend: HTML + CSS + JavaScript (статика, Nginx)
- Backend: Python + Flask + Gunicorn
- Worker: Python + Flask + Gunicorn + ThreadPoolExecutor
- Gateway: Nginx
- Оркестрация: Docker Compose
