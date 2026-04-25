Проект доступен по ссылке https://github.com/Maksik1935/practice105

# UUID Spring Microservices Demo

1. **Frontend** — HTML-страница с одной кнопкой.
2. **Backend** — генератор UUID
3. **Long Task Processor** — Шедулер, который периодически проверяет доступность интернета. Как же генератор UUID может без интернета то жить))

## Запуск

```bash
docker compose up --build
```

После запуска открыть:

```text
http://localhost:8081
```

## Что делает приложение

На странице есть кнопка **"Сгенерировать UUID"**.  
Frontend вызывает backend:

```http
GET http://localhost:8080/api/uuid
```

Backend возвращает JSON:

```json
{
  "uuid": "8e8f0ad1-4ac9-42d5-9017-29d42ebf2e20"
}
```

Long Task Processor каждые 30 секунд вызывает:

```text
https://clients3.google.com/generate_204
```

И пишет в лог, доступен ли интернет.

## Проверка API вручную

```bash
curl http://localhost:8080/api/uuid
```

```bash
curl http://localhost:8080/actuator/health
```

## Структура проекта

```text
uuid-spring-microservices-demo/
├── docker-compose.yml
├── README.md
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   └── nginx.conf
├── backend-wsgi/
│   ├── Dockerfile
│   ├── pom.xml
│   └── src/main/java/com/example/backend/
│       ├── BackendApplication.java
│       └── UuidController.java
└── long-task-processor/
    ├── Dockerfile
    ├── pom.xml
    └── src/main/java/com/example/longtask/
        ├── LongTaskProcessorApplication.java
        └── InternetCheckScheduler.java
```

