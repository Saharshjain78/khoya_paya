import face_recognition
import cv2
import numpy as np
import os
import csv
from datetime import datetime
video_capture = cv2.VideoCapture(0)
jobs_image = face_recognition.load_image_file("jobs.jpg")
jobs_face_encoding = face_recognition.face_encodings(jobs_image)[0]
ratan_image = face_recognition.load_image_file("ratan.jpg")
ratan_face_encoding = face_recognition.face_encodings(ratan_image)[0]

known_face_encodings = [jobs_face_encoding, ratan_face_encoding]
known_face_names = ["Jobs", "Ratan"]




