import os
import sys
import django
sys.path.append('c:/xampp/htdocs/capstone-project/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.ai_tools import search_employees
from django.contrib.auth.models import User

# User ID 2 is likely superadmin/admin based on previous contexts. Let's just try calling the function logic directly.
print(search_employees.invoke({"query": "", "division_name": None, "only_my_division": True, "requester_user_id": 1}))
