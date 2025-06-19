import os
import uuid
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DID_API_KEY = os.getenv('DID_API_KEY')
DID_API_URL = "https://api.d-id.com"

def get_auth_header():
    if not DID_API_KEY:
        return None
    return {
        'Authorization': f'Basic {DID_API_KEY}',
        'Content-Type': 'application/json'
    }

@app.route('/uploadd', methods=['POST'])
def upload_to_did():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'}), 400

    filename = secure_filename(str(uuid.uuid4()) + os.path.splitext(file.filename)[1])
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        headers = get_auth_header()
        if not headers:
            return jsonify({'success': False, 'error': 'D-ID API key not configured'}), 500
        headers.pop('Content-Type', None)  # Remove Content-Type for multipart/form-data

        with open(filepath, 'rb') as f_read:
            files = {'image': f_read}
            response = requests.post(
                f"{DID_API_URL}/images",
                headers=headers,
                files=files
            )

        if response.status_code == 201:
            image_url = response.json().get('url')
            return jsonify({'success': True, 'image_url': image_url})
        else:
            return jsonify({'success': False, 'error': f'D-ID API error: {response.text}'}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=5100, ssl_context=('cert.pem', 'key.pem'))