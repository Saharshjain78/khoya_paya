import cv2
import face_recognition
import sqlite3
import numpy as np
import io
from PIL import Image
import sys
import os

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
                    
                    # Get face encoding
                    face_encodings = face_recognition.face_encodings(image_np)
                    if face_encodings:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(name)
                        print(f"Loaded face data for: {name}")
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
                
                # Convert BGR to RGB
                rgb_small_frame = small_frame[:, :, ::-1]
                
                # Find faces in current frame
                face_locations = face_recognition.face_locations(rgb_small_frame)
                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                
                # Process each face in the frame
                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    # Scale back up face locations
                    top *= 4
                    right *= 4
                    bottom *= 4
                    left *= 4
                    
                    # Check if the face matches any known face
                    matches = face_recognition.compare_faces(
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