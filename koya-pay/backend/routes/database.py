from flask import Blueprint, request, jsonify
from models.database import db, Entry  # Assuming Entry is a model for database entries
from services.face_recognition import recognize_face

database_bp = Blueprint('database', __name__)

@database_bp.route('/entries', methods=['GET'])
def get_entries():
    entries = Entry.query.all()
    return jsonify([entry.to_dict() for entry in entries])

@database_bp.route('/entries', methods=['POST'])
def add_entry():
    data = request.json
    new_entry = Entry(name=data['name'], photo=data['photo'], location=data['location'])
    db.session.add(new_entry)
    db.session.commit()
    return jsonify(new_entry.to_dict()), 201

@database_bp.route('/scan', methods=['POST'])
def scan_photo():
    file = request.files['photo']
    if file:
        matches = recognize_face(file)
        return jsonify(matches)
    return jsonify({'error': 'No photo provided'}), 400

@database_bp.route('/update_location/<int:entry_id>', methods=['PUT'])
def update_location(entry_id):
    data = request.json
    entry = Entry.query.get(entry_id)
    if entry:
        entry.location = data['location']
        db.session.commit()
        return jsonify(entry.to_dict())
    return jsonify({'error': 'Entry not found'}), 404