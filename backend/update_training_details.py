import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from django.db import transaction
from api.models import (
    TrainingMaster, TrainingEvent, EventSchedule,
    EventCost, EventParticipant
)

def update_training_details():
    # Find the recently generated trainings
    recent_trainings = TrainingMaster.objects.filter(training_description__startswith='Generated training based on TNA')
    
    count = 0
    try:
        with transaction.atomic():
            for tm in recent_trainings:
                course_name = tm.course.course_name if tm.course.course_name else tm.course.course_id
                
                # Get the event for this training
                events = TrainingEvent.objects.filter(training=tm)
                for event in events:
                    
                    # 1. Update Schedule material_link to syllabus format
                    schedules = EventSchedule.objects.filter(event=event)
                    for i, schedule in enumerate(schedules):
                        if i == 0:
                            schedule.material_link = f"Introduction to {course_name}, Fundamentals of {course_name}"
                        else:
                            schedule.material_link = f"Advanced Concepts of {course_name}, Case Studies"
                        schedule.save()
                        
                    # 2. Update Cost Center to "Divisi Sumber Daya Manusia" (DSDM22)
                    costs = EventCost.objects.filter(event=event)
                    for cost in costs:
                        cost.cost_center = 'DSDM22'
                        cost.save()
                        
                    # 3. Ensure exactly 1 participant is Absent, others Present
                    participants = list(EventParticipant.objects.filter(event=event))
                    if participants:
                        # Reset everyone to Present first
                        for p in participants:
                            p.attendance_status = 'Present'
                        
                        # Pick exactly 1 to be Absent
                        absent_participant = random.choice(participants)
                        absent_participant.attendance_status = 'Absent'
                        
                        # Bulk update is faster, or just save them
                        EventParticipant.objects.bulk_update(participants, ['attendance_status'])
                        
                count += 1
                
        print(f"Successfully updated {count} Training records (Syllabus, Cost Center, and Attendance).")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == '__main__':
    update_training_details()
