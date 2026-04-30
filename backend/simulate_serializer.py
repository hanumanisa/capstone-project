import os
import django
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import Employee
from api.serializers import EmployeeSerializer

emp = Employee.objects.get(nik='200047')
serializer = EmployeeSerializer(emp)
data = serializer.data

print(f"NIK: {data['nik']}, Name: {data['full_name']}")
print(f"Attendance: {data['attendance']}")
print(f"Total Hours: {data['total_hours']}")
print(f"TNA Count: {data['tna_count']}")
print(f"TNA Fulfilled: {data['tna_fulfilled']}")

print("\nEvents List:")
for ep in emp.eventparticipant_set.all():
    print(f"  - Event {ep.event_id}: {ep.event.training_topic}, Status {ep.event.status}, Att {ep.attendance_status}")
