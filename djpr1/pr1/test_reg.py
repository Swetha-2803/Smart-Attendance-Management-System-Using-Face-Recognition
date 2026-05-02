from django.test import Client
from myapp.models import Student, ODForm, User, StudentProfile

c = Client()
c.login(username='staff1', password='staff123')

with open('test_img.jpg', 'wb') as f:
    f.write(b'fake image data')

with open('test_img.jpg', 'rb') as f:
    r = c.post('/register-student/', {'student_name':'Test2', 'student_rollno':'T002', 'student_image': f}, follow=True)

if 'messages' in r.context:
    for msg in r.context['messages']:
        print("Message:", msg.message)
else:
    print("No messages")

print("Students count:", Student.objects.count())
