# myapp/apps.py
from django.apps import AppConfig

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        import os
        if os.environ.get("RUN_MAIN", None) == "true":  # only when server runs
            try:
                from attendance_recognition import start_camera_thread
                start_camera_thread()
            except Exception:
                pass
