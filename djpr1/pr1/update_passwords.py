import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pr1.settings")
django.setup()

from django.contrib.auth.models import User

users = User.objects.exclude(is_superuser=True)
count = 0
for u in users:
    u.set_password(u.username)
    u.save()
    count += 1
print(f"Updated {count} user passwords to match their usernames.")
