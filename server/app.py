from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import requests
import os
import base64
import numpy as np
from io import BytesIO
import json
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = Flask(__name__)

# 환경 변수에서 BENTO_API_URL 불러오기
BENTO_API_URL = os.getenv("BENTO_API_URL")

# 업로드 설정
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocess_image(image_path):
    """
    이미지 파일 경로를 받아서 전처리 후 모델 입력 형식으로 변환하는 함수입니다.
    """
    # 이미지 로드 및 전처리
    img = Image.open(image_path)
    img_array = np.array(img)
    return {"input_array": img_array.tolist()}

# 확장자 체크 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return "Flask server is running"


# 파일 업로드 라우트
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    if file and allowed_file(file.filename):
        filename = "test_image.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    return jsonify({"error": "File type not allowed"}), 400

# POST 요청: 이미지 전처리 후 BentoML에 전송
@app.route('/motion', methods=['POST'])
def create_motion():
    # 이미지 파일 경로 설정
    image_path = "static/uploads/test_image.png"
    
    # 이미지 전처리 수행
    payload = preprocess_image(image_path)
    
    # POST로 데이터 전송
    response = requests.post(BENTO_API_URL, json=payload)

    # 예측 결과 확인
    if response.status_code == 200:
        data = response.json()
        data_array = np.array(data)
        
        # 각 이미지를 개별적으로 Base64로 인코딩
        images_base64 = []
        for i in range(9):
            img = Image.fromarray((data_array[i]).astype(np.uint8))  # RGBA 이미지로 변환
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            img_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            images_base64.append(img_base64)
            buf.close()

        # JSON으로 인코딩된 이미지 목록 반환
        return jsonify({"images": images_base64}), 200
    else:
        return jsonify({"error": "Motion generation failed"}), 500

if __name__ == '__main__':
    app.run(debug=True)
