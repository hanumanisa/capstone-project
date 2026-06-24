import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import CourseCategory, Course

print("--- Course Categories ---")
for cc in CourseCategory.objects.all():
    print(f"ID: {cc.course_category_id}, Name: {cc.category_name}, Created: {cc.created_at}")

print("--- Courses ---")
for c in Course.objects.all():
    print(f"ID: {c.course_id}, Category ID: {c.course_category_id}, Name: {c.course_name}, Created: {c.created_at}")
