import os
import sys
import django
sys.path.append('c:/xampp/htdocs/capstone-project/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.ai_agent import execute_ai_query
from django.contrib.auth.models import User
from api.models import Profile, Employee

# Find Budi
users = User.objects.filter(first_name__icontains="Budi")
user = None
if users.exists():
    user = users.first()
else:
    # Try getting the one that has employee with name Budi
    emps = Employee.objects.filter(full_name__icontains="Budi")
    if emps.exists():
        emp = emps.first()
        if hasattr(emp, 'profile') and emp.profile.exists():
             user = emp.profile.first().user

if not user:
    user = User.objects.get(username='admin')

print("User found:", user.id, user.username)

try:
    response, tokens = execute_ai_query(user, "berikan saya list nama karyawan yang sedivisi", [])
    print("AI Response:", response)
except Exception as e:
    print("Exception:", e)
