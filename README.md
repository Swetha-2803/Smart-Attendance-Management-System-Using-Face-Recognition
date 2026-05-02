# Smart Attendance System

A comprehensive, Django-based Smart Attendance Management System that leverages facial recognition for automated attendance tracking. This project streamlines the process of marking attendance and includes robust workflows for handling student On-Duty (OD) and leave requests with multi-level approvals.

## Features

- **Facial Recognition Attendance:** Automated, period-wise attendance marking (P1-P7) using face detection and recognition algorithms (dlib & OpenCV).
- **Multi-Role Dashboards:** Distinct and modern dashboards tailored for Students, Staff, and HODs.
- **Automated OD & Leave Workflows:** Digital system for students to request On-Duty (OD) and leave, supporting multi-tier approval processes (Pending Staff -> Pending HOD -> Approved/Rejected).
- **Dynamic Face Dataset Management:** Automatically processes and saves student images into the dataset upon registration for facial recognition.
- **User Profiles & Authentication:** Secure login and registration flows for students and staff.

## Technology Stack

- **Backend:** Python, Django
- **Computer Vision:** dlib, OpenCV (Face Recognition)
- **Database:** SQLite3 (Configured by default, easily upgradeable to MySQL/PostgreSQL)
- **Frontend:** HTML5, CSS3, JavaScript (Responsive Dashboard UI)

## Prerequisites

- Python 3.8+
- CMake (Required for building dlib)
- Visual Studio Build Tools (If on Windows, for compiling dlib)

## Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install the required dependencies:**
   Make sure you have installed necessary dependencies. Common packages used in this project:
   ```bash
   pip install django dlib opencv-python pillow
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (Admin):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Access the application at `http://127.0.0.1:8000/`.

## Usage

- **Admin/Staff:** Register students and upload their images. The system will automatically build the facial recognition dataset.
- **Face Recognition:** Run the camera script or use the web interface to scan faces and mark attendance dynamically.
- **Students:** Log in to view attendance records, apply for Leave, or submit an OD form.
- **Staff/HOD:** Review, approve, or reject student Leave and OD requests from the dashboard.

## Project Structure

- `myapp/models.py`: Database schema definitions for Students, Staff, Attendance, and Leave/OD workflows.
- `attendance_recognition.py`: Core logic for face detection, encoding, and attendance logging.
- `templates/`: HTML files for Student/Staff dashboards, login, and registration.
- `media/`: Storage for student profile images, dataset, and uploaded leave/OD documents.

## License

This project is licensed under the MIT License.
