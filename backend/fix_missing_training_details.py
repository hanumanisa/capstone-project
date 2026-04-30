import os
import django
import random
from datetime import datetime, time, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import TrainingEvent, EventSchedule, EventLocation, EventCost, EventDocument, Employee

def fix_details():
    events = TrainingEvent.objects.all()
    print(f"Checking {events.count()} events...")
    
    locations = [
        {"city": "Jakarta", "venue": "Menara Mandiri", "room": "Assembly Hall", "address": "Jl. Jend. Sudirman No.54"},
        {"city": "Jakarta", "venue": "Hotel Indonesia Kempinski", "room": "Bali Room", "address": "Jl. M.H. Thamrin No.1"},
        {"city": "Bandung", "venue": "The Trans Luxury Hotel", "room": "Grand Ballroom", "address": "Jl. Gatot Subroto No.289"},
        {"city": "Surabaya", "venue": "Sheraton Surabaya", "room": "Kertajaya Room", "address": "Jl. Embong Malang No.25"},
        {"city": "Bali", "venue": "The Westin Resort", "room": "Mangupura Hall", "address": "Kawasan Pariwisata ITDC, Nusa Dua"},
    ]

    for event in events:
        updated = False
        
        # 1. Fix Location if missing
        if not hasattr(event, 'location'):
            loc_data = random.choice(locations)
            EventLocation.objects.create(
                event=event,
                city=loc_data['city'],
                venue=loc_data['venue'],
                room=loc_data['room'],
                address=loc_data['address']
            )
            print(f"  Added location for event {event.event_id}")
            updated = True
            
        # 2. Fix Schedule if missing
        if event.schedules.count() == 0:
            if not event.start_date or not event.end_date:
                # Should not happen with current seeding but for safety
                event.start_date = datetime.now().date()
                event.end_date = event.start_date + timedelta(days=2)
                event.save()
            
            curr_date = event.start_date
            while curr_date <= event.end_date:
                EventSchedule.objects.create(
                    event=event,
                    training_date=curr_date,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    material_link="https://drive.google.com/drive/folders/sample",
                    instructor_name=f"Instructor {random.randint(1, 100)}"
                )
                curr_date += timedelta(days=1)
            print(f"  Added schedule for event {event.event_id}")
            updated = True
            
        # 3. Fix Costs if missing
        if event.costs.count() == 0:
            # Estimate
            EventCost.objects.create(
                event=event,
                cost_type='Estimate Cost',
                cost_center='DSDM',
                training_cost=random.randint(5000000, 15000000),
                room_cost=random.randint(2000000, 8000000),
                sppd_cost=random.randint(1000000, 5000000)
            )
            # Actual
            EventCost.objects.create(
                event=event,
                cost_type='Actual Cost',
                cost_center='DSDM',
                training_cost=random.randint(4000000, 14000000),
                room_cost=random.randint(1500000, 7500000),
                sppd_cost=random.randint(800000, 4500000)
            )
            print(f"  Added costs for event {event.event_id}")
            updated = True
            
        # 4. Fix Documents if missing
        if event.documents.count() == 0:
            admin_emp = Employee.objects.filter(nik='200335').first() or Employee.objects.first()
            EventDocument.objects.create(
                event=event,
                file_name="Attendance List",
                document_type="PDF",
                file_url="https://drive.google.com/file/d/sample-id/view",
                uploaded_by=Employee.objects.get(nik='200335')
            )
            print(f"  Added document for event {event.event_id}")
            updated = True

        # 5. Set status to Completed if it's draft but has dates in the past
        if event.status == 'draft' and event.end_date < datetime.now().date():
            event.status = 'completed'
            event.save()
            print(f"  Updated status to COMPLETED for event {event.event_id}")
            updated = True

    print("Fix complete.")

if __name__ == "__main__":
    fix_details()
