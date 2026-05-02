from django.core.management.base import BaseCommand
from myapp.models import Student, Attendance
import face_recognition
import cv2
import os
from datetime import date

class Command(BaseCommand):
    help = "Mark attendance using live camera and face recognition"

    def handle(self, *args, **kwargs):
        print("📸 Opening Camera... Press 'q' to quit")

        # Step 1: Preload known student faces
        known_encodings = []
        known_rollnos = []

        images_path = "dataset/"  # student images folder (rollno.jpg format)
        for filename in os.listdir(images_path):
            if filename.endswith(".jpg"):
                rollno = filename.split(".")[0]
                img = face_recognition.load_image_file(os.path.join(images_path, filename))
                encoding = face_recognition.face_encodings(img)[0]
                known_encodings.append(encoding)
                known_rollnos.append(rollno)

        # Step 2: Open camera
        video_capture = cv2.VideoCapture(0)
        today = date.today()

        while True:
            ret, frame = video_capture.read()
            rgb_frame = frame[:, :, ::-1]

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                if True in matches:
                    match_index = matches.index(True)
                    rollno = known_rollnos[match_index]

                    try:
                        student = Student.objects.get(student_rollno=rollno)
                        Attendance.objects.update_or_create(
                            student=student,
                            date=today,
                            defaults={"status": "Present"}
                        )
                        print(f"{rollno} - ✅ Present")
                    except Student.DoesNotExist:
                        print(f"⚠ Unknown student: {rollno}")

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()
