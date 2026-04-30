import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import Employee, EventParticipant

nik = '200030'
emp = Employee.objects.get(nik=nik)
participants = EventParticipant.objects.filter(nik=emp)

print(f"Employee: {emp.full_name} ({emp.nik})")
print(f"Total Participations: {participants.count()}")

for ep in participants:
    event = ep.event
    training = event.training
    schedules = event.schedules.all()
    total_hours = 0
    for sch in schedules:
        if sch.start_time and sch.end_time:
            from datetime import datetime, date
            dummy_date = date(2000, 1, 1)
            t1 = datetime.combine(dummy_date, sch.start_time)
            t2 = datetime.combine(dummy_date, sch.end_time)
            total_hours += (t2 - t1).total_seconds() / 3600
    
    print(f"  - Event ID: {event.event_id}, Status: {event.status}")
    print(f"    Training: {training.training_title} ({training.training_type})")
    print(f"    Schedules: {schedules.count()}, Calculated Hours: {total_hours}")

completed_events = [ep for ep in participants if ep.event.status.lower() == 'completed']
total_completed_hours = 0
for ep in completed_events:
    event = ep.event
    for sch in event.schedules.all():
        if sch.start_time and sch.end_time:
            from datetime import datetime, date
            dummy_date = date(2000, 1, 1)
            t1 = datetime.combine(dummy_date, sch.start_time)
            t2 = datetime.combine(dummy_date, sch.end_time)
            total_completed_hours += (t2 - t1).total_seconds() / 3600

print(f"\nTotal Completed Hours: {total_completed_hours}")
