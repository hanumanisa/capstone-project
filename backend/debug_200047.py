import os
import django
from datetime import datetime, date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import Employee, EventParticipant

def get_hours(ev):
    h = 0
    for s in ev.schedules.all():
        if s.start_time and s.end_time:
            dummy_date = date(2000, 1, 1)
            t1 = datetime.combine(dummy_date, s.start_time)
            t2 = datetime.combine(dummy_date, s.end_time)
            h += (t2 - t1).total_seconds() / 3600
    return h

for emp in Employee.objects.filter(nik='200047'):
    print(f"Employee: {emp.full_name} ({emp.nik})")
    all_eps = EventParticipant.objects.filter(nik=emp)
    print(f"Total Participations: {all_eps.count()}")
    for ep in all_eps:
        h = get_hours(ep.event)
        print(f"  - Event {ep.event_id}: Status={ep.event.status}, Attendance={ep.attendance_status}, Hours={h}")
        print(f"    Topic: {ep.event.training_topic}")
