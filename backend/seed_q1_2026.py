import os
import django
import random
from datetime import timedelta, date, time
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import (
    Employee, Vendor, Course, CourseCategory, Division,
    TrainingMaster, TrainingEvent, EventLocation, EventSchedule,
    EventParticipant, EventCost, EventDocument
)
from django.db import transaction

def seed_more_trainings():
    print("Starting seeding of 15 additional trainings...")
    
    # Fetch lookups
    all_employees = list(Employee.objects.all())
    all_vendors = list(Vendor.objects.all())
    all_courses = list(Course.objects.all())
    all_categories = list(CourseCategory.objects.all())
    all_divisions = list(Division.objects.all())
    
    if not all_employees or not all_courses:
        print("Error: Employees or Courses table is empty. Please seed them first.")
        return

    pic_ids = [200335, 200331, 200329]
    pics = list(Employee.objects.filter(nik__in=pic_ids))
    if not pics:
        pics = all_employees[:3]

    titles = [
        "Digital Leadership Strategy", "Cybersecurity Awareness for Staff",
        "Financial Literacy for Professionals", "Mastering Public Speaking",
        "Strategic Human Resource Management", "Agile Project Management Basics",
        "Data Analytics with Power BI", "Effective Communication Skills",
        "Customer Experience Excellence", "Innovation and Design Thinking",
        "Emotional Intelligence at Work", "Advanced Excel for Business",
        "Marketing Analytics and ROI", "Change Management Best Practices",
        "Conflict Resolution in the Workplace"
    ]

    training_types = ['Inhouse Training', 'Public Training', 'E-Learning', 'Knowledge Sharing']
    training_categories = ['ESG', 'Hard Skill', 'Soft Skill']
    statuses = ['completed', 'completed', 'draft'] # Mostly completed since it's past
    
    cities = ['Jakarta', 'Bandung', 'Surabaya', 'Medan', 'Bali']
    venues = ['Hotel Indonesia Kempinski', 'Grand Hyatt', 'The Ritz-Carlton', 'Pullman Jakarta', 'Online - Zoom']
    
    # Q1 2026 Dates
    start_dates = []
    # January 2026
    for _ in range(5):
        start_dates.append(date(2026, 1, random.randint(5, 25)))
    # February 2026
    for _ in range(5):
        start_dates.append(date(2026, 2, random.randint(5, 25)))
    # March 2026
    for _ in range(5):
        start_dates.append(date(2026, 3, random.randint(5, 25)))
    
    random.shuffle(start_dates)

    created_count = 0
    
    try:
        with transaction.atomic():
            for i, title in enumerate(titles):
                course = random.choice(all_courses)
                cat = course.course_category or random.choice(all_categories)
                vendor = random.choice(all_vendors) if all_vendors else None
                pic = random.choice(pics)
                
                # Check for existing code to avoid unique constraint error
                training_code = f"TR-26-Q1-{1000 + i}"
                while TrainingMaster.objects.filter(training_code=training_code).exists():
                    training_code = f"TR-26-Q1-{random.randint(1000, 9999)}"
                
                tm = TrainingMaster.objects.create(
                    training_code=training_code,
                    course=course,
                    course_category=cat,
                    training_type=random.choice(training_types),
                    training_category=random.choice(training_categories),
                    training_title=title,
                    training_description=f"Automated training session for {title}",
                    pic=pic,
                    vendor=vendor,
                    estimated_cost=Decimal(random.randint(10000000, 50000000)),
                    is_active=True
                )
                
                s_date = start_dates[i]
                duration = random.randint(1, 2)
                e_date = s_date + timedelta(days=duration)
                
                status_val = random.choice(statuses)
                
                event = TrainingEvent.objects.create(
                    training=tm,
                    training_topic=title,
                    start_date=s_date,
                    end_date=e_date,
                    status=status_val,
                    enable_course_access=True,
                    enable_feedback=True,
                    enable_evaluations=True
                )
                
                # Location
                EventLocation.objects.create(
                    event=event,
                    city=random.choice(cities),
                    venue=random.choice(venues),
                    room=f"Meeting Room {random.randint(1, 10)}",
                    address="Jl. Jendral Sudirman No. 1"
                )
                
                # Schedule
                curr_date = s_date
                while curr_date <= e_date:
                    EventSchedule.objects.create(
                        event=event,
                        training_date=curr_date,
                        start_time=time(9, 0),
                        end_time=time(17, 0),
                        material_link="https://drive.google.com/drive/folders/sample",
                        instructor_name=f"Instructor {random.randint(1, 100)}"
                    )
                    curr_date += timedelta(days=1)
                
                # Participants (10-12)
                num_participants = random.randint(10, 12)
                # Pick unique employees
                selected_participants = random.sample(all_employees, min(num_participants, len(all_employees)))
                
                for emp in selected_participants:
                    # L2 logic: if > 4, it's 1-4 scale. 
                    # If we want a good score, 80-100 will be converted to 4 by the view logic if it were saved via API.
                    # Here we save directly to DB, so we should follow what the DB expects.
                    # The DB column for l2_score is Decimal(5,2).
                    # If I put 90.0, it stays 90.0. 
                    # But the frontend/dashboard might expect 1-4.
                    # Looking at views.py, it converts it DURING SAVE in the API.
                    # Let's see if there's any logic in the model or other views that expects 1-4.
                    
                    l2_val = Decimal(random.randint(75, 98))
                    
                    EventParticipant.objects.create(
                        event=event,
                        nik=emp,
                        attendance_status='Present',
                        l1_score=Decimal(random.uniform(3.8, 5.0)).quantize(Decimal('0.01')),
                        l2_score=l2_val
                    )
                
                # Cost
                div = random.choice(all_divisions) if all_divisions else None
                EventCost.objects.create(
                    event=event,
                    cost_center=div.division_id if div else "DSDM",
                    currency='IDR',
                    room_cost=Decimal(random.randint(1000000, 5000000)),
                    training_cost=Decimal(random.randint(5000000, 15000000)),
                    sppd_cost=Decimal(random.randint(500000, 2000000)),
                    cost_type='Actual Cost' if status_val == 'completed' else 'Estimate Cost',
                    status_cost='Paid'
                )
                
                # Document
                EventDocument.objects.create(
                    event=event,
                    document_type='Attendance',
                    file_name=f"Attendance_{training_code}.pdf",
                    file_url="https://drive.google.com/file/d/sample_attendance_link",
                    uploaded_by=pic
                )
                
                created_count += 1
                print(f"[{created_count}/15] Created Training: {training_code} - {title}")
                
        print(f"Successfully created {created_count} trainings.")
    except Exception as e:
        print(f"Error during seeding: {e}")

if __name__ == "__main__":
    seed_more_trainings()
