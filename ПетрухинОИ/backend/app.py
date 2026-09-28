import json
import os
import uuid

from flask import Flask, jsonify, request
import redis

app = Flask(__name__)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
TASK_QUEUE = os.getenv("TASK_QUEUE", "task_queue")
TASK_TTL_SECONDS = int(os.getenv("TASK_TTL_SECONDS", "3600"))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def task_key(task_id: str) -> str:
    return f"task:{task_id}"

@app.get("/api/health")
def health():
    try:
        redis_client.ping()
        return jsonify({"status": "ok", "service": "backend"})
    except redis.RedisError as exc:
        return jsonify({"status": "error", "service": "backend", "error": str(exc)}), 503

@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "Ожидается JSON-объект."}), 400
    text = data.get("text")
    if not isinstance(text, str):
        return jsonify({"error": "Поле 'text' должно быть строкой."}), 400
    text = text.strip()
    if not text:
        return jsonify({"error": "Текст не должен быть пустым."}), 400
    if len(text) > 50000:
        return jsonify({"error": "Максимальная длина текста — 50000 символов."}), 400

    task_id = str(uuid.uuid4())
    payload = {"task_id": task_id, "text": text}
    try:
        key = task_key(task_id)
        redis_client.hset(key, mapping={"status": "queued", "result": "", "error": ""})
        redis_client.expire(key, TASK_TTL_SECONDS)
        redis_client.rpush(TASK_QUEUE, json.dumps(payload, ensure_ascii=False))
    except redis.RedisError as exc:
        return jsonify({"error": f"Не удалось поставить задачу в очередь: {exc}"}), 503

    app.logger.info("Task %s queued", task_id)
    return jsonify({"task_id": task_id, "status": "queued"}), 202

@app.get("/api/tasks/<task_id>")
def get_task(task_id: str):
    try:
        task = redis_client.hgetall(task_key(task_id))
    except redis.RedisError as exc:
        return jsonify({"error": f"Redis недоступен: {exc}"}), 503
    if not task:
        return jsonify({"error": "Задача не найдена или срок её хранения истёк."}), 404

    response = {"task_id": task_id, "status": task.get("status", "unknown")}
    if task.get("result"):
        response["result"] = json.loads(task["result"])
    if task.get("error"):
        response["error"] = task["error"]
    return jsonify(response)
