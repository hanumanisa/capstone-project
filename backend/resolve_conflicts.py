import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import EventParticipant

def resolve_conflicts():
    participants = EventParticipant.objects.all().select_related('event', 'nik').order_by('created_at')
    nik_to_participants = defaultdict(list)
    for p in participants:
        nik_to_participants[p.nik_id].append(p)
        
    to_delete = []
    
    for nik, p_list in nik_to_participants.items():
        if len(p_list) < 2:
            continue
            
        # We want to keep records. If there's an overlap, we mark for deletion.
        # We sort by event status (completed first) then created_at.
        p_list.sort(key=lambda x: (0 if x.event.status == 'completed' else 1, x.created_at))
        
        kept_participants = []
        
        for p in p_list:
            s1, e1 = p.event.start_date, p.event.end_date
            is_conflicting = False
            
            for kept in kept_participants:
                ks, ke = kept.event.start_date, kept.event.end_date
                if (s1 <= ke) and (ks <= e1):
                    is_conflicting = True
                    break
            
            if is_conflicting:
                to_delete.append(p)
            else:
                kept_participants.append(p)
                
    count = len(to_delete)
    print(f"Marked {count} conflicting participant records for deletion.")
    
    for p in to_delete:
        print(f"Deleting conflict: NIK {p.nik_id} from '{p.event.training_topic}' ({p.event.start_date} to {p.event.end_date})")
        p.delete()
        
    print("Cleanup completed.")

if __name__ == "__main__":
    resolve_conflicts()
