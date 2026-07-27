from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Count, Sum, Q
from django.db.models.functions import ExtractMonth
from .models import Employee, EventParticipant, EventSchedule, TnaParticipant, TrainingEvent, TrainingMaster

class DashboardCardsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        year = request.query_params.get('year', '2026')
        
        try:
            profile = user.profile
            employee = profile.employee
            
            # Determine role correctly
            if user.is_superuser:
                role = "Super Administrator"
            elif user.groups.exists():
                role = user.groups.first().name
            else:
                role = "Employee"
        except Exception as e:
            return Response({"error": f"Profile not found: {str(e)}"}, status=404)

        # Determine employee scope (target_niks) based on role and view_mode
        view_mode = request.query_params.get('view_mode', 'admin')

        if view_mode == 'employee':
            target_niks = [employee.nik]
            employee_count = 1
        else:
            if role in ['Head of Division', 'Team Leader']:
                # Scope to entire division (includes self)
                division = employee.division
                target_niks = Employee.objects.filter(division=division).values_list('nik', flat=True)
                employee_count = len(target_niks)
            elif role in ['Super Administrator', 'Administrator', 'Dean']:
                # Admin sees everything
                target_niks = Employee.objects.all().values_list('nik', flat=True)
                employee_count = Employee.objects.count()
            else:
                # Role Employee - scope to self only
                target_niks = [employee.nik]
                employee_count = 1

        # Base filters: Completed and Draft events
        events = TrainingEvent.objects.filter(status='completed').filter(start_date__year=year)
        
        search = request.query_params.get('search')
        if search:
            events = events.filter(
                Q(training__training_title__icontains=search) |
                Q(training__course__course_name__icontains=search) |
                Q(training__vendor__vendor_name__icontains=search)
            )
        
        # Participants filter: Attendance Present, scope to target_niks, and completed/draft events
        participants = EventParticipant.objects.filter(
            nik__in=target_niks,
            attendance_status='Present',
            event__status='completed'
        ).filter(
            event__start_date__year=year
        )

        # Final filtered events for this scope (only events where target employees actually participated and were not absent)
        event_ids = participants.values_list('event_id', flat=True).distinct()
        events = events.filter(event_id__in=event_ids)

        # 1. Stats
        total_training = events.count()
        total_learners = participants.count()
        
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
        
        # Determine divisor for Average Hours based on role or view_mode
        if view_mode == 'employee' or role == 'Employee':
            divisor = total_training
        else:
            # For Head of Division, Team Leader, and Admins in this view
            divisor = participants.values('nik').distinct().count()

        average_hours_val = total_hours_val / divisor if divisor > 0 else 0
        
        l1_agg = participants.filter(l1_score__isnull=False).aggregate(Avg('l1_score'))['l1_score__avg']
        l2_agg = participants.filter(l2_score__isnull=False).aggregate(Avg('l2_score'))['l2_score__avg']
        l1_val = float(l1_agg) if l1_agg else 0.0
        l2_val = float(l2_agg) if l2_agg else 0.0

        # TNA Coverage Logic: Based on requirements (TnaParticipant) for the target_niks in the selected year
        tna_parts = TnaParticipant.objects.filter(nik__in=target_niks, tna__tna_period__year=year)
        total_tna = tna_parts.count()
        matched_tna = 0
        if total_tna > 0:
            # Attended courses in this year by the target employees (already filtered by year and status)
            attended_courses = set(events.values_list('training__course_id', flat=True))
            for tp in tna_parts:
                if tp.tna.course_id in attended_courses:
                    matched_tna += 1
            tna_coverage_val = (matched_tna / total_tna) * 100
        else:
            tna_coverage_val = 0

        # 2. Charts
        months = range(1, 13)
        events_by_month = events.annotate(month=ExtractMonth('start_date'))
        
        averageHours = [0] * 12
        totalTrainingMonthly = [0] * 12
        totalHoursMonthly = [0] * 12
        
        training_types = ["Inhouse Training", "Knowledge Sharing", "Public Training", "E-Learning"]
        training_categories = ["Hard Skill", "Soft Skill", "ESG"]
        
        type_counts = {t: [0]*12 for t in training_types}
        type_hours = {t: [0]*12 for t in training_types}
        cat_counts = {c: [0]*12 for c in training_categories}
        
        for m in months:
            m_events = events_by_month.filter(month=m)
            m_event_ids = m_events.values_list('event_id', flat=True)
            
            m_scheds = EventSchedule.objects.filter(event_id__in=m_event_ids)
            m_hours = 0
            for sch in m_scheds:
                if sch.start_time and sch.end_time:
                    dur = (sch.end_time.hour - sch.start_time.hour) + (sch.end_time.minute - sch.start_time.minute) / 60.0
                    m_hours += dur * part_counts_dict.get(sch.event_id, 0)
            
            totalTrainingMonthly[m-1] = m_events.count()
            totalHoursMonthly[m-1] = round(m_hours, 1)
            
            m_participants = participants.filter(event_id__in=m_event_ids)
            m_emp_count = m_participants.values('nik').distinct().count()
            averageHours[m-1] = m_hours / employee_count if employee_count > 0 else 0

            for t in training_types:
                type_m = m_events.filter(training__training_type=t)
                type_counts[t][m-1] = type_m.count()
                
                t_ids = type_m.values_list('event_id', flat=True)
                t_scheds = EventSchedule.objects.filter(event_id__in=t_ids)
                t_h = 0
                for sch in t_scheds:
                    if sch.start_time and sch.end_time:
                        dur = (sch.end_time.hour - sch.start_time.hour) + (sch.end_time.minute - sch.start_time.minute) / 60.0
                        t_h += dur * part_counts_dict.get(sch.event_id, 0)
                type_hours[t][m-1] = round(t_h, 1)

            for c in training_categories:
                cat_counts[c][m-1] = m_events.filter(training__training_category=c).count()

        return Response({
            "stats": {
                "total_training": total_training,
                "total_hours": f"{total_hours_val:,.1f}".replace('.0', ''),
                "average_hours": f"{average_hours_val:,.1f}".replace('.0', ''),
                "l1_score": f"{l1_val:.2f}",
                "l2_score": f"{l2_val:.2f}",
                "tna_coverage": f"{tna_coverage_val:.1f}%".replace('.0%', '%')
            },
            "charts": {
                "summaryCombined": {
                    "Total Training": totalTrainingMonthly,
                    "Total Hours": totalHoursMonthly,
                    "Total Learners": [0]*12 # Not needed for non-admin but keeps structure
                },
                "averageHours": averageHours,
                "totalTrainingCategory": cat_counts,
                "totalTrainingType": type_counts,
                "trainingTypeHours": type_hours
            }
        })
