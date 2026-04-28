import uuid
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WORKER_URL = "http://worker:5001"


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    task_id = str(uuid.uuid4())
    requests.post(f"{WORKER_URL}/tasks", json={"task_id": task_id, **data})
    return jsonify({"task_id": task_id, "status": "queued"})


@app.route("/api/status/<task_id>")
def status(task_id):
    resp = requests.get(f"{WORKER_URL}/tasks/{task_id}")
    return jsonify(resp.json()), resp.status_code
