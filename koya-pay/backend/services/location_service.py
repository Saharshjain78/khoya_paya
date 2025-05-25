from flask import jsonify, request
from models.database import db
from models.face_model import FaceModel

class LocationService:
    @staticmethod
    def update_location(face_id, new_location):
        face_entry = FaceModel.query.filter_by(id=face_id).first()
        if face_entry:
            face_entry.location = new_location
            db.session.commit()
            return jsonify({"message": "Location updated successfully."}), 200
        return jsonify({"message": "Face ID not found."}), 404

    @staticmethod
    def get_location(face_id):
        face_entry = FaceModel.query.filter_by(id=face_id).first()
        if face_entry:
            return jsonify({"face_id": face_entry.id, "location": face_entry.location}), 200
        return jsonify({"message": "Face ID not found."}), 404

    @staticmethod
    def get_all_locations():
        faces = FaceModel.query.all()
        locations = [{"face_id": face.id, "location": face.location} for face in faces]
        return jsonify(locations), 200