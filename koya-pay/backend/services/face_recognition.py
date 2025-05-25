from flask import jsonify
import cv2
import numpy as np
import face_recognition

class FaceRecognitionService:
    def __init__(self, database):
        self.database = database
        self.known_face_encodings = []
        self.known_face_names = []
        self.load_faces()

    def load_faces(self):
        # Load known faces from the database
        faces = self.database.get_all_faces()
        for face in faces:
            image = face_recognition.load_image_file(face['image_path'])
            encoding = face_recognition.face_encodings(image)[0]
            self.known_face_encodings.append(encoding)
            self.known_face_names.append(face['name'])

    def recognize_faces(self, image):
        # Convert the image to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Find all face locations and encodings in the image
        face_locations = face_recognition.face_locations(rgb_image)
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

        matches = []
        for face_encoding in face_encodings:
            # Check if the face matches any known faces
            match = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            matches.append(match)

        return face_locations, matches

    def update_location(self, face_name, location):
        # Update the location of the matched face in the database
        self.database.update_face_location(face_name, location)

def process_image(image_path):
    # Load the image for processing
    image = cv2.imread(image_path)
    return image

def handle_face_recognition(image_path, database):
    image = process_image(image_path)
    service = FaceRecognitionService(database)
    face_locations, matches = service.recognize_faces(image)

    results = []
    for i, match in enumerate(matches):
        if True in match:
            matched_name = service.known_face_names[match.index(True)]
            results.append({
                'name': matched_name,
                'location': face_locations[i]
            })

    return jsonify(results)