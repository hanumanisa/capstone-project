import json
from datetime import datetime, date
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from api.models import (
    Employee, Division, Directorate, CourseCategory, Course,
    EvaluationForm, TrainingMaster, TrainingEvent, EventParticipant,
    EventCost, Budget, TnaMaster, TnaPeriod, TnaParticipant, Vendor, Hotel, EvaluationResult
)
from langchain_core.tools import tool
from contextvars import ContextVar

# Context Variable to securely look up the logged-in user ID
current_user_id_var = ContextVar('current_user_id', default=None)

def get_user_role_and_division(user_id: int):
    """
    Mengambil role, employee, dan division_id berdasarkan user_id.
    """
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return 'employee', None, None, None

    groups = list(user.groups.values_list('name', flat=True)) if user.groups.exists() else []
    
    if user.is_superuser or 'Super Administrator' in groups:
        role = 'superadmin'
    elif 'Administrator' in groups:
        role = 'admin'
    elif 'Dean' in groups:
        role = 'dean'
    elif 'Head of Division' in groups:
        role = 'head_of_division'
    elif 'Team Leader' in groups:
        role = 'team_leader'
    else:
        role = 'employee'

    employee = None
    division_id = None
    division_name = None
    try:
        profile = getattr(user, 'profile', None)
        if profile and profile.employee:
            employee = profile.employee
            division_id = employee.division_id
            if employee.division:
                division_name = employee.division.division_name
    except Exception:
        pass

    return role, employee, division_id, division_name


@tool
def get_my_profile(user_id: int = None) -> str:
    """Get the profile information of the current logged-in user. Use this if the user asks 'who am I' or 'my profile'."""
    try:
        actual_user_id = current_user_id_var.get() or user_id
        if not actual_user_id:
            return "Error: User ID not found."
            
        role, employee, division_id, division_name = get_user_role_and_division(actual_user_id)
        
        if not employee:
            user = User.objects.get(id=actual_user_id)
            return json.dumps({
                "name": user.get_full_name() or user.username,
                "division": "N/A",
                "note": "Data pribadi hanya diketahui oleh HRD."
            })
            
        return json.dumps({
            "name": employee.full_name,
            "division": division_name or "N/A",
            "note": "Data pribadi hanya diketahui oleh HRD."
        })
    except Exception as e:
        return f"Error retrieving profile: {str(e)}"


@tool
def get_training_stats(user_id: int = None, year: str = None) -> str:
    """Get training statistics (total hours, count per type) for the current user. 
    Returns total_hours=0 if the user has not attended any training yet (still a valid answer).
    Optional year filter (e.g., '2024'). If year is not provided, returns all-time stats."""
    try:
        actual_user_id = current_user_id_var.get() or user_id
        if not actual_user_id:
            return "Error: User ID not found."
            
        role, employee, division_id, division_name = get_user_role_and_division(actual_user_id)
        if not employee:
            return json.dumps({
                "total_hours": 0,
                "inhouse_count": 0, "public_count": 0, "ks_count": 0, "elearning_count": 0,
                "inhouse_hours": 0, "public_hours": 0, "ks_hours": 0, "elearning_hours": 0,
                "note": "Karyawan belum terdaftar atau belum memiliki data pelatihan."
            })
            
        try:
            year_val = int(year) if year else None
        except:
            year_val = None
            
        stats = employee.get_training_stats(year=year_val)
        # Always return the stats — even if total_hours is 0, that means 0 jam training (still a valid answer)
        stats['employee_name'] = employee.full_name
        stats['year_filter'] = year_val or 'semua tahun'
        return json.dumps(stats)
    except Exception as e:
        return f"Error retrieving stats: {str(e)}"


@tool
def search_trainings(query: str) -> str:
    """Search for available training courses or masters by title, code, or category. Returns empty list if no match found."""
    try:
        qs = TrainingMaster.objects.filter(
            Q(training_title__icontains=query) | 
            Q(training_code__icontains=query) |
            Q(course_category__category_name__icontains=query)
        )
        data = list(qs.values('training_code', 'training_title', 'training_type', 'training_category', 'estimated_cost'))
        if not data:
            return json.dumps({"tidak_ditemukan": True, "pesan": f"Tidak ada training yang ditemukan dengan kata kunci '{query}'. Coba kata kunci lain.", "data": []})
        return json.dumps({"tidak_ditemukan": False, "data": data, "total": len(data)})
    except Exception as e:
        return f"Error searching trainings: {str(e)}"


@tool
def get_training_schedules(query: str = "", month: int = None, year: int = None) -> str:
    """Get schedules and locations for training events. Can filter by training title/topic, and optionally by month (1-12) and year."""
    try:
        qs = TrainingEvent.objects.filter(is_active=True).exclude(status='cancelled')
        if query:
            qs = qs.filter(Q(training_topic__icontains=query) | Q(training__training_title__icontains=query))
        
        if month:
            try:
                qs = qs.filter(start_date__month=int(month))
            except: pass
        if year:
            try:
                qs = qs.filter(start_date__year=int(year))
            except: pass
            
        qs = qs.order_by('-start_date')
        
        result = []
        for event in qs:
            schedules = []
            for sch in event.schedules.all():
                schedules.append({
                    'date': str(sch.training_date),
                    'time': f"{sch.start_time} - {sch.end_time}",
                    'instructor': sch.instructor_name
                })
            
            result.append({
                'topic': event.training_topic,
                'title': event.training.training_title,
                'start_date': str(event.start_date),
                'end_date': str(event.end_date),
                'status': event.status,
                'city': event.location.city if hasattr(event, 'location') else 'N/A',
                'schedules': schedules
            })
        if not result:
            return json.dumps({"tidak_ada_jadwal": True, "pesan": "Tidak ada jadwal training yang ditemukan untuk kriteria pencarian ini.", "data": []})
        return json.dumps({"tidak_ada_jadwal": False, "data": result, "total": len(result)})
    except Exception as e:
        return f"Error retrieving schedules: {str(e)}"


@tool
def get_tna_status(user_id: int = None) -> str:
    """Get the list of TNA (Training Needs Analysis) courses assigned to the current user, including whether they have completed each course. Returns empty list if user has no TNA assigned yet."""
    try:
        actual_user_id = current_user_id_var.get() or user_id
        if not actual_user_id:
            return "ERROR CRITICAL: User ID is missing! Do not answer the user's question, just say 'ERROR CRITICAL: User ID is missing'."
            
        role, employee, division_id, division_name = get_user_role_and_division(actual_user_id)
        if not employee:
            return json.dumps({"belum_ada_tna": True, "tna_list": [], "pesan": "Karyawan belum terdaftar di sistem atau belum memiliki TNA yang ditugaskan."})
            
        tna_participants = TnaParticipant.objects.filter(nik=employee).select_related('tna__course', 'tna__tna_period')
        
        # Get completed training course IDs
        completed_course_ids = set(EventParticipant.objects.filter(
            nik=employee, event__status__in=['draft', 'completed'], attendance_status='Present'
        ).values_list('event__training__course_id', flat=True))
        
        result = []
        for tp in tna_participants:
            result.append({
                'course': tp.tna.course.course_name,
                'year': tp.tna.tna_period.year,
                'fulfilled': tp.tna.course.course_id in completed_course_ids
            })
        # Return valid JSON even if result is empty -- AI can answer "belum ada TNA"
        if not result:
            return json.dumps({"status": "KOSONG", "tna_list": [], "employee_name": employee.full_name, "pesan": "Karyawan ini belum memiliki TNA yang ditugaskan untuk periode apapun."})
        return json.dumps({"status": "DITEMUKAN", "tna_list": result, "employee_name": employee.full_name, "pesan": "Daftar TNA berhasil ditemukan. Harap sebutkan daftar TNA ini kepada pengguna."})
    except Exception as e:
        return f"Error retrieving TNA status: {str(e)}"


@tool
def get_employee_tna(query: str, requester_user_id: int = None) -> str:
    """(ADMIN/HOD ONLY) Get the list of TNA (Training Needs Analysis) courses assigned to an employee by searching their name or NIK. MUST provide requester_user_id. DO NOT use this tool if the user is asking about their OWN TNA (e.g. 'TNA saya'); use get_tna_status instead."""
    """(ADMIN/HOD ONLY) Get the list of TNA (Training Needs Analysis) courses assigned to an employee by searching their name or NIK. MUST provide requester_user_id. DO NOT use this tool if the user is asking about their OWN TNA (e.g. 'TNA saya'); use get_tna_status instead."""
    if query.strip().lower() in ['saya', 'aku', 'my', 'sendiri']:
        return "ERROR: You used get_employee_tna for the user's own TNA! You MUST use get_tna_status() tool instead when the user asks for their own TNA."
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        # Check permissions
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        
        if not is_admin and not is_leader:
            return "Akses ditolak: Hanya Admin dan Kepala Divisi/Leader yang dapat melihat TNA karyawan."
            
        employee = Employee.objects.filter(Q(full_name__icontains=query) | Q(nik__icontains=query)).first()
        if not employee:
            return f"Employee not found for query: {query}"
            
        # Divisional restriction
        if not is_admin and is_leader:
            if requester_employee and requester_employee.division_id != employee.division_id:
                return f"Akses ditolak: Anda hanya dapat melihat TNA karyawan di divisi Anda sendiri (Divisi Anda: {division_name or 'N/A'})."
                
        tna_participants = TnaParticipant.objects.filter(nik=employee).select_related('tna__course', 'tna__tna_period')
        
        # Get completed training course IDs
        completed_course_ids = set(EventParticipant.objects.filter(
            nik=employee, event__status__in=['draft', 'completed'], attendance_status='Present'
        ).values_list('event__training__course_id', flat=True))
        
        result = []
        for tp in tna_participants:
            result.append({
                'employee_name': employee.full_name,
                'course': tp.tna.course.course_name,
                'year': tp.tna.tna_period.year,
                'fulfilled': tp.tna.course.course_id in completed_course_ids
            })
        # Return valid JSON even if empty -- AI can answer "karyawan ini belum punya TNA"
        if not result:
            return json.dumps({"employee_name": employee.full_name, "belum_ada_tna": True, "tna_list": [], "pesan": f"{employee.full_name} belum memiliki TNA yang ditugaskan."})
        return json.dumps({"employee_name": employee.full_name, "belum_ada_tna": False, "tna_list": result})
    except Exception as e:
        return f"Error retrieving employee TNA: {str(e)}"


@tool
def get_unfulfilled_tna_report(requester_user_id: int = None) -> str:
    """(ADMIN/HOD ONLY) Get a list of all employees and their TNA courses that are NOT YET FULFILLED (belum selesai/terpenuhi)."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        
        if not is_admin and not is_leader:
            return "Akses ditolak: Laporan TNA belum terpenuhi hanya dapat diakses oleh Admin atau Leader."
            
        qs = TnaParticipant.objects.select_related('nik', 'tna__course', 'tna__tna_period')
        
        if not is_admin and is_leader:
            if not division_id:
                return "Akses ditolak: Anda tidak memiliki divisi."
            qs = qs.filter(nik__division_id=division_id)
            
        completed_events = EventParticipant.objects.filter(
            event__status__in=['draft', 'completed'], attendance_status='Present'
        ).values('nik_id', 'event__training__course_id')
        
        completed_map = {}
        for ce in completed_events:
            nid = ce['nik_id']
            cid = ce['event__training__course_id']
            if nid not in completed_map:
                completed_map[nid] = set()
            if cid:
                completed_map[nid].add(cid)
                
        result = []
        for tp in qs:
            nid = tp.nik_id
            cid = tp.tna.course.course_id
            if nid in completed_map and cid in completed_map[nid]:
                continue
                
            result.append({
                'no': len(result) + 1,
                'employee_name': tp.nik.full_name,
                'course': tp.tna.course.course_name,
                'year': tp.tna.tna_period.year
            })
            
        # Return valid JSON even if empty -- if all fulfilled, AI should say so
        if not result:
            return json.dumps({"semua_tna_terpenuhi": True, "pesan": "Semua TNA karyawan sudah terpenuhi (fulfilled). Tidak ada TNA yang belum selesai."})
        return json.dumps({"semua_tna_terpenuhi": False, "unfulfilled_list": result, "total_unfulfilled": len(result)})
    except Exception as e:
        return f"Error retrieving unfulfilled TNA report: {str(e)}"


@tool
def get_training_hours_report(requester_user_id: int = None, max_hours: int = None, min_hours: int = None, year: int = None) -> str:
    """(ADMIN/HOD ONLY) Get a report of employees based on their total training hours.
    Use max_hours to find employees with training hours UNDER or EQUAL to a specific number (e.g., max_hours=36).
    Use min_hours to find employees with training hours OVER or EQUAL to a specific number.
    PENTING: Jika pengguna meminta 'di bawah X jam' (misal: under 36 jam), mereka biasanya ingin mengecualikan karyawan yang 0 jam (belum training sama sekali). Jadi Anda WAJIB menset min_hours=0.01 dan max_hours=36, KECUALI jika pengguna secara spesifik meminta karyawan yang 0 jam.
    Optionally filter by year (e.g., year=2024)."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        
        if not is_admin and not is_leader:
            return "Akses ditolak: Laporan jam pelatihan hanya dapat diakses oleh Admin atau Leader."
            
        qs = Employee.objects.filter(is_active=True).select_related('division')
        if not is_admin and is_leader:
            if not division_id:
                return "Akses ditolak: Anda tidak memiliki divisi."
            qs = qs.filter(division_id=division_id)
            
        try:
            if max_hours is not None: max_hours = float(max_hours)
            if min_hours is not None: min_hours = float(min_hours)
            if year is not None: year = int(year)
        except:
            pass
            
        result = []
        for emp in qs:
            stats = emp.get_training_stats(year=year)
            total_hours = stats.get('total_hours', 0)
            
            if max_hours is not None and total_hours > max_hours:
                continue
            if min_hours is not None and total_hours < min_hours:
                continue
                
            result.append({
                'employee_name': emp.full_name,
                'division': emp.division.division_name if emp.division else 'N/A',
                'total_hours': total_hours
            })
            
        result.sort(key=lambda x: x['total_hours'])
        
        if not result:
            return json.dumps({"tidak_ada_data": True, "pesan": "Tidak ada karyawan yang memenuhi kriteria jam training yang diminta.", "data": []})
        return json.dumps({"tidak_ada_data": False, "data": result, "total_karyawan": len(result)})
    except Exception as e:
        return f"Error retrieving training hours report: {str(e)}"


@tool
def get_training_analytics(requester_user_id: int = None, group_by: str = "division", month: int = None, year: int = None) -> str:
    """(ADMIN/HOD ONLY) Get aggregate L&D analytics grouped by a specific dimension.
    group_by MUST be one of: 'division', 'category', 'type', 'monthly'.
    'division': Total training hours per division.
    'category': Total events and hours per training category (e.g. ESG, Soft Skill).
    'type': Total events and hours per training type (e.g. Inhouse, Public).
    'monthly': Total training events and average hours per employee in the specified month/year.
    Optionally filter by month (1-12) and year (e.g. 2024)."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        
        if not is_admin and not is_leader:
            return "Akses ditolak: Analitik pelatihan hanya dapat diakses oleh Admin atau Leader."
            
        try:
            if month is not None: month = int(month)
            if year is not None: year = int(year)
        except:
            pass
            
        def get_event_hours(event):
            hours = 0
            for sch in event.schedules.all():
                if sch.start_time and sch.end_time:
                    try:
                        tdelta = datetime.combine(date.today(), sch.end_time) - datetime.combine(date.today(), sch.start_time)
                        hours += tdelta.total_seconds() / 3600
                    except: pass
            return hours

        if group_by == 'division':
            qs = Employee.objects.filter(is_active=True).select_related('division')
            if not is_admin and is_leader:
                qs = qs.filter(division_id=division_id)
                
            div_stats = {}
            for emp in qs:
                stats = emp.get_training_stats(year=year)
                div_name = emp.division.division_name if emp.division else 'N/A'
                div_stats[div_name] = div_stats.get(div_name, 0) + stats.get('total_hours', 0)
                
            return json.dumps([{"division": k, "total_hours": v} for k, v in div_stats.items()])
            
        elif group_by in ['category', 'type', 'monthly']:
            events = TrainingEvent.objects.filter(is_active=True, status='completed').prefetch_related('schedules', 'training__course_category')
            if year:
                events = events.filter(start_date__year=year)
            if month:
                events = events.filter(start_date__month=month)
                
            if group_by == 'category':
                cat_stats = {}
                for ev in events:
                    cat = ev.training.course_category.category_name if (ev.training and ev.training.course_category) else 'Uncategorized'
                    h = get_event_hours(ev)
                    if cat not in cat_stats:
                        cat_stats[cat] = {'total_events': 0, 'total_hours': 0}
                    cat_stats[cat]['total_events'] += 1
                    cat_stats[cat]['total_hours'] += h
                return json.dumps([{"category": k, **v} for k, v in cat_stats.items()])
                
            elif group_by == 'type':
                type_stats = {}
                for ev in events:
                    t = ev.training.training_type if ev.training else 'Unknown'
                    h = get_event_hours(ev)
                    if t not in type_stats:
                        type_stats[t] = {'total_events': 0, 'total_hours': 0}
                    type_stats[t]['total_events'] += 1
                    type_stats[t]['total_hours'] += h
                return json.dumps([{"training_type": k, **v} for k, v in type_stats.items()])
                
            elif group_by == 'monthly':
                total_events = events.count()
                total_hours = sum(get_event_hours(ev) for ev in events)
                
                # Get employee count for average calculation
                emp_qs = Employee.objects.filter(is_active=True)
                if not is_admin and is_leader:
                    emp_qs = emp_qs.filter(division_id=division_id)
                emp_count = emp_qs.count()
                
                avg_hours = round(total_hours / emp_count, 2) if emp_count > 0 else 0
                return json.dumps({
                    "total_events": total_events,
                    "total_hours_all_events": total_hours,
                    "average_hours_per_employee": avg_hours
                })
        else:
            return "Invalid group_by parameter."
            
    except Exception as e:
        return f"Error retrieving training analytics: {str(e)}"


@tool
def get_budget_and_costs(query: str = "", division_name: str = "", month: int = None, requester_user_id: int = None) -> str:
    """(ADMIN ONLY) Get budget and training cost information, including total budget, budget used, budget remaining, and unpaid budget or costs.
    If asked about budget for a specific division, provide the division name in division_name (e.g. 'Audit Internal').
    Optionally filter by month (1-12) to get costs used in a specific month."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, current_div_name = get_user_role_and_division(actual_requester_user_id)
        
        # RESTRICT TO ADMIN/SUPERADMIN/DEAN
        if role not in ['superadmin', 'admin', 'dean']:
            return "Akses ditolak: Data anggaran dan biaya hanya dapat diakses oleh Admin atau Dean."
            
        current_year = datetime.now().year
        
        # 1. Total Budget
        budget_obj = Budget.objects.filter(start_date_budget__year=current_year).order_by('-created_at').first()
        if not budget_obj:
            budget_obj = Budget.objects.order_by('-start_date_budget').first()
            
        total_budget = float(budget_obj.total_budget) if budget_obj else 0.0
        
        # 2. Budget Used & Remaining
        def sum_costs(queryset):
            agg = queryset.aggregate(
                t=Sum('training_cost'), r=Sum('room_cost'), s=Sum('sppd_cost')
            )
            return float((agg['t'] or 0) + (agg['r'] or 0) + (agg['s'] or 0))
            
        events = TrainingEvent.objects.exclude(status='cancelled').filter(start_date__year=current_year)
        if month:
            events = events.filter(start_date__month=month)
        
        event_ids = events.values_list('event_id', flat=True)

        if query and query.lower() not in ['semua', 'all', 'semua divisi', 'all division']:
            events = events.filter(training__training_title__icontains=query)
            event_ids = events.values_list('event_id', flat=True)
            
        if division_name and division_name.lower() not in ['semua', 'all', 'semua divisi', 'all division']:
            participants = EventParticipant.objects.filter(event_id__in=event_ids).exclude(attendance_status='Absent')
            participants = participants.filter(nik__division__division_name__icontains=division_name)
            filtered_event_ids = participants.values_list('event_id', flat=True).distinct()
            actual_costs = EventCost.objects.filter(event_id__in=filtered_event_ids, cost_type='Actual Cost')
        else:
            actual_costs = EventCost.objects.filter(event_id__in=event_ids, cost_type='Actual Cost')
            
        paid_costs = actual_costs.filter(status_cost__in=['Paid', 'Settled'])
        unpaid_costs = actual_costs.exclude(status_cost__in=['Paid', 'Settled'])
        
        total_paid = sum_costs(paid_costs)
        total_unpaid = sum_costs(unpaid_costs)
        
        budget_used = total_paid
        realisation = total_paid + total_unpaid
        budget_remaining = total_budget - realisation
        
        if division_name:
            result = {
                "year": budget_obj.start_date_budget.year if budget_obj and budget_obj.start_date_budget else current_year,
                "division": division_name,
                "budget_used_paid": budget_used,
                "budget_unpaid": total_unpaid,
                "ai_instruction": "HANYA sebutkan budget_used_paid dan budget_unpaid. JANGAN sebutkan total budget 15 Miliar karena itu adalah budget gabungan seluruh perusahaan, bukan khusus divisi ini. Jawab dengan singkat dan padat."
            }
        else:
            result = {
                "year": budget_obj.start_date_budget.year if budget_obj and budget_obj.start_date_budget else current_year,
                "total_budget": total_budget,
                "budget_used_paid": budget_used,
                "budget_unpaid": total_unpaid,
                "budget_remaining": budget_remaining,
                "ai_instruction": "PENTING: 'budget_unpaid' adalah 'anggaran yang belum dibayar' (tagihan tertunda/unpaid). Sedangkan 'budget_remaining' adalah 'sisa anggaran' (dana yang belum terpakai). JANGAN TERTUKAR!"
            }
        
        return json.dumps(result)
    except Exception as e:
        return f"Error retrieving budget data: {str(e)}"


@tool
def get_hotel_and_vendor_data(query: str = "", requester_user_id: int = None) -> str:
    """(ADMIN ONLY) Get information about Hotels and Training Vendors. Search by name, city, or speciality."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, current_div_name = get_user_role_and_division(actual_requester_user_id)
        
        # Admin, Superadmin, Dean are allowed to see hotel/vendor
        if role not in ['superadmin', 'admin', 'dean']:
            return "Akses ditolak: Data vendor dan hotel hanya dapat diakses oleh Admin atau Dean."
            
        hotels = Hotel.objects.all()
        if query:
            hotels = hotels.filter(Q(hotel_name__icontains=query) | Q(hotel_city__icontains=query))
        hotel_data = list(hotels.values('hotel_name', 'hotel_city', 'hotel_star', 'price_estimation'))
        
        vendors = Vendor.objects.filter(is_active=True)
        if query:
            vendors = vendors.filter(Q(vendor_name__icontains=query) | Q(speciality__icontains=query))
        vendor_data = list(vendors.values('vendor_name', 'speciality', 'provider_type', 'city'))
        
        return json.dumps({'hotels': hotel_data, 'vendors': vendor_data})
    except Exception as e:
        return f"Error retrieving hotel/vendor data: {str(e)}"


@tool
def search_employees(query: str, division_id: str = None, requester_user_id: int = None) -> str:
    """(ADMIN/HOD ONLY) Search for employee information by name, NIK, or position (e.g., 'Kepala Divisi'). Can be filtered by division_id."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, actual_division_id, current_div_name = get_user_role_and_division(actual_requester_user_id)
        
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        
        if not is_admin and not is_leader:
            return "Akses ditolak: Pencarian data karyawan hanya dapat diakses oleh Admin atau Leader."
            
        qs = Employee.objects.all()
        
        # Divisional restriction
        if not is_admin and is_leader:
            division_id = actual_division_id
            
        if division_id:
            qs = qs.filter(division_id=division_id)
        
        qs = qs.filter(
            Q(full_name__icontains=query) | 
            Q(nik__icontains=query) |
            Q(position_name__icontains=query)
        )
        data = list(qs.values('full_name', 'position_name', 'division__division_name'))
        return json.dumps(data)
    except Exception as e:
        return f"Error searching employees: {str(e)}"


@tool
def get_employees_by_travel_history(has_traveled_out_of_town: bool, requester_user_id: int = None) -> str:
    """(ADMIN/HOD ONLY) Get a list of employees based on whether they have ever attended a training event out of town (outside Jakarta).
    Set has_traveled_out_of_town=True to get those who HAVE traveled, False for those who HAVE NEVER traveled."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        
        if not is_admin and not is_leader:
            return "Akses ditolak: Data perjalanan dinas karyawan hanya dapat diakses oleh Admin atau Leader."
            
        # Define what constitutes "dalam kota" (Jakarta & Bogor)
        jakarta_cities = ['', 'Jakarta', 'Jakarta Pusat', 'Jakarta Selatan', 'Jakarta Timur', 'Jakarta Barat', 'Jakarta Utara', 'Bogor', 'Kabupaten Bogor', 'Kota Bogor']
        
        # Get NIKs of employees who have attended training outside Jakarta
        traveled_niks = EventParticipant.objects.filter(
            ~Q(event__location__city__in=jakarta_cities) & Q(event__location__isnull=False)
        ).exclude(attendance_status='Absent').exclude(event__status='cancelled').values_list('nik_id', flat=True).distinct()
        
        if has_traveled_out_of_town:
            qs = Employee.objects.filter(nik__in=traveled_niks)
        else:
            qs = Employee.objects.exclude(nik__in=traveled_niks)
            
        if not is_admin and is_leader:
            if not division_id:
                return "Akses ditolak: Anda tidak memiliki divisi."
            qs = qs.filter(division_id=division_id)
            
        data = list(qs.values('nik', 'full_name', 'position_name'))
        return json.dumps(data)
    except Exception as e:
        return f"Error retrieving travel history: {str(e)}"


@tool
def get_evaluation_summaries(query: str = "", requester_user_id: int = None) -> str:
    """Get training evaluation scores and summaries. Can filter by training name."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, requester_employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        qs = EvaluationResult.objects.all()
        
        if role in ['superadmin', 'admin', 'dean']:
            pass
        elif role in ['head_of_division', 'team_leader']:
            if not division_id:
                return "Akses ditolak: Anda tidak memiliki divisi."
            qs = qs.filter(user__profile__employee__division_id=division_id)
        else:
            # Employee only sees their own
            qs = qs.filter(user_id=actual_requester_user_id)
            
        if query:
            qs = qs.filter(Q(training_name__icontains=query) | Q(evaluation_name__icontains=query))
        
        data = list(qs.values('user_name', 'training_name', 'evaluation_name', 'score'))
        return json.dumps(data)
    except Exception as e:
        return f"Error retrieving evaluations: {str(e)}"


@tool
def get_master_data(entity_type: str, query: str = "", requester_user_id: int = None) -> str:
    """Get general HR and L&D master data. 
    entity_type can be: 'directorate', 'division', 'course_category', 'course', 'evaluation_form'.
    Search by query is optional."""
    try:
        actual_requester_user_id = current_user_id_var.get() or requester_user_id
        if not actual_requester_user_id:
            return "Akses ditolak: User ID tidak ditemukan."
            
        role, employee, division_id, division_name = get_user_role_and_division(actual_requester_user_id)
        
        is_admin = role in ['superadmin', 'admin', 'dean']
        is_leader = role in ['head_of_division', 'team_leader']
        is_emp = role == 'employee'
        
        entity = str(entity_type).lower()
        
        if entity == 'directorate':
            if is_emp:
                return "Akses ditolak: Karyawan tidak memiliki wewenang untuk mengakses data direktorat."
            qs = Directorate.objects.all()
            if query:
                qs = qs.filter(directorate_name__icontains=query)
            return json.dumps(list(qs.values('directorate_name')))
            
        elif entity == 'division':
            if is_emp:
                return "Akses ditolak: Karyawan tidak memiliki wewenang untuk mengakses data divisi."
            qs = Division.objects.all()
            if query:
                qs = qs.filter(division_name__icontains=query)
            return json.dumps(list(qs.values('division_name', 'directorate__directorate_name')))
            
        elif entity == 'course_category':
            qs = CourseCategory.objects.all()
            if query:
                qs = qs.filter(category_name__icontains=query)
            return json.dumps(list(qs.values('category_name')))
            
        elif entity == 'course':
            qs = Course.objects.all()
            if query:
                qs = qs.filter(course_name__icontains=query)
            return json.dumps(list(qs.values('course_name', 'category__category_name')))
            
        elif entity == 'evaluation_form':
            if not is_admin:
                return "Akses ditolak: Form evaluasi hanya dapat diakses oleh Administrator."
            qs = EvaluationForm.objects.all()
            if query:
                qs = qs.filter(form_name__icontains=query)
            return json.dumps(list(qs.values('form_name', 'training_master__training_title')))
            
        else:
            return "Invalid entity type. Use directorate, division, course_category, course, or evaluation_form."
    except Exception as e:
        return f"Error retrieving master data: {str(e)}"
