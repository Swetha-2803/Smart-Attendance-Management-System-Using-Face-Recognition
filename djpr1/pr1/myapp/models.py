import os
import shutil
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.utils import timezone

def student_images_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.student_rollno}.{ext}"
    return os.path.join('student_images', filename)

class Student(models.Model):   
    student_id = models.AutoField(primary_key=True)
    student_name = models.CharField(max_length=100)
    student_rollno = models.CharField(max_length=20, unique=True)
    student_image = models.ImageField(upload_to='dataset/', null=True, blank=True, unique=True)

    def __str__(self):
        return f"{self.student_name} ({self.student_rollno})"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    student_name = models.CharField(max_length=100, null=True, blank=True)
    student_rollno = models.CharField(max_length=20, null=True, blank=True)
    student_image = models.ImageField(upload_to="attendance_images/", null=True, blank=True)
    # Period-wise attendance columns (P1 - P7)
    CHOICES = [("Present", "Present"), ("Absent", "Absent"), ("OD", "OD"), ("Leave", "Leave")]
    period1 = models.CharField(max_length=10, default="Absent")
    period1_time = models.TimeField(null=True, blank=True)

    period2 = models.CharField(max_length=10, default="Absent")
    period2_time = models.TimeField(null=True, blank=True)

    period3 = models.CharField(max_length=10, default="Absent")
    period3_time = models.TimeField(null=True, blank=True)

    period4 = models.CharField(max_length=10, default="Absent")
    period4_time = models.TimeField(null=True, blank=True)

    period5 = models.CharField(max_length=10, default="Absent")
    period5_time = models.TimeField(null=True, blank=True)

    period6 = models.CharField(max_length=10, default="Absent")
    period6_time = models.TimeField(null=True, blank=True)

    period7 = models.CharField(max_length=10, default="Absent")
    period7_time = models.TimeField(null=True, blank=True)
    
    date = models.DateField(default=timezone.now)
    time = models.TimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'date')

    def __str__(self):
        return f"{self.student_name} - {self.date} - {self.status}"
class StaffAttendance(models.Model):
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    period1 = models.CharField(max_length=10, default="Absent")
    period2 = models.CharField(max_length=10, default="Absent")
    period3 = models.CharField(max_length=10, default="Absent")
    period4 = models.CharField(max_length=10, default="Absent")
    period5 = models.CharField(max_length=10, default="Absent")
    period6 = models.CharField(max_length=10, default="Absent")
    period7 = models.CharField(max_length=10, default="Absent")

    class Meta:
        unique_together = ('staff', 'date')

    def __str__(self):
        return f"{self.staff.staff_id} - {self.date}"

from django.contrib.auth.models import User

class StaffProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    staff_id = models.CharField(max_length=20, unique=True, null=True, blank=True)
    staff_image = models.ImageField(upload_to='dataset/', null=True, blank=True)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Staff"

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user.username} - Student"

class ODForm(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    reason = models.TextField()
    document = models.FileField(upload_to='od_forms/', null=True, blank=True)
    status_choices = [("Pending", "Pending"), ("Pending Staff", "Pending Staff"), ("Pending HOD", "Pending HOD"), ("Approved", "Approved"), ("Rejected", "Rejected")]
    status = models.CharField(max_length=20, choices=status_choices, default="Pending Staff")

    def __str__(self):
        if self.student:
            return f"OD - Student {self.student.student_rollno} - {self.date}"
        elif self.staff:
            return f"OD - Staff {self.staff.staff_id} - {self.date}"
        return f"OD - {self.date}"

class StudentLeaveForm(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=timezone.now)
    reason = models.TextField()
    document = models.FileField(upload_to='student_leave/', null=True, blank=True)
    status_choices = [("Pending Staff", "Pending Staff"), ("Pending HOD", "Pending HOD"), ("Approved", "Approved"), ("Rejected", "Rejected")]
    status = models.CharField(max_length=20, choices=status_choices, default="Pending Staff")

    def __str__(self):
        if self.student:
            return f"Leave - Student {self.student.student_rollno} - {self.date}"
        return f"Leave - {self.date}"

from django.db.models.signals import post_save, post_delete

class StaffLeaveForm(models.Model):
    staff = models.ForeignKey('StaffProfile', on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    reason = models.TextField()
    document = models.FileField(upload_to='staff_leave/', null=True, blank=True)
    status_choices = [("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")]
    status = models.CharField(max_length=20, choices=status_choices, default="Pending")

    def __str__(self):
        return f"Leave - Staff {self.staff.staff_id} - {self.date}"

from django.dispatch import receiver
from django.conf import settings
import os
import shutil

@receiver(post_save, sender=Student)
def copy_image_to_dataset(sender, instance, **kwargs):
    if instance.student_image:
        dataset_folder = os.path.join(settings.MEDIA_ROOT, 'dataset')
        os.makedirs(dataset_folder, exist_ok=True)

        ext = 'jpg'  # force jpg format
        dest_path = os.path.join(dataset_folder, f"{instance.student_rollno}.{ext}")
        src_path = os.path.abspath(instance.student_image.path)
        dest_path_abs = os.path.abspath(dest_path)

        # Skip copying if source and destination are the same
        if src_path != dest_path_abs:
            try:
                # Convert image to JPG if needed
                from PIL import Image
                img = Image.open(src_path).convert('RGB')
                img.save(dest_path_abs, 'JPEG')
                print(f"✅ Dataset image saved: {dest_path_abs}")
            except Exception as e:
                print(f"⚠️ Could not save image: {e}")
        else:
            print(f"ℹ️ Image already in dataset: {dest_path_abs}")

@receiver(post_delete, sender=Student)
def delete_dataset_image(sender, instance, **kwargs):
    if instance.student_image:
        dataset_folder = os.path.join(settings.MEDIA_ROOT, 'dataset')
        file_path = os.path.join(dataset_folder, f"{instance.student_rollno}.jpg")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Deleted dataset image: {file_path}")
