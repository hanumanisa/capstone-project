import os
import django
import random
import datetime
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from django.db import connection, transaction
from django.contrib.auth.models import User
from api.models import (
    TrainingMaster, TrainingEvent, EventLocation, EventSchedule,
    EventCost, EvaluationForm
)

def get_realistic_title(course_name):
    templates = [
        "Mastering {course}",
        "Advanced {course} Workshop",
        "Fundamentals of {course}",
        "{course} for Professionals",
        "Strategic {course} Masterclass",
        "Practical Approaches to {course}",
        "{course}: Strategies and Applications",
        "Essential {course} Skills"
    ]
    return random.choice(templates).format(course=course_name)

def generate_mock_location():
    cities = ['Jakarta', 'Bandung', 'Surabaya', 'Yogyakarta', 'Bali']
    venues = ['Hotel Kempinski', 'Menara Mandiri', 'Head Office', 'Grand Hyatt', 'Ritz Carlton']
    rooms = ['Ballroom A', 'Meeting Room 1', 'Conference Room C', 'Auditorium', 'Training Room B']
    addresses = ['Jl. Jend. Sudirman No. 1', 'Jl. MH Thamrin No. 9', 'Jl. Gatot Subroto Kav. 10', 'SCBD Lot 4']
    
    return {
        'city': random.choice(cities),
        'venue': random.choice(venues),
        'room': random.choice(rooms),
        'address': random.choice(addresses)
    }

def generate_mock_instructor():
    instructors = ['Dr. Budi Santoso', 'Prof. Andi Wijaya', 'Siti Rahmawati, MBA', 'John Doe', 'Jane Smith', 'Ir. Hendra Kusuma']
    return random.choice(instructors)

def update_trainings():
    # Fix sequences if necessary for new inserts
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT setval('event_locations_event_location_id_seq', (SELECT COALESCE(MAX(event_location_id), 1) FROM event_locations));")
            cursor.execute("SELECT setval('event_schedules_schedule_id_seq', (SELECT COALESCE(MAX(schedule_id), 1) FROM event_schedules));")
            cursor.execute("SELECT setval('event_costs_cost_id_seq', (SELECT COALESCE(MAX(cost_id), 1) FROM event_costs));")
            cursor.execute("SELECT setval('evaluation_forms_form_id_seq', (SELECT COALESCE(MAX(form_id), 1) FROM evaluation_forms));")
        except Exception as e:
            pass
            
    # Find the newly created 40 trainings
    recent_trainings = TrainingMaster.objects.filter(training_description__startswith='Generated training based on TNA')
    
    admin_user = User.objects.first()
    
    count = 0
    try:
        with transaction.atomic():
            for tm in recent_trainings:
                # Update training title to be more realistic
                course_name = tm.course.course_name if tm.course.course_name else tm.course.course_id
                realistic_title = get_realistic_title(course_name)
                
                tm.training_title = realistic_title
                tm.save()
                
                # Get the event for this training
                events = TrainingEvent.objects.filter(training=tm)
                for event in events:
                    # Sync event topic with training title
                    event.training_topic = realistic_title
                    event.save()
                    
                    # 1. Location
                    if not hasattr(event, 'location'):
                        loc_data = generate_mock_location()
                        EventLocation.objects.create(
                            event=event,
                            city=loc_data['city'],
                            venue=loc_data['venue'],
                            room=loc_data['room'],
                            address=loc_data['address']
                        )
                    
                    # 2. Schedule
                    if not event.schedules.exists():
                        EventSchedule.objects.create(
                            event=event,
                            training_date=event.start_date,
                            start_time=datetime.time(9, 0),
                            end_time=datetime.time(17, 0),
                            material_link='https://drive.google.com/drive/folders/example-materials-link',
                            instructor_name=generate_mock_instructor()
                        )
                        
                        # Add a second day if event spans multiple days
                        if event.end_date > event.start_date:
                            EventSchedule.objects.create(
                                event=event,
                                training_date=event.start_date + datetime.timedelta(days=1),
                                start_time=datetime.time(9, 0),
                                end_time=datetime.time(17, 0),
                                material_link='https://drive.google.com/drive/folders/example-materials-link',
                                instructor_name=generate_mock_instructor()
                            )
                    
                    # 3. Cost
                    if not event.costs.exists():
                        EventCost.objects.create(
                            event=event,
                            cost_center='DIV-IT-001',
                            currency='IDR',
                            room_cost=Decimal(random.randint(2, 10)) * Decimal(1000000),
                            training_cost=Decimal(random.randint(5, 20)) * Decimal(1000000),
                            sppd_cost=Decimal(random.randint(1, 5)) * Decimal(1000000),
                            cost_type='Estimate Cost',
                            status_cost='Unpaid'
                        )
                        
                        # Also add actual cost for some variation
                        EventCost.objects.create(
                            event=event,
                            cost_center='DIV-IT-001',
                            currency='IDR',
                            room_cost=Decimal(random.randint(2, 10)) * Decimal(1000000),
                            training_cost=Decimal(random.randint(5, 20)) * Decimal(1000000),
                            sppd_cost=Decimal(random.randint(1, 5)) * Decimal(1000000),
                            cost_type='Actual Cost',
                            status_cost='Paid'
                        )
                
                # 4. Evaluation Form
                if not EvaluationForm.objects.filter(training_master=tm).exists():
                    EvaluationForm.objects.create(
                        form_name=f"Level 1 Evaluation - {realistic_title[:100]}",
                        training_master=tm,
                        description="Please provide your feedback for this training.",
                        deadline=datetime.datetime.now() + datetime.timedelta(days=30),
                        is_active=True,
                        created_by=admin_user,
                        created_at=datetime.datetime.now(),
                        form_type='L1'
                    )
                    
                count += 1
                
        print(f"Successfully updated {count} Training records with realistic titles, location, schedule, costs, and evaluations.")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    update_trainings()
