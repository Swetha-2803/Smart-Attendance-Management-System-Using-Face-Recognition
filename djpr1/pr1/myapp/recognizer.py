# myapp/recognizer.py
import cv2, face_recognition, numpy as np, os
from django.utils import timezone
from .models import Student, Attendance

def load_encodings():
    dataset_path = os.path.join("media", "dataset")
    encoded_faces, roll_numbers = [], []
    for file in os.listdir(dataset_path):
        if file.endswith((".jpg", ".png", ".jpeg")):
            rollno = os.path.splitext(file)[0]
            img = cv2.imread(os.path.join(dataset_path, file))
            if img is None:
                continue
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encodings = face_recognition.face_encodings(rgb_img)
            if len(encodings) > 0:
                encoded_faces.append(encodings[0])
                roll_numbers.append(rollno)
    return encoded_faces, roll_numbers

def recognize_face_from_frame(frame):
    encoded_faces, roll_numbers = load_encodings()
    tolerance = 0.5
    rgb_small = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = face_recognition.face_locations(rgb_small)
    encodings = face_recognition.face_encodings(rgb_small, faces)

    for encoding in encodings:
        matches = face_recognition.compare_faces(encoded_faces, encoding, tolerance)
        face_distances = face_recognition.face_distance(encoded_faces, encoding)
        if len(face_distances) > 0:
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                return roll_numbers[best_match_index]
    return None

def mark_attendance(rollno):
    student = Student.objects.filter(student_rollno=rollno).first()
    if student:
        today = timezone.now().date()
        current_time = timezone.now().time()
        Attendance.objects.update_or_create(
            student=student,
            date=today,
            defaults={
                "student_name": student.student_name,
                "student_rollno": student.student_rollno,
                "status": "Present",
                "time": current_time
            }
        )
        return student
    return None
