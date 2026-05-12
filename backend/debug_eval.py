import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import EvaluationAnswer, EvaluationForm, EvaluationResult, EventParticipant, Profile

print(f"Total Answers: {EvaluationAnswer.objects.count()}")
print(f"Total Results: {EvaluationResult.objects.count()}")
print(f"Total Participants: {EventParticipant.objects.count()}")
print(f"Total Profiles: {Profile.objects.count()}")

for form in EvaluationForm.objects.all():
    print(f"Form: {form.form_name} (ID: {form.form_id})")
    print(f"  Answers Count (Raw): {EvaluationAnswer.objects.filter(form=form).count()}")
    print(f"  Distinct Users: {EvaluationAnswer.objects.filter(form=form).values('user').distinct().count()}")
    
    if form.training_master_id:
        p_niks = EventParticipant.objects.filter(event__training_id=form.training_master_id).values_list('nik_id', flat=True)
        p_user_ids = Profile.objects.filter(employee_id__in=p_niks).values_list('user_id', flat=True)
        print(f"  Participants (NIKs): {list(p_niks)}")
        print(f"  Participant User IDs: {list(p_user_ids)}")
        
        filtered_count = EvaluationAnswer.objects.filter(form=form, user_id__in=p_user_ids).values('user').distinct().count()
        print(f"  Filtered Response Count: {filtered_count}")
