from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F
from django.db.models.functions import ExtractMonth
from collections import defaultdict
from .models import (
    TrainingEvent, EventParticipant, EventSchedule, EventCost, Employee, 
    TnaParticipant, TnaMaster
)

class DashboardAdminAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        division = request.query_params.get('division')
        search = request.query_params.get('search')
        course = request.query_params.get('course')
        
        events = TrainingEvent.objects.all()
        
        if year:
            events = events.filter(start_date__year=year)
            
        if search:
            from django.db.models import Q
            events = events.filter(
                Q(training__training_title__icontains=search) |
                Q(training__course_name__icontains=search) |
                Q(training__vendor__vendor_name__icontains=search)
            )
            
        if course:
            events = events.filter(training__course_name__icontains=course)
        
        event_ids = events.values_list('event_id', flat=True)
        
        # Participants for these events
        participants = EventParticipant.objects.filter(event_id__in=event_ids)
        
        if division:
            # Need to filter participants by their division
            participants = participants.filter(nik__division__division_name__icontains=division)
            filtered_event_ids = participants.values_list('event_id', flat=True).distinct()
            events = events.filter(event_id__in=filtered_event_ids)
            event_ids = filtered_event_ids

        # 1. Total Training (Count of TrainingEvents)
        total_training = events.count()

        # 2. Total Learners (Count of EventParticipants)
        total_learners = participants.count()

        # 3. Total Employee (Distinct Employees in Participants)
        total_employee = participants.values('nik').distinct().count()

        # 4. Total Hours
        from django.db.models import Count
        part_counts_dict = {
            item['event_id']: item['c'] 
            for item in participants.values('event_id').annotate(c=Count('event_participant_id'))
        }
        
        schedules = EventSchedule.objects.filter(event_id__in=event_ids)
        total_hours_val = 0
        for sched in schedules:
            if sched.start_time and sched.end_time:
                duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                if duration > 0:
                    total_hours_val += duration * part_counts_dict.get(sched.event_id, 0)
        
        # 5. Average Hours
        average_hours_val = total_hours_val / total_employee if total_employee > 0 else 0

        # 6. Budget Used & Remaining
        costs = EventCost.objects.filter(event_id__in=event_ids)
        
        actual_costs = costs.filter(cost_type='Actual Cost')
        estimate_costs = costs.filter(cost_type='Estimate Cost')
        
        def sum_costs(queryset):
            agg = queryset.aggregate(
                t=Sum('training_cost'), r=Sum('room_cost'), s=Sum('sppd_cost')
            )
            return float((agg['t'] or 0) + (agg['r'] or 0) + (agg['s'] or 0))

        total_actual_cost = sum_costs(actual_costs)
        total_estimate_cost = sum_costs(estimate_costs)
        budget_remaining = total_estimate_cost - total_actual_cost

        # 7. Categories
        hard_skill = events.filter(training__training_category='Hard Skill').count()
        soft_skill = events.filter(training__training_category='Soft Skill').count()
        esg = events.filter(training__training_category='ESG').count()

        # 8. Types
        online_training = events.filter(training__training_type='E-Learning').count()
        inhouse = events.filter(training__training_type='Inhouse Training').count()
        public = events.filter(training__training_type='Public Training').count()
        knowledge_sharing = events.filter(training__training_type='Knowledge Sharing').count()

        # 9. L1 and L2
        l1_agg = participants.filter(l1_score__isnull=False).aggregate(Avg('l1_score'))['l1_score__avg']
        l2_agg = participants.filter(l2_score__isnull=False).aggregate(Avg('l2_score'))['l2_score__avg']
        l1_val = float(l1_agg) if l1_agg else 0.0
        l2_val = float(l2_agg) if l2_agg else 0.0

        # 10. TNA Program Coverage & Learners Coverage
        all_tna_parts = TnaParticipant.objects.all()
        if division:
            all_tna_parts = all_tna_parts.filter(nik__division__division_name__icontains=division)
        
        total_tna_learners = all_tna_parts.values('nik').distinct().count()
        total_tna_programs = TnaMaster.objects.count()

        # Employees who have a TNA and attended a matching training
        matched_learners = set()
        matched_programs = set()

        # To optimize, get all attended courses per nik
        attended_map = defaultdict(set)
        for p in participants.select_related('event__training'):
            attended_map[p.nik_id].add(p.event.training.course_id)

        for tp in all_tna_parts.select_related('tna'):
            if tp.tna.course_id in attended_map[tp.nik_id]:
                matched_learners.add(tp.nik_id)
                matched_programs.add(tp.tna_id)

        tna_learners_coverage = (len(matched_learners) / total_tna_learners * 100) if total_tna_learners > 0 else 0
        tna_program_coverage = (len(matched_programs) / total_tna_programs * 100) if total_tna_programs > 0 else 0

        # FORMAT STATS
        stats = {
            "total_training": total_training,
            "online_training": online_training,
            "total_hours": f"{float(total_hours_val):,.1f}".replace('.0', ''),
            "soft_skill": soft_skill,
            "total_learners": total_learners,
            "hard_skill": hard_skill,
            "total_employee": total_employee,
            "esg": esg,
            "average_hours": f"{float(average_hours_val):,.1f}".replace('.0', ''),
            "l1_score": f"{l1_val:.2f}",
            "budget_used": f"{float(total_actual_cost):,.0f}",
            "budget_remaining": f"{float(budget_remaining):,.0f}",
            "l2_score": f"{l2_val:.2f}",
            "inhouse_training": inhouse,
            "tna_learners_coverage": f"{tna_learners_coverage:.1f}%".replace('.0%', '%'),
            "knowledge_sharing": knowledge_sharing,
            "tna_program_coverage": f"{tna_program_coverage:.1f}%".replace('.0%', '%'),
            "public_training": public
        }

        # --- CHARTS ---
        # 12 Months mapping
        months = range(1, 13)
        events_by_month = events.annotate(month=ExtractMonth('start_date'))
        
        # Helper for monthly aggregation
        def get_monthly_counts(queryset):
            counts = queryset.values('month').annotate(c=Count('event_id'))
            d = {c['month']: c['c'] for c in counts if c['month']}
            return [d.get(m, 0) for m in months]

        averageHours = [0] * 12
        budgetUsed = [0] * 12
        # Calculate monthly budget and hours
        for m in months:
            m_events = events_by_month.filter(month=m)
            m_event_ids = m_events.values_list('event_id', flat=True)
            
            m_scheds = EventSchedule.objects.filter(event_id__in=m_event_ids)
            m_hours = 0
            for sched in m_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0: 
                        m_hours += duration * part_counts_dict.get(sched.event_id, 0)
            m_employee_count = participants.filter(event_id__in=m_event_ids).values('nik').distinct().count()
            averageHours[m-1] = m_hours / m_employee_count if m_employee_count > 0 else 0
            
            m_costs = actual_costs.filter(event_id__in=m_event_ids)
            m_cost_val = sum_costs(m_costs)
            budgetUsed[m-1] = m_cost_val / 1000000.0  # in millions

        charts = {
            "averageHours": averageHours,
            "budgetUsed": budgetUsed,
            "totalTrainingCategory": {
                "Hard Skill": get_monthly_counts(events_by_month.filter(training__training_category='Hard Skill')),
                "Soft Skill": get_monthly_counts(events_by_month.filter(training__training_category='Soft Skill')),
                "ESG": get_monthly_counts(events_by_month.filter(training__training_category='ESG'))
            },
            "trainingCategoryHours": {
                "Hard Skill": [0]*12, "Soft Skill": [0]*12, "ESG": [0]*12 # Simplified for performance, can enhance later
            },
            "presentaseKaryawan": {
                "Direktur": participants.filter(nik__position_name__icontains='Direktur').values('nik').distinct().count(),
                "Kepala Divisi": participants.filter(nik__position_name__icontains='Kepala Divisi').values('nik').distinct().count(),
                "Team Leader": participants.filter(nik__position_name__icontains='Team Leader').values('nik').distinct().count(),
                "Staff": participants.filter(nik__position_name__icontains='Staff').values('nik').distinct().count()
            },
            "totalTrainingType": {
                "Inhouse Training": get_monthly_counts(events_by_month.filter(training__training_type='Inhouse Training')),
                "Knowledge Sharing": get_monthly_counts(events_by_month.filter(training__training_type='Knowledge Sharing')),
                "Public Training": get_monthly_counts(events_by_month.filter(training__training_type='Public Training')),
                "Online Training": get_monthly_counts(events_by_month.filter(training__training_type='E-Learning'))
            }
        }

        # --- TABLES ---
        # 1. Category Table
        cat_table = []
        for cat in ['Hard Skill', 'Soft Skill', 'ESG']:
            cat_events = events.filter(training__training_category=cat)
            cat_learners = EventParticipant.objects.filter(event__in=cat_events).values('nik').distinct().count()
            
            cat_scheds = EventSchedule.objects.filter(event__in=cat_events)
            cat_hours = 0
            for sched in cat_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0:
                        cat_hours += duration * part_counts_dict.get(sched.event_id, 0)
            
            cat_table.append({
                "category": cat,
                "learners": cat_learners,
                "hours": round(cat_hours, 1),
                "title_count": cat_events.count()
            })

        # 2. Location Table
        loc_table = []
        locations = events.values_list('location__city', flat=True).distinct()
        for loc in locations:
            if not loc: continue
            loc_events = events.filter(location__city=loc)
            loc_learners = EventParticipant.objects.filter(event__in=loc_events).values('nik').distinct().count()
            
            loc_scheds = EventSchedule.objects.filter(event__in=loc_events)
            loc_hours = 0
            for sched in loc_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0:
                        loc_hours += duration * part_counts_dict.get(sched.event_id, 0)
            
            loc_table.append({
                "location": loc,
                "learners": loc_learners,
                "hours": round(loc_hours, 1),
                "title_count": loc_events.count()
            })
        loc_table = sorted(loc_table, key=lambda x: x['title_count'], reverse=True)[:5] # top 5

        # 3. Vendors Table
        vend_table = []
        vendors = events.values_list('training__vendor__vendor_name', flat=True).distinct()
        for vend in vendors:
            if not vend: continue
            vend_events = events.filter(training__vendor__vendor_name=vend)
            vend_learners = EventParticipant.objects.filter(event__in=vend_events).values('nik').distinct().count()
            
            vend_scheds = EventSchedule.objects.filter(event__in=vend_events)
            vend_hours = 0
            for sched in vend_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0:
                        vend_hours += duration * part_counts_dict.get(sched.event_id, 0)
                    
            vend_table.append({
                "vendor": vend,
                "learners": vend_learners,
                "hours": round(vend_hours, 1),
                "title_count": vend_events.count()
            })
        vend_table = sorted(vend_table, key=lambda x: x['title_count'], reverse=True)[:5] # top 5

        # 4. Division Table
        div_table = []
        divs = participants.values_list('nik__division__division_name', flat=True).distinct()
        for div in divs:
            if not div: continue
            div_parts = participants.filter(nik__division__division_name=div)
            div_learners = div_parts.values('nik').distinct().count()
            div_emp_total = Employee.objects.filter(division__division_name=div).count()
            
            div_events = events.filter(event_id__in=div_parts.values_list('event_id', flat=True))
            div_scheds = EventSchedule.objects.filter(event__in=div_events)
            div_hours = 0
            for sched in div_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0:
                        div_hours += duration * part_counts_dict.get(sched.event_id, 0)
            
            div_table.append({
                "division": div,
                "employee": div_emp_total,
                "learners": div_learners,
                "hours": round(div_hours, 1)
            })
        div_table = sorted(div_table, key=lambda x: x['learners'], reverse=True)[:5] # top 5

        # 5. Position Table
        pos_table = []
        positions = participants.values_list('nik__position_name', flat=True).distinct()
        for pos in positions:
            if not pos: continue
            pos_parts = participants.filter(nik__position_name=pos)
            pos_learners = pos_parts.values('nik').distinct().count()
            pos_emp_total = Employee.objects.filter(position_name=pos).count()
            
            pos_events = events.filter(event_id__in=pos_parts.values_list('event_id', flat=True))
            pos_scheds = EventSchedule.objects.filter(event__in=pos_events)
            pos_hours = 0
            for sched in pos_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0:
                        pos_hours += duration * part_counts_dict.get(sched.event_id, 0)
            
            pos_table.append({
                "position": pos,
                "employee": pos_emp_total,
                "learners": pos_learners,
                "hours": round(pos_hours, 1)
            })
        pos_table = sorted(pos_table, key=lambda x: x['learners'], reverse=True)[:5]

        # 6. Cost Table (by Month)
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        cost_table = []
        for m in months:
            m_events = events_by_month.filter(month=m)
            m_event_ids = m_events.values_list('event_id', flat=True)
            
            m_actual_costs = actual_costs.filter(event_id__in=m_event_ids)
            m_estimate_costs = estimate_costs.filter(event_id__in=m_event_ids)
            
            m_actual_val = sum_costs(m_actual_costs)
            m_estimate_val = sum_costs(m_estimate_costs)
            m_remaining = m_estimate_val - m_actual_val
            m_percentage = (m_actual_val / m_estimate_val * 100) if m_estimate_val > 0 else 0
            
            if m_actual_val > 0 or m_estimate_val > 0:
                cost_table.append({
                    "month": month_names[m-1],
                    "realisation": m_actual_val,
                    "remaining": m_remaining,
                    "percentage": f"{m_percentage:.2f}%"
                })

        tables = {
            "category": cat_table,
            "location": loc_table,
            "vendors": vend_table,
            "division": div_table,
            "position": pos_table,
            "cost": cost_table
        }
        
        return Response({
            "stats": stats,
            "charts": charts,
            "tables": tables
        })
