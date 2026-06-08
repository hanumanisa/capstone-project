import os
import sys
import django
sys.path.append('c:/xampp/htdocs/capstone-project/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.ai_agent import execute_ai_query
from django.contrib.auth.models import User

user = User.objects.get(id=330)
response, tokens = execute_ai_query(user, "berikan saya list nama karyawan yang sedivisi", [])

with open("scratch/test_output.txt", "wb") as f:
    f.write(response.encode("utf-8"))
