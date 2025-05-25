import cv2
import sqlite3
import numpy as np
import io
from PIL import Image
import sys
import os
import dlib
import face_recognition_models

# Get face detector and face recognition models
face_detector = dlib.get_frontal_face_detector()
face_landmark_path = face_recognition_models.get_facial_landmarks_model_location()
pose_predictor = dlib.shape_predictor(face_landmark_path)
face_encoder = dlib.face_recognition_model_v1(face_recognition_models.get_face_recognition_model_location())

class LiveFaceRecognition:
    def __init__(self, db_path: str = 'database/faces.db'):
        try:
            if not os.path.exists(db_path):
                print(f"Error: Database not found at {db_path}")
                print("Please run database_creator.py first to create and populate the database.")
                sys.exit(1)

            self.known_face_encodings = []
            self.known_face_names = []
            self.load_faces_from_db(db_path)
            
        except Exception as e:
            print(f"Initialization error: {e}")
            sys.exit(1)
        
    def face_encodings(self, face_image, face_locations=None, num_jitters=1):
        """Get face encodings for an image"""
        if face_locations is None:
            face_locations = self.face_locations(face_image)
        else:
            face_locations = [dlib.rectangle(left, top, right, bottom) for (top, right, bottom, left) in face_locations]
        
        face_landmarks = [pose_predictor(face_image, face_location) for face_location in face_locations]
        return [np.array(face_encoder.compute_face_descriptor(face_image, landmark_set, num_jitters)) 
                for landmark_set in face_landmarks]
    
    def face_locations(self, img, number_of_times_to_upsample=1):
        """Get face locations from an image"""
        rects = face_detector(img, number_of_times_to_upsample)
        return [(rect.top(), rect.right(), rect.bottom(), rect.left()) for rect in rects]
    
    def compare_faces(self, known_face_encodings, face_encoding_to_check, tolerance=0.6):
        """Compare faces with a tolerance"""
        return [np.linalg.norm(known_encoding - face_encoding_to_check) <= tolerance 
                for known_encoding in known_face_encodings]
    
    def load_faces_from_db(self, db_path):
        """Load all faces from the database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.execute("SELECT name, photo FROM faces")
            
            for row in cursor:
                try:
                    name, photo_blob = row
                      # Convert BLOB to numpy array
                    image = Image.open(io.BytesIO(photo_blob))
                    image_np = np.array(image)
                    
                    # Get face locations first
                    face_locs = self.face_locations(image_np)
                    if face_locs:
                        # Convert to dlib rectangles for face_encodings
                        face_rects = [dlib.rectangle(left, top, right, bottom) for (top, right, bottom, left) in face_locs]
                        # Get landmarks directly using pose_predictor
                        face_landmarks = [pose_predictor(image_np, face_rect) for face_rect in face_rects]
                        # Get encodings directly using face_encoder
                        encodings = [np.array(face_encoder.compute_face_descriptor(image_np, landmark_set, 1)) 
                                   for landmark_set in face_landmarks]
                        
                        if encodings:
                            self.known_face_encodings.append(encodings[0])
                            self.known_face_names.append(name)
                            print(f"Loaded face data for: {name}")
                        else:
                            print(f"Warning: No face encoding could be computed for {name}")
                    else:
                        print(f"Warning: No face detected in the photo for {name}")
                
                except Exception as e:
                    print(f"Error processing face data for a record: {e}")
                    continue
            
            conn.close()
            
            if not self.known_face_names:
                print("No faces were loaded from the database. Please check your database content.")
                sys.exit(1)
                
            print(f"Successfully loaded {len(self.known_face_names)} faces from database")
            
        except Exception as e:
            print(f"Database error: {e}")
            sys.exit(1)
    
    def start_recognition(self):
        # Initialize video capture
        video_capture = cv2.VideoCapture(0)
        
        if not video_capture.isOpened():
            print("Error: Could not open video capture device (webcam)")
            print("Please check if your webcam is connected and not in use by another application")
            return
        
        print("Starting live recognition... Press 'q' to quit")
        try:
            while True:
                ret, frame = video_capture.read()
                if not ret:
                    print("Error: Failed to grab frame from webcam")
                    break
                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                
                # Convert BGR to RGB (making sure it's uint8 and has 3 channels)
                rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                
                # Find faces in current frame
                face_locs = []
                face_encodings = []
                
                try:
                    # Get face locations
                    face_locs = self.face_locations(rgb_small_frame)
                    
                    # Process each face directly to avoid format issues
                    if face_locs:
                        # Convert to dlib rectangles
                        face_rects = [dlib.rectangle(left, top, right, bottom) for (top, right, bottom, left) in face_locs]
                        # Get landmarks directly using pose_predictor
                        face_landmarks = [pose_predictor(rgb_small_frame, face_rect) for face_rect in face_rects]
                        # Get encodings directly using face_encoder
                        face_encodings = [np.array(face_encoder.compute_face_descriptor(rgb_small_frame, landmark_set, 1)) 
                                      for landmark_set in face_landmarks]
                except Exception as e:
                    print(f"Error processing current frame: {e}")
                    # Continue with the next frame even if this one fails
                    continue                  # Process each face in the frame
                for i, face_loc in enumerate(face_locs):
                    if i >= len(face_encodings):
                        # Skip if we don't have an encoding for this face
                        continue
                        
                    face_encoding = face_encodings[i]
                    top, right, bottom, left = face_loc
                    
                    # Scale back up face locations
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Check if the face matches any known face
                    try:
                        matches = self.compare_faces(
                            self.known_face_encodings, 
                            face_encoding, 
                            tolerance=0.6
                        )
                        name = "Unknown"
                        
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = self.known_face_names[first_match_index]
                        
                        # Draw rectangle around face
                        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                        
                        # Draw name label
                        label_y = bottom - 10 if bottom - 10 > 10 else bottom + 10
                        cv2.rectangle(frame, (left, label_y-35), (right, label_y), (0, 255, 0), cv2.FILLED)
                        font = cv2.FONT_HERSHEY_DUPLEX
                        cv2.putText(frame, name, (left + 6, label_y-6), font, 0.6, (255, 255, 255), 1)
                        # Print name in terminal
                        if name != "Unknown":
                            print(f"Recognized: {name}")
                            
                            # Add a more prominent display for recognized faces
                            # This ensures the recognized face is displayed clearly
                            font_scale = 0.8  # Slightly larger font
                            text_width, text_height = cv2.getTextSize(name, font, font_scale, 2)[0]
                            
                            # Draw a larger notification at the top of the frame for better visibility
                            notification_y = 30
                            cv2.rectangle(frame, (10, notification_y-text_height-10), 
                                         (text_width+20, notification_y+10), (0, 255, 0), cv2.FILLED)
                            cv2.putText(frame, f"Recognized: {name}", (15, notification_y), 
                                       font, font_scale, (255, 255, 255), 2)
                    except Exception as e:
                        print(f"Error matching face: {e}")
                        continue
                
                # Display the frame
                cv2.imshow('Face Recognition', frame)
                
                # Break loop on 'q' press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except Exception as e:
            print(f"Recognition error: {e}")
        
        finally:
            # Clean up
            video_capture.release()
            cv2.destroyAllWindows()

def main():
    try:
        recognition_system = LiveFaceRecognition()
        recognition_system.start_recognition()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
