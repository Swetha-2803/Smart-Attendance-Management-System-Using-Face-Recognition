from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('attendance/', views.attendance_dashboard, name='attendance'),
    path('export-excel/', views.export_attendance_excel, name="export_attendance_excel"),
    path('export-csv/', views.export_attendance_csv, name="export_attendance_csv"),
    path('export-word/', views.export_attendance_word, name="export_attendance_word"),
    path('export-pdf/', views.export_attendance_pdf, name="export_attendance_pdf"),
    path('dashboard/', views.attendance_dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('upload-od/', views.upload_od, name='upload_od'),
    path('approve-od/<int:od_id>/', views.approve_od, name='approve_od'),
    path('download-blank-od/', views.download_blank_od_form, name='download_blank_od_form'),
    path('upload-student-leave/', views.upload_student_leave, name='upload_student_leave'),
    path('approve-student-leave/<int:leave_id>/', views.approve_student_leave, name='approve_student_leave'),
    path('upload-staff-leave/', views.upload_staff_leave, name='upload_staff_leave'),
    path('approve-staff-leave/<int:leave_id>/', views.approve_staff_leave, name='approve_staff_leave'),

    path('enroll-user/', views.enroll_user, name='enroll_user'),
    path('bulk-enroll/', views.bulk_enroll, name='bulk_enroll'),
    path('update-attendance/', views.update_attendance, name='update_attendance'),
]