import time
import random
import string
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, jsonify

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=4)
tasks = {}


def _strength(length, use_upper, use_digits, use_special):
    score = (
        (1 if length >= 8 else 0)
        + (1 if length >= 12 else 0)
        + (1 if use_upper else 0)
        + (1 if use_digits else 0)
        + (1 if use_special else 0)
    )
    return ["weak", "weak", "medium", "medium", "strong", "strong"][score]


def _run(task_id, length, count, use_upper, use_digits, use_special):
    tasks[task_id] = {"status": "running"}

    time.sleep(4)  # имитация тяжёлой задачи

    chars = string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation

    passwords = [
        {
            "password": "".join(random.choice(chars) for _ in range(length)),
            "strength": _strength(length, use_upper, use_digits, use_special),
        }
        for _ in range(count)
    ]

    tasks[task_id] = {"status": "done", "passwords": passwords}


@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json()
    task_id = data["task_id"]
    tasks[task_id] = {"status": "queued"}
    executor.submit(
        _run,
        task_id,
        int(data.get("length", 12)),
        int(data.get("count", 5)),
        bool(data.get("use_upper", True)),
        bool(data.get("use_digits", True)),
        bool(data.get("use_special", False)),
    )
    return jsonify({"task_id": task_id, "status": "queued"}), 202


@app.route("/tasks/<task_id>")
def get_task(task_id):
    task = tasks.get(task_id)
    if not task:
        return jsonify({"status": "not_found"}), 404
    return jsonify(task)
