from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from myapp.models import Student, ODForm, User, StaffProfile, StudentProfile

c = Client()
res = c.login(username='staff1', password='staff123')
print("Staff Login success:", res)

img = SimpleUploadedFile("test.jpg", b"file_content", content_type="image/jpeg")
r = c.post('/register-student/', {'student_name':'Test3', 'student_rollno':'T003', 'student_image': img})

print("Register Status Code:", r.status_code)
print("Students count:", Student.objects.count())

c.logout()

res = c.login(username='23BIT031', password='student123')
print("Student Login success:", res)

doc = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
r = c.post('/upload-od/', {'date': '2026-04-19', 'reason': 'Sick', 'document': doc})
print("Upload OD Status Code:", r.status_code)
print("ODs count:", ODForm.objects.count())

