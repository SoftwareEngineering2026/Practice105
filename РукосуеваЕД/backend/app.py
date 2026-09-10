import os

from celery.result import AsyncResult
from flask import Flask, jsonify, request, send_from_directory

from celery_app import celery_app
from tasks import generate_avatar

MEDIA_DIR = os.environ.get("MEDIA_DIR", "/app/media")

app = Flask(__name__)


@app.post("/api/avatars")
def create_avatar():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Поле 'name' обязательно"}), 400

    task = generate_avatar.delay(name)
    return jsonify({"task_id": task.id}), 202


@app.get("/api/avatars/<task_id>")
def get_avatar_status(task_id):
    result = AsyncResult(task_id, app=celery_app)

    if result.state in ("PENDING", "STARTED"):
        return jsonify({"status": "pending"})
    if result.state == "FAILURE":
        return jsonify({"status": "failure", "error": str(result.result)}), 500
    if result.state == "SUCCESS":
        filename = result.result["filename"]
        return jsonify({"status": "success", "avatar_url": f"/api/media/{filename}"})

    return jsonify({"status": result.state.lower()})


@app.get("/api/media/<path:filename>")
def get_media(filename):
    return send_from_directory(MEDIA_DIR, filename)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})
