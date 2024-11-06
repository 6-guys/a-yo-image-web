from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from PIL import Image
import requests
import os
import base64
import numpy as np
from io import BytesIO
import json
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

app = Flask(__name__)

BENTO_API_URL = "http://localhost:3000/generate_frames"

# 업로드 설정
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def preprocess_image(image_path):
    """
    이미지 파일 경로를 받아서 전처리 후 모델 입력 형식으로 변환하는 함수입니다.
    
    Args:
        image_path (str): 이미지 파일 경로
        repeat_count (int): 이미지를 반복하는 횟수 (디폴트는 10)
        
    Returns:
        dict: 전처리된 이미지와 라벨을 포함한 딕셔너리
    """
    # 이미지 로드 및 전처리
    img = Image.open(image_path)
    img_array = np.array(img)
    # print(img_array[80, :, :])
    # JSON 형식으로 반환
    return {"input_array": img_array.tolist()}


# 확장자 체크 함수
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_gif(frames, output_path="static/animation.gif", duration=200):
    """
    주어진 NumPy 배열 프레임을 사용하여 GIF 파일을 생성하는 함수.

    Parameters:
    frames (numpy array): 각 프레임 이미지가 포함된 배열, (num_frames, height, width, channels) 형식이어야 함.
    output_path (str): 저장할 GIF 파일의 경로.
    duration (int): 각 프레임의 표시 시간(밀리초 단위).
    """
    # 각 프레임을 PIL 이미지 객체로 변환
    pil_frames = [Image.fromarray(frame.astype(np.uint8)) for frame in frames]

    # 첫 번째 이미지를 기준으로 나머지 프레임을 추가하여 GIF 생성
    pil_frames[0].save(output_path, save_all=True, append_images=pil_frames[1:], format="GIF", loop=0, duration=duration)

# 루트 라우트
@app.route('/')
def index():
    return render_template('upload.html')

# 파일 업로드 라우트
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = "test_image.png"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('display_file', filename=filename))
    return redirect(request.url)

# 업로드된 이미지 표시 라우트
@app.route('/display/<filename>')
def display_file(filename):
    return render_template('upload.html', filename=filename)

# POST 요청: 이미지 전처리 후 BentoML에 전송
@app.route('/motion', methods=['POST'])
def create_motion():
    # 이미지 파일 경로 설정
    image_path = "static/uploads/test_image.png"
    
    # 이미지 전처리 수행
    payload = preprocess_image(image_path)
    
    # POST로 데이터 전송
    response = requests.post(BENTO_API_URL, json=payload)

    # 예측 결과 확인ㄱ
    if response.status_code == 200:
        data = json.loads(response.text)
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

        gif_path = "static/animation.gif"
        save_gif(data_array, gif_path)

        # HTML 템플릿으로 전달할 데이터 설정
        return render_template('result.html', images=images_base64, gif_url=gif_path)
    else:
        return "모션 생성 요청에 실패했습니다."

if __name__ == '__main__':
    app.run(debug=True)
