from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_rollno')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student_name', 'student_rollno', 'date', 'time',
                    'period1','period2','period3','period4','period5','period6','period7')
    list_filter = ('date',)
