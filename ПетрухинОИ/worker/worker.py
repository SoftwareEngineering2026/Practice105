import json
import logging
import os
import re
import time
from collections import Counter

import redis

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
TASK_QUEUE = os.getenv("TASK_QUEUE", "task_queue")
RESULT_TTL_SECONDS = int(os.getenv("RESULT_TTL_SECONDS", "3600"))
HEARTBEAT_KEY = os.getenv("HEARTBEAT_KEY", "worker:heartbeat")
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

def task_key(task_id: str) -> str:
    return f"task:{task_id}"

def analyze_text(text: str) -> dict:
    # Искусственная задержка нужна для наглядной демонстрации long task.
    for _ in range(5):
        time.sleep(1)
    words = re.findall(r"[A-Za-zА-Яа-яЁё0-9]+", text.lower())
    counter = Counter(words)
    return {
        "characters": len(text),
        "characters_without_spaces": sum(not char.isspace() for char in text),
        "lines": len(text.splitlines()) or 1,
        "words": len(words),
        "unique_words": len(counter),
        "top_words": [{"word": word, "count": count} for word, count in counter.most_common(10)],
    }

def set_heartbeat() -> None:
    redis_client.set(HEARTBEAT_KEY, str(time.time()), ex=30)

def process_task(payload: dict) -> None:
    task_id = payload["task_id"]
    key = task_key(task_id)
    redis_client.hset(key, mapping={"status": "processing", "error": ""})
    logging.info("Started task %s", task_id)
    try:
        result = analyze_text(payload["text"])
        redis_client.hset(key, mapping={"status": "completed", "result": json.dumps(result, ensure_ascii=False), "error": ""})
        redis_client.expire(key, RESULT_TTL_SECONDS)
        logging.info("Completed task %s", task_id)
    except Exception as exc:
        redis_client.hset(key, mapping={"status": "failed", "error": str(exc)})
        redis_client.expire(key, RESULT_TTL_SECONDS)
        logging.exception("Task %s failed", task_id)

def main() -> None:
    logging.info("Worker started")
    set_heartbeat()
    while True:
        try:
            set_heartbeat()
            item = redis_client.blpop(TASK_QUEUE, timeout=5)
            if item is None:
                continue
            _, raw_payload = item
            process_task(json.loads(raw_payload))
        except redis.RedisError:
            logging.exception("Redis connection error")
            time.sleep(2)
        except json.JSONDecodeError:
            logging.exception("Invalid task payload")

if __name__ == "__main__":
    main()
