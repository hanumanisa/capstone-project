import os
import django
import random
from datetime import timedelta, date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from django.db import connection
from api.models import (
    TnaMaster, TnaParticipant, Employee, Vendor, 
    TrainingMaster, TrainingEvent, EventParticipant
)
from django.db import transaction

def fix_sequences():
    with connection.cursor() as cursor:
        try:
            cursor.execute("SELECT setval('tna_participant_tna_participant_id_seq', (SELECT MAX(tna_participant_id) FROM tna_participant));")
            cursor.execute("SELECT setval('training_master_training_id_seq', (SELECT MAX(training_id) FROM training_master));")
            cursor.execute("SELECT setval('training_events_event_id_seq', (SELECT MAX(event_id) FROM training_events));")
            cursor.execute("SELECT setval('event_participants_event_participant_id_seq', (SELECT MAX(event_participant_id) FROM event_participants));")
        except Exception as e:
            print("Could not fix sequences, maybe SQLite or different sequence name:", e)

def seed_trainings():
    fix_sequences()
    
    TARGET_TRAININGS = 40
    
    all_tnas = list(TnaMaster.objects.all())
    random.shuffle(all_tnas)
    
    selected_tnas = all_tnas[:TARGET_TRAININGS]
    
    if not selected_tnas:
        print("No TNA records found.")
        return

    pic_ids = [200335, 200331, 200329]
    pics = list(Employee.objects.filter(nik__in=pic_ids))
    if not pics:
        pics = list(Employee.objects.all()[:5])
        
    vendors = list(Vendor.objects.all())
    all_employees = list(Employee.objects.all())
    
    training_types = ['Inhouse Training', 'Public Training', 'E-Learning', 'Knowledge Sharing']
    training_categories = ['ESG', 'Hard Skill', 'Soft Skill']
    statuses = ['draft', 'completed', 'cancelled']
    
    created_count = 0
    
    try:
        with transaction.atomic():
            for tna in selected_tnas:
                course = tna.course
                course_category = tna.course_category
                
                training_code = f"TR-{random.randint(1000, 9999)}-{tna.tna_id}"
                while TrainingMaster.objects.filter(training_code=training_code).exists():
                    training_code = f"TR-{random.randint(10000, 99999)}"
                    
                training = TrainingMaster.objects.create(
                    training_code=training_code,
                    course=course,
                    course_category=course_category,
                    training_type=random.choice(training_types),
                    training_category=random.choice(training_categories),
                    training_title=f"Training for {course.course_name if course.course_name else course.course_id}",
                    training_description=f"Generated training based on TNA {tna.tna_id}",
                    pic=random.choice(pics),
                    vendor=random.choice(vendors) if vendors else None,
                    estimated_cost=Decimal(random.randint(1000000, 50000000)),
                    is_active=True
                )
                
                start_date = date.today() + timedelta(days=random.randint(1, 60))
                end_date = start_date + timedelta(days=random.randint(1, 5))
                
                event = TrainingEvent.objects.create(
                    training=training,
                    training_topic=training.training_title,
                    start_date=start_date,
                    end_date=end_date,
                    status=random.choice(statuses),
                    is_active=True,
                    enable_course_access=True,
                    enable_feedback=True,
                    enable_evaluations=True
                )
                
                num_participants = random.randint(15, 20)
                
                existing_tna_participants = list(TnaParticipant.objects.filter(tna=tna))
                participant_employees = [tp.nik for tp in existing_tna_participants]
                
                if len(participant_employees) < num_participants:
                    needed = num_participants - len(participant_employees)
                    available_emps = [e for e in all_employees if e not in participant_employees]
                    random.shuffle(available_emps)
                    added_emps = available_emps[:needed]
                    
                    for emp in added_emps:
                        TnaParticipant.objects.create(
                            tna=tna,
                            nik=emp
                        )
                    participant_employees.extend(added_emps)
                
                final_participants = participant_employees[:num_participants]
                
                for emp in final_participants:
                    EventParticipant.objects.create(
                        event=event,
                        nik=emp,
                        attendance_status=random.choice(['Present', 'Absent', None])
                    )
                    
                created_count += 1
                print(f"Created Training: {training_code} with {len(final_participants)} participants (TNA: {tna.tna_id})")
                
        print(f"Successfully created {created_count} Training records.")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    seed_trainings()
