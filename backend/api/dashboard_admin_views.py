from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Avg, F, Q
from django.db.models.functions import ExtractMonth
from collections import defaultdict
from .models import (
    TrainingEvent, EventParticipant, EventSchedule, EventCost, Employee, 
    TnaParticipant, TnaMaster, Budget, TrainingMaster, EvaluationResult
)

class DashboardAdminAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        year = request.query_params.get('year')
        division = request.query_params.get('division')
        search = request.query_params.get('search')
        course = request.query_params.get('course')
        
        events = TrainingEvent.objects.exclude(status='cancelled')
        
        if year:
            events = events.filter(start_date__year=year)
        else:
            from datetime import datetime
            year = str(datetime.now().year)
            events = events.filter(start_date__year=year)
            
        if search:
            events = events.filter(
                Q(training__training_title__icontains=search) |
                Q(training__course__course_name__icontains=search) |
                Q(training__vendor__vendor_name__icontains=search)
            )
            
        if course:
            events = events.filter(training__course__course_name=course)
        
        event_ids = events.values_list('event_id', flat=True)
        
        # Participants for events (exclude absent)
        participants = EventParticipant.objects.filter(event_id__in=event_ids).exclude(attendance_status='Absent')
        
        if division:
            # filter participants by division
            participants = participants.filter(nik__division__division_name__icontains=division)
            filtered_event_ids = participants.values_list('event_id', flat=True).distinct()
            events = events.filter(event_id__in=filtered_event_ids)
            event_ids = filtered_event_ids

        # HELPERS 
        def sum_costs(queryset):
            agg = queryset.aggregate(
                t=Sum('training_cost'), r=Sum('room_cost'), s=Sum('sppd_cost')
            )
            return float((agg['t'] or 0) + (agg['r'] or 0) + (agg['s'] or 0))

        # 1. Total Training
        total_training = events.count()

        # 2. Total Learners
        total_learners = participants.count()

        # 3. Total Employee
        total_employee_in_system = Employee.objects.count()
        if division:
            total_employee_in_system = Employee.objects.filter(division__division_name__icontains=division).count()
        total_employee_attended = participants.values('nik').distinct().count()

        # 4. Total Hours
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
        average_hours_val = total_hours_val / total_employee_attended if total_employee_attended > 0 else 0
        average_hours_by_all = total_hours_val / total_employee_in_system if total_employee_in_system > 0 else 0

        # 6. Budget Used (Actual Cost where status is Paid/Settled)
        costs = EventCost.objects.filter(event_id__in=event_ids)
        actual_costs = costs.filter(cost_type='Actual Cost')
        paid_costs = actual_costs.filter(status_cost__iexact='Paid')
        total_actual_cost_paid = sum_costs(paid_costs)
        
        # Online Training - ESG counts: distinct training count
        training_ids = events.values_list('training', flat=True).distinct()
        
        e_learning = TrainingMaster.objects.filter(training_id__in=training_ids, training_type='E-Learning').count()
        inhouse_training = TrainingMaster.objects.filter(training_id__in=training_ids, training_type='Inhouse Training').count()
        knowledge_sharing = TrainingMaster.objects.filter(training_id__in=training_ids, training_type='Knowledge Sharing').count()
        public_training = TrainingMaster.objects.filter(training_id__in=training_ids, training_type='Public Training').count()
        
        soft_skill = TrainingMaster.objects.filter(training_id__in=training_ids, training_category='Soft Skill').count()
        hard_skill = TrainingMaster.objects.filter(training_id__in=training_ids, training_category='Hard Skill').count()
        esg = TrainingMaster.objects.filter(training_id__in=training_ids, training_category='ESG').count()

        # Evaluations
        # Evaluation Scores from EventParticipant (Training Master)
        l1_avg = participants.filter(l1_score__isnull=False).aggregate(Avg('l1_score'))['l1_score__avg'] or 0
        l1_score = float(l1_avg)

        l2_avg = participants.filter(l2_score__isnull=False).aggregate(Avg('l2_score'))['l2_score__avg'] or 0
        l2_score = float(l2_avg)

        # TNA Coverage
        tna_qs = TnaMaster.objects.filter(tna_period__year=year)
        if division:
            tna_qs = tna_qs.filter(created_by__division__division_name=division)
        
        total_tna_count = tna_qs.count()
        
        # Realized TNA (Program)
        # Match by course and category
        realized_tna_count = 0
        # Optimization: get distinct pairs from events
        event_pairs = set(events.values_list('training__course', 'training__course_category'))
        for tna in tna_qs:
            if (tna.course_id, tna.course_category_id) in event_pairs:
                realized_tna_count += 1
        
        tna_program_coverage = f"{(realized_tna_count / total_tna_count * 100):.1f}%" if total_tna_count > 0 else "0%"
        
        # TNA Learners Coverage
        tna_participants_qs = TnaParticipant.objects.filter(tna__in=tna_qs)
        total_tna_learners = tna_participants_qs.values('nik').distinct().count()
        
        tna_learner_niks = list(tna_participants_qs.values_list('nik', flat=True).distinct())
        realized_learners_count = EventParticipant.objects.filter(
            event_id__in=event_ids, 
            nik_id__in=tna_learner_niks
        ).exclude(attendance_status='Absent').values('nik').distinct().count()
        
        tna_learners_coverage = f"{(realized_learners_count / total_tna_learners * 100):.1f}%" if total_tna_learners > 0 else "0%"

        # Budget Sub-info
        budget_obj = Budget.objects.filter(start_date_budget__year=year).order_by('-created_at').first()
        budget_val = float(budget_obj.total_budget) if budget_obj else 0.0

        total_actual_cost_unpaid = sum_costs(actual_costs.exclude(status_cost__iexact='Paid'))
        realisation = total_actual_cost_paid + total_actual_cost_unpaid
        budget_remaining = budget_val - realisation

        total_training_category = TrainingMaster.objects.filter(training_id__in=training_ids).values('training_category').distinct().count()
        total_training_type = TrainingMaster.objects.filter(training_id__in=training_ids).values('training_type').distinct().count()

        # Stats Formatting
        stats = {
            "total_hours": f"{float(total_hours_val):,.1f}".replace('.0', ''),
            "total_training": total_training,
            "average_hours": f"{float(average_hours_val):,.1f}".replace('.0', ''),
            "total_learners": total_learners,
            "budget_used": f"{float(total_actual_cost_paid):,.0f}",
            "budget_remaining": f"{float(budget_remaining):,.0f}",
            "total_training_category": total_training_category,
            "total_training_type": total_training_type,
            "total_employee": total_employee_attended,
            "presentase_karyawan": f"{(total_employee_attended / total_employee_in_system * 100):.1f}%" if total_employee_in_system > 0 else "0%",
            "e_learning": e_learning,
            "inhouse_training": inhouse_training,
            "knowledge_sharing": knowledge_sharing,
            "public_training": public_training,
            "soft_skill": soft_skill,
            "hard_skill": hard_skill,
            "esg": esg,
            "l1_score": f"{l1_score:.2f}",
            "l2_score": f"{l2_score:.2f}",
            "tna_program_coverage": tna_program_coverage,
            "tna_learners_coverage": tna_learners_coverage,
            "training_reach": f"{(total_employee_attended / total_employee_in_system * 100):.1f}%" if total_employee_in_system > 0 else "0%",
        }

        # CHARTS 
        months = range(1, 13)
        events_by_month = events.annotate(month=ExtractMonth('start_date'))
        
        def get_monthly_counts(queryset):
            counts = queryset.values('month').annotate(c=Count('event_id'))
            d = {c['month']: c['c'] for c in counts if c['month']}
            return [d.get(m, 0) for m in months]

        averageHours = [0] * 12
        budgetUsed = [0] * 12
        type_hours = {
            "Inhouse Training": [0]*12, 
            "Knowledge Sharing": [0]*12, 
            "Public Training": [0]*12, 
            "E-Learning": [0]*12
        }
        totalTrainingMonthly = [0] * 12
        totalHoursMonthly = [0] * 12
        totalLearnersMonthly = [0] * 12
        totalEmployeeMonthly = [0] * 12 # Unique employees per month

        for m in months:
            m_events = events_by_month.filter(month=m)
            m_event_ids = m_events.values_list('event_id', flat=True)
            
            # Monthly Hours
            m_scheds = EventSchedule.objects.filter(event_id__in=m_event_ids)
            m_hours = 0
            for sched in m_scheds:
                if sched.start_time and sched.end_time:
                    duration = (sched.end_time.hour - sched.start_time.hour) + (sched.end_time.minute - sched.start_time.minute) / 60.0
                    if duration > 0: 
                        m_hours += duration * part_counts_dict.get(sched.event_id, 0)
            
            m_participants = participants.filter(event_id__in=m_event_ids)
            m_employee_count = m_participants.values('nik').distinct().count()
            averageHours[m-1] = m_hours / m_employee_count if m_employee_count > 0 else 0
            
            # Monthly Totals
            totalTrainingMonthly[m-1] = m_events.count()
            totalHoursMonthly[m-1] = round(m_hours, 1)
            totalLearnersMonthly[m-1] = m_participants.count()
            totalEmployeeMonthly[m-1] = m_employee_count
            
            # Monthly Budget Used (Paid)
            m_costs_paid = costs.filter(event_id__in=m_event_ids, cost_type='Actual Cost', status_cost__iexact='Paid')
            budgetUsed[m-1] = sum_costs(m_costs_paid) / 1000000.0 # in Millions
            
            # Monthly Type Hours
            for t_type in type_hours.keys():
                type_m_events = m_events.filter(training__training_type=t_type)
                type_m_ids = type_m_events.values_list('event_id', flat=True)
                type_m_scheds = EventSchedule.objects.filter(event_id__in=type_m_ids)
                type_h = 0
                for sch in type_m_scheds:
                    if sch.start_time and sch.end_time:
                        dur = (sch.end_time.hour - sch.start_time.hour) + (sch.end_time.minute - sch.start_time.minute) / 60.0
                        type_h += dur * part_counts_dict.get(sch.event_id, 0)
                type_hours[t_type][m-1] = type_h

        # Calculate MoM Changes
        from datetime import datetime
        now = datetime.now()
        if not year or year == str(now.year):
            curr_idx = now.month - 1
        else:
            curr_idx = 11 # December for past years
        
        prev_idx = curr_idx - 1
        
        def calc_change(arr, c_idx, p_idx):
            cv = arr[c_idx]
            pv = arr[p_idx] if p_idx >= 0 else 0
            if pv == 0:
                return (f"{100}%" if cv > 0 else "0%"), True
            change_val = ((cv - pv) / pv) * 100
            return f"{abs(change_val):.1f}%", change_val >= 0

        tr_change, tr_up = calc_change(totalTrainingMonthly, curr_idx, prev_idx)
        hr_change, hr_up = calc_change(totalHoursMonthly, curr_idx, prev_idx)
        ln_change, ln_up = calc_change(totalLearnersMonthly, curr_idx, prev_idx)
        emp_change, emp_up = calc_change(totalEmployeeMonthly, curr_idx, prev_idx)
        av_change, av_up = calc_change(averageHours, curr_idx, prev_idx)

        stats.update({
            "total_training_change": tr_change, "total_training_up": tr_up,
            "total_hours_change": hr_change, "total_hours_up": hr_up,
            "total_learners_change": ln_change, "total_learners_up": ln_up,
            "total_employee_change": emp_change, "total_employee_up": emp_up,
            "average_hours_change": av_change, "average_hours_up": av_up,
        })

        charts = {
            "summaryCombined": {
                "Total Training": totalTrainingMonthly,
                "Total Hours": totalHoursMonthly,
                "Total Learners": totalLearnersMonthly
            },
            "averageHours": averageHours,
            "budgetUsed": budgetUsed,
            "totalTrainingCategory": {
                "Hard Skill": get_monthly_counts(events_by_month.filter(training__training_category='Hard Skill')),
                "Soft Skill": get_monthly_counts(events_by_month.filter(training__training_category='Soft Skill')),
                "ESG": get_monthly_counts(events_by_month.filter(training__training_category='ESG'))
            },
            "trainingTypeHours": type_hours,
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
                "E-Learning": get_monthly_counts(events_by_month.filter(training__training_type='E-Learning'))
            }
        }

        # TABLES 
        month_names = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
        
        # 10. Cost Table
        budget_obj = Budget.objects.filter(start_date_budget__year=year).first()
        if not budget_obj:
            budget_obj = Budget.objects.order_by('-start_date_budget').first()
        total_yearly_budget = float(budget_obj.total_budget) if budget_obj else 0.0
        
        running_total_realization = 0.0
        cost_table = []
        for m in months:
            m_events = events_by_month.filter(month=m)
            m_ids = m_events.values_list('event_id', flat=True)
            m_costs = EventCost.objects.filter(event_id__in=m_ids, cost_type='Actual Cost')
            
            m_paid = sum_costs(m_costs.filter(status_cost__iexact='Paid'))
            m_unpaid = sum_costs(m_costs.exclude(status_cost__iexact='Paid'))
            m_realization = m_paid + m_unpaid
            
            running_total_realization += m_realization
            m_remaining = total_yearly_budget - running_total_realization
            m_utilization = (running_total_realization / total_yearly_budget * 100) if total_yearly_budget > 0 else 0
            
            if m_realization > 0 or m == 1:
                cost_table.append({
                    "month": month_names[m-1],
                    "paid": m_paid,
                    "unpaid": m_unpaid,
                    "realisation": m_realization,
                    "remaining": m_remaining,
                    "utilization": f"{m_utilization:.2f}%"
                })

        # Table Helpers
        def get_table_data(queryset, group_field, label_name):
            data = []
            groups = queryset.values(group_field).distinct()
            for g in groups:
                val = g[group_field]
                if not val: continue
                
                g_events = queryset.filter(**{group_field: val})
                if group_field.startswith('nik__'):
                    # For participants grouping
                    g_learners = g_events.count()
                    g_event_ids = g_events.values_list('event_id', flat=True)
                    g_actual_events = events.filter(event_id__in=g_event_ids)
                    g_title_count = g_actual_events.count()
                    g_scheds = EventSchedule.objects.filter(event_id__in=g_event_ids)
                    
                    # Count participants per event only for this specific group
                    g_part_counts = {
                        item['event_id']: item['c']
                        for item in g_events.values('event_id').annotate(c=Count('event_participant_id'))
                    }
                else:
                    # For events grouping
                    g_learners = participants.filter(event__in=g_events).count()
                    g_title_count = g_events.count()
                    g_scheds = EventSchedule.objects.filter(event__in=g_events)
                    g_part_counts = part_counts_dict
                
                g_hours = 0
                for sch in g_scheds:
                    if sch.start_time and sch.end_time:
                        dur = (sch.end_time.hour - sch.start_time.hour) + (sch.end_time.minute - sch.start_time.minute) / 60.0
                        g_hours += dur * g_part_counts.get(sch.event_id, 0)
                
                data.append({
                    label_name: val,
                    "learners": g_learners,
                    "hours": round(g_hours, 1),
                    "title_count": g_title_count
                })
            return sorted(data, key=lambda x: x['learners'], reverse=True)

        # 11. Course Category
        course_cat_table = get_table_data(events, 'training__course_category__category_name', 'category')
        
        # 12. Course
        course_table = get_table_data(events, 'training__course__course_name', 'course')
        
        # 13. Training Type
        type_table = get_table_data(events, 'training__training_type', 'type')
        
        # 14. Training Category
        cat_table = get_table_data(events, 'training__training_category', 'category')
        
        # 15. Location
        loc_table = get_table_data(events, 'location__city', 'location')
        
        # 16. Vendors
        vend_table = get_table_data(events, 'training__vendor__vendor_name', 'vendor')
        
        # 17. Division
        div_table = get_table_data(participants, 'nik__division__division_name', 'division')
        
        # 18. Position
        pos_table = get_table_data(participants, 'nik__position_name', 'position')

        tables = {
            "cost": cost_table,
            "course_category": course_cat_table,
            "course": course_table,
            "training_type": type_table,
            "training_category": cat_table,
            "location": loc_table,
            "vendors": vend_table,
            "division": div_table,
            "position": pos_table
        }
        
        return Response({
            "stats": stats,
            "charts": charts,
            "tables": tables
        })
