from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    text = data.get('text')
    
    # Отправляем задачу воркеру
    response = requests.post(
        'http://worker:5001/generate',
        json={'text': text}
    )
    
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)