import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import Employee, EventParticipant, EventSchedule

def check_chandra():
    chandra = Employee.objects.filter(full_name__icontains='Chandra Kurniawan Ananda').first()
    if not chandra:
        print("Chandra not found")
        return
    
    print(f"Checking for {chandra.full_name} (NIK: {chandra.nik})")
    
    year = '2026'
    participants = EventParticipant.objects.filter(nik=chandra).exclude(attendance_status='Absent').exclude(event__status='cancelled').filter(event__start_date__year=year)
    
    total_hours = 0
    for p in participants:
        event = p.event
        print(f"\nEvent: {event.training.training_title} (ID: {event.event_id}, Status: {event.status})")
        schedules = EventSchedule.objects.filter(event=event)
        event_hours = 0
        for s in schedules:
            if s.start_time and s.end_time:
                duration = (s.end_time.hour - s.start_time.hour) + (s.end_time.minute - s.start_time.minute) / 60.0
                print(f"  Schedule: {s.start_time} - {s.end_time} (Duration: {duration})")
                event_hours += duration
        print(f"  Event Total Hours: {event_hours}")
        total_hours += event_hours
    
    print(f"\nTotal Hours Calculated: {total_hours}")

if __name__ == "__main__":
    check_chandra()
