import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import EventParticipant

participants = EventParticipant.objects.filter(l1_score__gt=4.0) | EventParticipant.objects.filter(l2_score__gt=4.0)
print(f"Found {participants.count()} participants with scores > 4.0")

for p in participants:
    if p.l1_score and p.l1_score > 4.0:
        print(f"Capping L1 score for {p.nik.full_name}: {p.l1_score} -> 4.0")
        p.l1_score = 4.0
    if p.l2_score and p.l2_score > 4.0:
        print(f"Capping L2 score for {p.nik.full_name}: {p.l2_score} -> 4.0")
        p.l2_score = 4.0
    p.save()

print("Finished capping scores.")
