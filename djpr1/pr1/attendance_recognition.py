import cv2
import os
import numpy as np
from datetime import datetime
import threading
import django
import sys

# --- Setup Django environment ---
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pr1.settings")
django.setup()

from myapp.models import Student, Attendance
from django.utils import timezone

# --- Face Recognition Libraries ---
import mediapipe as mp
import face_recognition

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils


# --------------------------------------------------
# Load Dataset (Student Images)
# --------------------------------------------------
def load_known_faces():
    known_faces = []
    known_names = []
    dataset_dir = os.path.join("media", "dataset")

    print("📦 Loading dataset...")
    for file in os.listdir(dataset_dir):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(dataset_dir, file)
            try:
                img = cv2.imread(path)
                if img is None:
                    raise Exception("OpenCV could not read image.")
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                encodings = face_recognition.face_encodings(rgb_img)
                if encodings:
                    known_faces.append(encodings[0])
                    name = os.path.splitext(file)[0]
                    known_names.append(name)
                    print(f"✅ Loaded {name}")
                else:
                    print(f"⚠️ No face found in {file}")
            except Exception as e:
                print(f"❌ Error loading {file}: {e}")

    print(f"✅ Total students loaded: {len(known_names)}")
    return known_faces, known_names


# --------------------------------------------------
# Ensure Attendance Entry Exists (Default = Absent)
# --------------------------------------------------
def ensure_default_attendance():
    today = timezone.now().date()
    students = Student.objects.all()
    for student in students:
        attendance, created = Attendance.objects.get_or_create(
            student=student,
            date=today,
            defaults={
                "student_name": student.student_name,
                "student_rollno": student.student_rollno,
                "period1": "Absent",
                "period2": "Absent",
                "period3": "Absent",
                "period4": "Absent",
                "period5": "Absent",
                "period6": "Absent",
                "period7": "Absent",
            },
        )
        if created:
            print(f"🆕 Created default Absent record for {student.student_name}")


# --------------------------------------------------
# Mark Attendance
# --------------------------------------------------
def mark_attendance(name):
    today = timezone.now().date()
    current_time = timezone.now().time()

    student = Student.objects.filter(student_rollno=name).first()
    if not student:
        print(f"⚠️ Student with rollno {name} not found in DB")
        return

    attendance, created = Attendance.objects.get_or_create(
        student=student,
        date=today,
        defaults={
            "student_name": student.student_name,
            "student_rollno": student.student_rollno,
        },
    )

    # Find current period based on precise timetable timings
    now_time = datetime.now().time()
    from datetime import time as dt_time
    
    if dt_time(9, 0) <= now_time < dt_time(9, 55):
        period = "period1"
    elif dt_time(9, 55) <= now_time < dt_time(10, 50):
        period = "period2"
    elif dt_time(11, 10) <= now_time < dt_time(12, 0):
        period = "period3"
    elif dt_time(12, 0) <= now_time < dt_time(12, 50):
        period = "period4"
    elif dt_time(13, 40) <= now_time < dt_time(14, 30):
        period = "period5"
    elif dt_time(14, 30) <= now_time < dt_time(15, 20):
        period = "period6"
    elif dt_time(15, 20) <= now_time < dt_time(16, 10):
        period = "period7"
    else:
        period = None

    if period:
        current_status = getattr(attendance, period)
        if current_status != "Present":
            setattr(attendance, period, "Present")
            setattr(attendance, f"{period}_time", current_time)
            attendance.save()
            print(f"✅ Marked {student.student_name} as Present ({period})")
    else:
        print("⏰ Not within class period time, attendance not marked.")


# --------------------------------------------------
# Liveness Detection Helpers
# --------------------------------------------------
import math

def calculate_ear(eye_points):
    v1 = math.dist(eye_points[1], eye_points[5])
    v2 = math.dist(eye_points[2], eye_points[4])
    h = math.dist(eye_points[0], eye_points[3])
    if h == 0:
        return 0
    return (v1 + v2) / (2.0 * h)

# --------------------------------------------------
# Recognition Function
# --------------------------------------------------
camera_running = False

def calculate_iou(boxA, boxB):
    # box format: [top, right, bottom, left]
    xA = max(boxA[3], boxB[3])
    yA = max(boxA[0], boxB[0])
    xB = min(boxA[1], boxB[1])
    yB = min(boxA[2], boxB[2])
    
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    
    boxAArea = (boxA[1] - boxA[3] + 1) * (boxA[2] - boxA[0] + 1)
    boxBArea = (boxB[1] - boxB[3] + 1) * (boxB[2] - boxB[0] + 1)
    
    iou = interArea / float(boxAArea + boxBArea - interArea)
    return iou

def background_load():
    global known_faces, known_names, faces_loaded
    known_faces, known_names = load_known_faces()
    ensure_default_attendance()
    faces_loaded = True

def start_recognition():
    global camera_running, faces_loaded, known_faces, known_names
    if camera_running:
        print("Camera is already running.")
        return
    camera_running = True
    faces_loaded = False

    threading.Thread(target=background_load, daemon=True).start()

    cap = None
    for cam_index in [0, 1]:
        cap = cv2.VideoCapture(cam_index)
        if cap.isOpened():
            print(f"📸 Using camera index: {cam_index}")
            break
    if not cap or not cap.isOpened():
        print("❌ No camera found!")
        return

    print("🎥 Starting face recognition... Press 'q' to quit.")

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=5,  # Support 5 people
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    liveness_tracker = {}
    EAR_THRESHOLD = 0.22
    MOVEMENT_THRESHOLD = 3.0 # Pixels (lower for instant detection)

    process_frame = True
    frame_count = 0
    current_faces = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame_count += 1
        h, w, _ = frame.shape

        if not faces_loaded:
            cv2.putText(frame, "Loading AI Models... Please wait.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow('Attendance Camera', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # Face Recognition (ID)
        if process_frame:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            current_faces = []
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_faces, face_encoding, tolerance=0.45)
                name = "Unknown"
                if True in matches:
                    match_index = matches.index(True)
                    name = known_names[match_index]
                
                # Scale up coordinates
                top *= 4; right *= 4; bottom *= 4; left *= 4
                current_faces.append({'name': name, 'box': [top, right, bottom, left]})

        process_frame = not process_frame

        # Check if anyone needs liveness verification
        needs_liveness = False
        for face in current_faces:
            name = face['name']
            if name != "Unknown" and name not in liveness_tracker:
                liveness_tracker[name] = {'blinked': False, 'moved': False, 'nose_hist': [], 'verified': False}
            if name != "Unknown" and not liveness_tracker[name]['verified']:
                needs_liveness = True

        # Process Face Mesh ONLY if someone needs verification (CPU saver)
        mesh_results = None
        if needs_liveness:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mesh_results = face_mesh.process(rgb_frame)

        # Draw UI and Process Logic
        for face in current_faces:
            name = face['name']
            top, right, bottom, left = face['box']

            if name == "Unknown":
                color = (0, 0, 255)
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                continue

            tracker = liveness_tracker[name]

            # Process Liveness if not verified
            if not tracker['verified'] and mesh_results and mesh_results.multi_face_landmarks:
                # Find matching mesh for this face
                best_iou = 0
                best_mesh = None
                
                for mesh in mesh_results.multi_face_landmarks:
                    # Calculate mesh bounding box
                    x_coords = [int(lm.x * w) for lm in mesh.landmark]
                    y_coords = [int(lm.y * h) for lm in mesh.landmark]
                    mesh_box = [min(y_coords), max(x_coords), max(y_coords), min(x_coords)]
                    
                    iou = calculate_iou([top, right, bottom, left], mesh_box)
                    if iou > best_iou:
                        best_iou = iou
                        best_mesh = mesh
                
                if best_mesh and best_iou > 0.1: # Match found
                    # 1. Blink
                    right_eye_idx = [33, 160, 158, 133, 153, 144]
                    left_eye_idx = [362, 385, 387, 263, 373, 380]
                    
                    r_eye = [(int(best_mesh.landmark[i].x * w), int(best_mesh.landmark[i].y * h)) for i in right_eye_idx]
                    l_eye = [(int(best_mesh.landmark[i].x * w), int(best_mesh.landmark[i].y * h)) for i in left_eye_idx]
                    
                    if calculate_ear(r_eye) < EAR_THRESHOLD or calculate_ear(l_eye) < EAR_THRESHOLD:
                        tracker['blinked'] = True
                        
                    # 2. Movement (Instant < 1s)
                    nose_x = int(best_mesh.landmark[1].x * w)
                    nose_y = int(best_mesh.landmark[1].y * h)
                    
                    tracker['nose_hist'].append((nose_x, nose_y))
                    if len(tracker['nose_hist']) > 5: # Only 5 frames history! Super fast.
                        tracker['nose_hist'].pop(0)
                        
                    if len(tracker['nose_hist']) >= 3:
                        old_x, old_y = tracker['nose_hist'][0]
                        dist = math.dist((nose_x, nose_y), (old_x, old_y))
                        if dist > MOVEMENT_THRESHOLD:
                            tracker['moved'] = True

                    # Verify
                    if tracker['blinked'] and tracker['moved']:
                        tracker['verified'] = True
                        mark_attendance(name)

            # UI Display
            if tracker['verified']:
                color = (0, 255, 0)
                status_text = "Verified! Attendance Marked"
            else:
                color = (0, 255, 255)
                status_text = "Checking Liveness..."
                if tracker['blinked']: status_text += " [Blink OK]"
                if tracker['moved']: status_text += " [Move OK]"

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            show_text = True
            if not tracker['verified']:
                show_text = (frame_count // 10) % 2 == 0 # Blink Roll Number
            
            if show_text:
                cv2.putText(frame, name, (left, top - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            cv2.putText(frame, status_text, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        cv2.imshow('Attendance Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    face_mesh.close()
    cv2.destroyAllWindows()
    camera_running = False
    print("👋 Camera closed.")


# --------------------------------------------------
# Run Camera Thread (for Django)
# --------------------------------------------------
def start_camera_thread():
    t = threading.Thread(target=start_recognition)
    t.daemon = True
    t.start()


# --------------------------------------------------
# Run directly
# --------------------------------------------------
if __name__ == "__main__":
    start_recognition()
