import os
import django
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import EventParticipant, TrainingEvent

def find_conflicts():
    participants = EventParticipant.objects.all().select_related('event', 'nik')
    conflicts = []
    
    # Simple N^2 check for small datasets, or group by NIK
    from collections import defaultdict
    nik_to_events = defaultdict(list)
    for p in participants:
        nik_to_events[p.nik_id].append(p)
        
    for nik, p_list in nik_to_events.items():
        if len(p_list) < 2:
            continue
            
        # Sort by start_date
        p_list.sort(key=lambda x: x.event.start_date)
        
        for i in range(len(p_list)):
            for j in range(i + 1, len(p_list)):
                p1 = p_list[i]
                p2 = p_list[j]
                
                s1, e1 = p1.event.start_date, p1.event.end_date
                s2, e2 = p2.event.start_date, p2.event.end_date
                
                if (s1 <= e2) and (s2 <= e1):
                    conflicts.append((p1, p2))
                    
    print(f"Found {len(conflicts)} conflicts.")
    for p1, p2 in conflicts:
        print(f"NIK: {p1.nik_id} ({p1.nik.full_name})")
        print(f"  Event A: {p1.event.training_topic} ({p1.event.start_date} to {p1.event.end_date})")
        print(f"  Event B: {p2.event.training_topic} ({p2.event.start_date} to {p2.event.end_date})")
        print("-" * 20)

if __name__ == "__main__":
    find_conflicts()
