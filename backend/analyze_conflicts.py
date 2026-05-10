import os
import django
from collections import defaultdict

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crudmodule.settings')
django.setup()

from api.models import EventParticipant

def analyze_conflicts():
    participants = EventParticipant.objects.all().select_related('event', 'nik')
    nik_to_events = defaultdict(list)
    for p in participants:
        nik_to_events[p.nik_id].append(p)
        
    conflicting_employees = 0
    total_conflicts = 0
    
    for nik, p_list in nik_to_events.items():
        if len(p_list) < 2:
            continue
            
        p_list.sort(key=lambda x: x.event.start_date)
        has_conflict = False
        for i in range(len(p_list)):
            for j in range(i + 1, len(p_list)):
                p1 = p_list[i]
                p2 = p_list[j]
                s1, e1 = p1.event.start_date, p1.event.end_date
                s2, e2 = p2.event.start_date, p2.event.end_date
                if (s1 <= e2) and (s2 <= e1):
                    has_conflict = True
                    total_conflicts += 1
        
        if has_conflict:
            conflicting_employees += 1
            
    print(f"Total Employees with conflicts: {conflicting_employees}")
    print(f"Total specific conflict pairs: {total_conflicts}")

if __name__ == "__main__":
    analyze_conflicts()
