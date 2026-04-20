import os
import time
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

ftp_bp = Blueprint('ftp', __name__)

cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME', 'dqhqrjoe6'),
    api_key=os.getenv('CLOUDINARY_API_KEY', '359285996587242'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET', '')
)

_cache_images = []
_last_update = 0
CACHE_TIME = 60  # seconds


@ftp_bp.route('/upload-image', methods=['POST'])
def upload_image():
    file = request.files.get('imagen')
    if not file:
        return jsonify({'ok': False, 'error': 'No file'})

    if file.content_type not in ('image/jpeg', 'image/png'):
        return jsonify({'ok': False, 'error': 'Solo JPG y PNG'})

    try:
        result = cloudinary.uploader.upload(file, folder='gafitas')
        global _cache_images, _last_update
        _cache_images = []
        _last_update = 0
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500


@ftp_bp.route('/images')
def get_images():
    global _cache_images, _last_update

    if _cache_images and (time.time() - _last_update < CACHE_TIME):
        return jsonify(_cache_images)

    try:
        result = cloudinary.api.resources(
            type='upload',
            prefix='gafitas/',
            max_results=50,
            direction='desc'
        )
        images = [r['secure_url'] for r in result.get('resources', [])]
        _cache_images = images
        _last_update = time.time()
        return jsonify(images)
    except Exception as e:
        print('Error Cloudinary list:', e)
        return jsonify([])
