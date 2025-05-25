from flask import Blueprint, request, jsonify
from backend.services.face_recognition import recognize_face
from backend.models.face_model import FaceModel

recognition_bp = Blueprint('recognition', __name__)

@recognition_bp.route('/api/recognize', methods=['POST'])
def recognize():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        matched_face = recognize_face(file)
        if matched_face:
            return jsonify({'matched': True, 'face': matched_face}), 200
        else:
            return jsonify({'matched': False}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recognition_bp.route('/api/update_location', methods=['POST'])
def update_location():
    data = request.json
    face_id = data.get('face_id')
    new_location = data.get('location')

    if not face_id or not new_location:
        return jsonify({'error': 'Invalid data'}), 400

    try:
        face_entry = FaceModel.query.get(face_id)
        if face_entry:
            face_entry.location = new_location
            face_entry.save()  # Assuming save method exists
            return jsonify({'message': 'Location updated successfully'}), 200
        else:
            return jsonify({'error': 'Face not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500