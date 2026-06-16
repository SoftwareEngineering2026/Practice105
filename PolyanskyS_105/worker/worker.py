from flask import Flask, request, jsonify
import qrcode
import io
import base64
import time

app = Flask(__name__)

@app.route('/generate', methods=['POST'])
def generate_qr():
    data = request.get_json()
    text = data.get('text')
    
    # Имитация длительной задачи (2 секунды)
    time.sleep(2)
    
    # Генерация QR-кода
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(text)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Конвертация в base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    
    return jsonify({'qr': img_base64})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)