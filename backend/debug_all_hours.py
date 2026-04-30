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

print("NIK | Comp Hours | Total Hours (Any Status) | Count Mismatch?")
for emp in Employee.objects.all():
    all_eps = EventParticipant.objects.filter(nik=emp)
    if not all_eps.exists():
        continue
        
    comp_h = sum(get_hours(ep.event) for ep in all_eps if ep.event.status.lower() == 'completed')
    total_h = sum(get_hours(ep.event) for ep in all_eps)
    
    if comp_h != total_h:
        print(f"{emp.nik} | {comp_h} | {total_h} | YES")
        for ep in all_eps:
             print(f"  - Event {ep.event_id}: {ep.event.status}, hours: {get_hours(ep.event)}")
