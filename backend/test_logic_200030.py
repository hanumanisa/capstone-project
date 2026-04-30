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

for emp in Employee.objects.filter(nik='200030'):
    all_eps = EventParticipant.objects.filter(nik=emp)
    comp_h = sum(get_hours(ep.event) for ep in all_eps if ep.event.status.lower() == 'completed')
    present_h = sum(get_hours(ep.event) for ep in all_eps if ep.attendance_status == 'Present')
    print(f"NIK: {emp.nik}, Comp: {comp_h}, Present: {present_h}")
