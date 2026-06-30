from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import (
    Employee, CourseCategory, Course,
    Vendor, TnaPeriod, TnaMaster, TnaParticipant, Hotel,
    TrainingMaster, TrainingEvent, EventLocation, EventSchedule,
    EventParticipant, EventCost, EventDocument, Division,
    EvaluationForm, EvaluationQuestion, EvaluationQuestionOption,
    EvaluationAnswer, EvaluationResult,
    AiAdminConfig, AiChatSession, AiChatLog, AiUnauthorizedAttempt,
    Budget
)

def get_highest_role(user):
    if not user:
        return "Employee"
    groups = list(user.groups.values_list('name', flat=True)) if user.groups.exists() else []
    if user.is_superuser or 'Super Administrator' in groups:
        return "Super Administrator"
    elif 'Administrator' in groups:
        return "Administrator"
    elif 'Dean' in groups:
        return "Dean"
    elif 'Head of Division' in groups:
        return "Head of Division"
    elif 'Team Leader' in groups:
        return "Team Leader"
    return "Employee"

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'



class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = '__all__'



# Jwt Token Serializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        
        user = self.user
        
        # Logic role
        user_role = get_highest_role(user)
            
        data['user'] = {
            'email': user.email,
            'full_name': user.profile.employee.full_name if hasattr(user, 'profile') else "-",
            'role': user_role,
            'nik': user.profile.employee.nik if hasattr(user, 'profile') else "-"
        }
        
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['email'] = user.email

        user_role = get_highest_role(user)

        token['role'] = user_role

        if hasattr(user, 'profile'):
            token['nik'] = user.profile.employee.nik
            token['full_name'] = user.profile.employee.full_name

        return token





# Super admin serializer
class UserSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'role']
        read_only_fields = ['id']

    def get_role(self, obj):
        return get_highest_role(obj)



class EmployeeSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    division_name = serializers.CharField(source='division.division_name', read_only=True)
    
    attendance = serializers.SerializerMethodField()
    inhouse_training = serializers.SerializerMethodField()
    public_training = serializers.SerializerMethodField()
    knowledge_sharing = serializers.SerializerMethodField()
    elearning = serializers.SerializerMethodField()
    iht_plus_public = serializers.SerializerMethodField()
    
    total_hours = serializers.SerializerMethodField()
    inhouse_hours = serializers.SerializerMethodField()
    public_hours = serializers.SerializerMethodField()
    ks_hours = serializers.SerializerMethodField()
    elearning_hours = serializers.SerializerMethodField()
    
    tna_count = serializers.SerializerMethodField()
    tna_fulfilled = serializers.SerializerMethodField()

    attendance_details = serializers.SerializerMethodField()
    tna_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'nik', 'full_name', 'division', 'division_name', 
            'level', 'position_name', 'special_position', 'role', 'is_active',
            'attendance', 'inhouse_training', 'public_training', 'knowledge_sharing', 'elearning', 'iht_plus_public',
            'total_hours', 'inhouse_hours', 'public_hours', 'ks_hours', 'elearning_hours',
            'tna_count', 'tna_fulfilled', 'attendance_details', 'tna_details'
        ]

    def get_role(self, obj):
        try:
            user = obj.profile_set.first().user
            return get_highest_role(user)
        except Exception:
            pass
        return "Employee"

    def _get_filtered_events(self, obj):
        if hasattr(obj, '_filtered_events_cache'):
            return obj._filtered_events_cache
            
        year = self.context.get('year')
        start_date = self.context.get('start_date')
        end_date = self.context.get('end_date')
        status_filter = self.context.get('status')
        category_filter = self.context.get('category')
        type_filter = self.context.get('type')

        events = obj.get_completed_events(year)
        events = [ep for ep in events if ep.event.status.lower() == 'completed']
        
        if start_date:
            events = [ep for ep in events if ep.event.start_date and ep.event.start_date.isoformat() >= start_date]
        if end_date:
            events = [ep for ep in events if ep.event.end_date and ep.event.end_date.isoformat() <= end_date]
        if status_filter and status_filter != 'all':
            events = [ep for ep in events if ep.event.status.lower() == status_filter.lower()]
        if category_filter and category_filter != 'all':
            events = [ep for ep in events if ep.event.training.training_category == category_filter]
        if type_filter and type_filter != 'all':
            events = [ep for ep in events if ep.event.training.training_type == type_filter]
            
        obj._filtered_events_cache = events
        return events

    def _get_filtered_stats(self, obj):
        if hasattr(obj, '_filtered_stats_cache'):
            return obj._filtered_stats_cache
            
        stats = {
            'inhouse_count': 0, 'public_count': 0, 'ks_count': 0, 'elearning_count': 0,
            'inhouse_hours': 0, 'public_hours': 0, 'ks_hours': 0, 'elearning_hours': 0,
            'total_hours': 0
        }
        
        events = self._get_filtered_events(obj)
        from datetime import datetime, date
        for ep in events:
            tt = (ep.event.training.training_type or '').strip()
            
            event_hours = 0
            for sch in ep.event.schedules.all():
                if sch.start_time and sch.end_time:
                    dummy_date = date(2000, 1, 1)
                    t1 = datetime.combine(dummy_date, sch.start_time)
                    t2 = datetime.combine(dummy_date, sch.end_time)
                    event_hours += (t2 - t1).total_seconds() / 3600
            
            if tt == 'Inhouse Training':
                stats['inhouse_count'] += 1
                stats['inhouse_hours'] += event_hours
            elif tt == 'Public Training':
                stats['public_count'] += 1
                stats['public_hours'] += event_hours
            elif tt == 'Knowledge Sharing':
                stats['ks_count'] += 1
                stats['ks_hours'] += event_hours
            elif tt == 'E-Learning':
                stats['elearning_count'] += 1
                stats['elearning_hours'] += event_hours
            
            stats['total_hours'] += event_hours
            
        obj._filtered_stats_cache = stats
        return stats

    def get_attendance_details(self, obj):
        year = self.context.get('year')
        events = self._get_filtered_events(obj)
        events = [ep for ep in events if ep.event.status.lower() == 'completed']
        
        # Pre-fetch TNA course IDs for this employee
        tna_qs = obj.tnaparticipant_set.all()
        if year:
            try:
                y = int(year)
                tna_qs = tna_qs.filter(tna__tna_period__year=y)
            except (ValueError, TypeError):
                pass
        tna_course_ids = set(tp.tna.course_id for tp in tna_qs if tp.tna.course_id)

        details = []
        from datetime import datetime, date
        for ep in events:
            event = ep.event
            training = event.training
            
            # Hours calculation
            event_hours = 0
            for sch in event.schedules.all():
                if sch.start_time and sch.end_time:
                    dummy_date = date(2000, 1, 1)
                    t1 = datetime.combine(dummy_date, sch.start_time)
                    t2 = datetime.combine(dummy_date, sch.end_time)
                    event_hours += (t2 - t1).total_seconds() / 3600
            
            details.append({
                'title': training.training_title,
                'category': training.training_category or '',
                'hours': round(event_hours, 2),
                'tna': training.course.course_name if training.course_id in tna_course_ids else '-',
                'type': training.training_type or ''
            })
        return details

    def get_attendance(self, obj):
        return len(self._get_filtered_events(obj))

    def get_inhouse_training(self, obj):
        return self._get_filtered_stats(obj)['inhouse_count']

    def get_public_training(self, obj):
        return self._get_filtered_stats(obj)['public_count']

    def get_knowledge_sharing(self, obj):
        return self._get_filtered_stats(obj)['ks_count']

    def get_elearning(self, obj):
        return self._get_filtered_stats(obj)['elearning_count']

    def get_iht_plus_public(self, obj):
        stats = self._get_filtered_stats(obj)
        return stats['inhouse_count'] + stats['public_count']

    def get_total_hours(self, obj):
        return round(self._get_filtered_stats(obj)['total_hours'], 2)

    def get_inhouse_hours(self, obj):
        return round(self._get_filtered_stats(obj)['inhouse_hours'], 2)

    def get_public_hours(self, obj):
        return round(self._get_filtered_stats(obj)['public_hours'], 2)

    def get_ks_hours(self, obj):
        return round(self._get_filtered_stats(obj)['ks_hours'], 2)

    def get_elearning_hours(self, obj):
        return round(self._get_filtered_stats(obj)['elearning_hours'], 2)

    def get_tna_count(self, obj):
        year = self.context.get('year')
        tna_qs = obj.tnaparticipant_set.all()
        if year:
            try:
                y = int(year)
                tna_qs = tna_qs.filter(tna__tna_period__year=y)
            except (ValueError, TypeError):
                pass
        return tna_qs.count()

    def get_tna_fulfilled(self, obj):
        year = self.context.get('year')
        tna_qs = obj.tnaparticipant_set.all()
        if year:
            try:
                y = int(year)
                tna_qs = tna_qs.filter(tna__tna_period__year=y)
            except (ValueError, TypeError):
                pass
        
        tna_list = list(tna_qs)
        if not tna_list:
            return 0
            
        events = self._get_filtered_events(obj)
        attended_course_ids = set(ep.event.training.course_id for ep in events)
        fulfilled_count = 0
        for tp in tna_list:
            if tp.tna.course_id in attended_course_ids:
                fulfilled_count += 1
        return fulfilled_count

    def get_tna_details(self, obj):
        year = self.context.get('year')
        tna_qs = obj.tnaparticipant_set.all()
        if year:
            try:
                y = int(year)
                tna_qs = tna_qs.filter(tna__tna_period__year=y)
            except (ValueError, TypeError):
                pass
        
        events = self._get_filtered_events(obj)
        attended_course_ids = set(ep.event.training.course_id for ep in events if ep.event.training.course_id)
        
        details = []
        for tp in tna_qs:
            course_name = tp.tna.course.course_name if tp.tna.course else "-"
            fulfilled = 1 if tp.tna.course_id in attended_course_ids else 0
            details.append({
                'course_name': course_name,
                'fulfilled': fulfilled
            })
        return details


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    tna_count = serializers.SerializerMethodField()
    division_name = serializers.CharField(source='division.division_name', read_only=True)

    class Meta:
        model = Employee
        fields = ['nik', 'full_name', 'role', 'position_name', 'tna_count', 'division_name']

    def get_role(self, obj):
        try:
            user = obj.profile_set.first().user
            return get_highest_role(user)
        except Exception:
            pass
        return "Employee"

    def get_tna_count(self, obj):
        return obj.tnaparticipant_set.count()


class CourseCategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()

    class Meta:
        model = CourseCategory
        fields = [
            'course_category_id',
            'category_name',
            'description',
            'is_active',
            'created_at',
            'course_count',
        ]
        read_only_fields = ['created_at']

    def get_course_count(self, obj):
        return obj.course_set.count()

    def validate_course_category_id(self, value):
        if self.instance is None:  # Only for creation
            if CourseCategory.objects.filter(course_category_id=value).exists():
                raise serializers.ValidationError("Course Category Code already exists.")
        return value


class CourseSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(
        source='course_category.category_name', read_only=True
    )

    class Meta:
        model = Course
        fields = [
            'course_id',
            'course_category',
            'category_name',
            'course_name',
            'description',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['created_at']

    def validate_course_id(self, value):
        if self.instance is None:  # Only for creation
            if Course.objects.filter(course_id=value).exists():
                raise serializers.ValidationError("Course Code already exists.")
        return value


class VendorSerializer(serializers.ModelSerializer):
    trainings = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['created_at']

    def get_trainings(self, obj):
        trainings = obj.trainingmaster_set.select_related('course', 'course_category').all()
        return [
            {
                'category_name': t.course_category.category_name if t.course_category else '',
                'course_name': t.course.course_name if t.course else '',
                'training_title': t.training_title or ''
            }
            for t in trainings
        ]

    def validate_vendor_id(self, value):
        if self.instance is None:  # Only for creation
            if Vendor.objects.filter(vendor_id=value).exists():
                raise serializers.ValidationError("Vendor Code already exists.")
        return value


class TnaPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TnaPeriod
        fields = '__all__'
        read_only_fields = ['created_at']


class TnaMasterSerializer(serializers.ModelSerializer):
    tna_period_name = serializers.CharField(source='tna_period.period_name', read_only=True)
    category_name = serializers.CharField(source='course_category.category_name', read_only=True)
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    creator_name = serializers.CharField(source='created_by.full_name', read_only=True)

    class Meta:
        model = TnaMaster
        fields = [
            'tna_id', 'tna_period', 'tna_period_name',
            'course_category', 'category_name',
            'course', 'course_name',
            'group_name', 'created_by', 'creator_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class TnaParticipantSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='nik.full_name', read_only=True)
    division_name = serializers.CharField(source='nik.division.division_name', read_only=True)
    position_name = serializers.CharField(source='nik.position_name', read_only=True)
    course_name = serializers.CharField(source='tna.course.course_name', read_only=True)
    category_name = serializers.CharField(source='tna.course_category.category_name', read_only=True)
    
    iht_plus_public = serializers.SerializerMethodField()
    tna_fulfilled = serializers.SerializerMethodField()
    fulfillment_trainings = serializers.SerializerMethodField()

    class Meta:
        model = TnaParticipant
        fields = [
            'tna_participant_id', 'tna', 'category_name', 'course_name', 
            'nik', 'employee_name', 'division_name', 'position_name',
            'iht_plus_public', 'tna_fulfilled', 'fulfillment_trainings'
        ]

    def get_iht_plus_public(self, obj):
        # Return count of IHT + Public for the specific year of the TNA period
        year = obj.tna.tna_period.year
        return obj.nik.get_iht_plus_public(year)

    def get_tna_fulfilled(self, obj):
        # Binary fulfillment for the specific course and year
        year = obj.tna.tna_period.year
        events = obj.nik.get_completed_events(year)
        attended_course_ids = [ep.event.training.course_id for ep in events]
        return 1 if obj.tna.course_id in attended_course_ids else 0

    def get_fulfillment_trainings(self, obj):
        year = obj.tna.tna_period.year
        events = obj.nik.get_completed_events(year)
        matching_events = [
            ep for ep in events 
            if ep.event.training.course_id == obj.tna.course_id
        ]
        titles = [ep.event.training.training_title for ep in matching_events if ep.event.training.training_title]
        unique_titles = []
        for title in titles:
            if title not in unique_titles:
                unique_titles.append(title)
        return ", ".join(unique_titles)



class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'
        read_only_fields = ['created_at']

    def validate_hotel_id(self, value):
        if self.instance is None:  # Only for creation
            if Hotel.objects.filter(hotel_id=value).exists():
                raise serializers.ValidationError("Hotel ID already exists.")
        return value


class TrainingMasterSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.course_name', read_only=True)
    category_name = serializers.CharField(source='course_category.category_name', read_only=True)
    pic_name = serializers.CharField(source='pic.full_name', read_only=True)
    pic_nik = serializers.CharField(source='pic.nik', read_only=True)
    pic_division = serializers.CharField(source='pic.division.division_name', read_only=True)
    pic_position = serializers.CharField(source='pic.position_name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.vendor_name', read_only=True)

    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    days = serializers.SerializerMethodField()
    hours = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    l1_avg = serializers.SerializerMethodField()
    l2_avg = serializers.SerializerMethodField()
    tna_fulfillment = serializers.SerializerMethodField()
    
    training_cost = serializers.SerializerMethodField()
    venue_cost = serializers.SerializerMethodField()
    sppd_cost = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()

    latest_event = serializers.SerializerMethodField()
    division_participant_names = serializers.SerializerMethodField()

    class Meta:
        model = TrainingMaster
        fields = [
            'training_id', 'training_code', 'course', 'course_category', 
            'training_type', 'training_category', 'training_title', 
            'training_description', 'pic', 'vendor', 'estimated_cost',
            'is_active', 'created_at', 'updated_at',
            'course_name', 'category_name', 'pic_name', 'pic_nik', 
            'pic_division', 'pic_position', 'vendor_name',
            'start_date', 'end_date', 'days', 'hours', 'location', 
            'l1_avg', 'l2_avg', 'tna_fulfillment',
            'training_cost', 'venue_cost', 'sppd_cost', 'total_cost',
            'latest_event', 'division_participant_names'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate_training_code(self, value):
        if self.instance is None:  # Only for creation
            if TrainingMaster.objects.filter(training_code=value).exists():
                raise serializers.ValidationError("Training Code already exists.")
        return value

    def get_latest_event_model(self, obj):
        if not hasattr(self, '_latest_event_cache'):
            self._latest_event_cache = {}
        if obj.training_id not in self._latest_event_cache:
            request = self.context.get('request')
            view_mode = request.query_params.get('view_mode', 'admin') if request and hasattr(request, 'query_params') else 'admin'
            
            # Check if purely an Employee role
            is_employee_user = False
            if request and request.user.is_authenticated:
                user_groups = list(request.user.groups.values_list('name', flat=True))
                if "Employee" in user_groups and not any(r in user_groups for r in ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader']):
                    is_employee_user = True
            
            if view_mode == 'employee' or is_employee_user:
                event = None
                if request and request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.employee:
                    emp = request.user.profile.employee
                    event = obj.trainingevent_set.filter(
                        participants__nik=emp,
                        participants__attendance_status='Present',
                        status='completed'
                    ).order_by('-start_date').first()
                if not event:
                    event = obj.trainingevent_set.filter(status='completed').order_by('-start_date').first()
                self._latest_event_cache[obj.training_id] = event
            else:
                self._latest_event_cache[obj.training_id] = obj.trainingevent_set.order_by('-start_date').first()
        return self._latest_event_cache[obj.training_id]

    def get_latest_event(self, obj):
        event = self.get_latest_event_model(obj)
        if not event:
            return None
        
        # full details for the edit form
        return {
            'event_id': event.event_id,
            'topic': event.training_topic,
            'start_date': event.start_date,
            'end_date': event.end_date,
            'status': event.status,
            'enable_course_access': event.enable_course_access,
            'enable_feedback': event.enable_feedback,
            'enable_evaluations': event.enable_evaluations,
            'location': {
                'city': event.location.city if hasattr(event, 'location') else "",
                'venue': event.location.venue if hasattr(event, 'location') else "",
                'room': event.location.room if hasattr(event, 'location') else "",
                'address': event.location.address if hasattr(event, 'location') else "",
            },
            'schedules': EventScheduleSerializer(event.schedules.all(), many=True).data,
            'participants': EventParticipantSerializer(event.participants.all(), many=True).data,
            'costs': EventCostSerializer(event.costs.all(), many=True).data,
            'documents': EventDocumentSerializer(event.documents.all(), many=True).data,
        }

    def get_start_date(self, obj):
        event = self.get_latest_event_model(obj)
        if isinstance(event, dict): 
            return event.get('start_date')
        return event.start_date if event else None

    def get_end_date(self, obj):
        event = self.get_latest_event_model(obj)
        if isinstance(event, dict):
            return event.get('end_date')
        return event.end_date if event else None

    def get_days(self, obj):
        event = self.get_latest_event_model(obj)
        if event and event.start_date and event.end_date:
            return (event.end_date - event.start_date).days + 1
        return 0

    def get_hours(self, obj):
        from django.db.models import F, ExpressionWrapper, DurationField
        from datetime import datetime, date, timedelta
        event = self.get_latest_event_model(obj)
        if not event: return 0
        total_seconds = 0
        for sch in event.schedules.all():
            if sch.start_time and sch.end_time:
                dummy_date = date(2000, 1, 1)
                t1 = datetime.combine(dummy_date, sch.start_time)
                t2 = datetime.combine(dummy_date, sch.end_time)
                total_seconds += (t2 - t1).total_seconds()
        return round(total_seconds / 3600, 2)

    def get_location(self, obj):
        event = self.get_latest_event_model(obj)
        if event and hasattr(event, 'location'):
            return event.location.city
        return "-"

    def get_l1_avg(self, obj):
        from django.db.models import Avg
        result = EventParticipant.objects.filter(event__training=obj).aggregate(Avg('l1_score'))['l1_score__avg']
        return round(result, 2) if result else 0

    def get_l2_avg(self, obj):
        participants = EventParticipant.objects.filter(event__training=obj)
        if not participants.exists():
            return 0
        
        total_converted = 0
        count = 0
        for p in participants:
            if p.l2_score is not None:
                try:
                    s = float(p.l2_score)
                    if s > 4: # Convert old 0-100 scale
                        if s <= 25: s = 1
                        elif s <= 50: s = 2
                        elif s <= 75: s = 3
                        else: s = 4
                    total_converted += s
                    count += 1
                except (ValueError, TypeError):
                    continue
        
        return round(total_converted / count, 2) if count > 0 else 0

    def get_tna_fulfillment(self, obj):
        from .models import TnaMaster
        return TnaMaster.objects.filter(course=obj.course).exists()

    def get_training_cost(self, obj):
        from django.db.models import Sum
        event = self.get_latest_event_model(obj)
        if event:
            return event.costs.aggregate(Sum('training_cost'))['training_cost__sum'] or 0
        return 0

    def get_venue_cost(self, obj):
        from django.db.models import Sum
        event = self.get_latest_event_model(obj)
        if event:
            return event.costs.aggregate(Sum('room_cost'))['room_cost__sum'] or 0
        return 0

    def get_sppd_cost(self, obj):
        from django.db.models import Sum
        event = self.get_latest_event_model(obj)
        if event:
            return event.costs.aggregate(Sum('sppd_cost'))['sppd_cost__sum'] or 0
        return 0

    def get_total_cost(self, obj):
        from django.db.models import Sum, F
        event = self.get_latest_event_model(obj)
        if event:
            totals = event.costs.aggregate(
                total=Sum(F('training_cost') + F('room_cost') + F('sppd_cost'))
            )
            return totals['total'] or 0
        return 0

    def get_division_participant_names(self, obj):
        from .models import EventParticipant
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return ""
        
        user = request.user
        user_groups = list(user.groups.values_list('name', flat=True))
        view_mode = request.query_params.get('view_mode', 'admin') if request and hasattr(request, 'query_params') else 'admin'
        
        # Check if purely an Employee role
        is_employee_user = "Employee" in user_groups and not any(r in user_groups for r in ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader'])

        if hasattr(user, 'profile') and user.profile.employee:
            emp = user.profile.employee
            if view_mode == 'employee' or is_employee_user:
                # Check if employee actually attended training and it is completed/Present
                if EventParticipant.objects.filter(event__training=obj, nik=emp, attendance_status='Present', event__status='completed').exists():
                    return emp.full_name
            else:
                if "Head of Division" in user_groups or "Team Leader" in user_groups:
                    div_id = emp.division_id
                    participants = EventParticipant.objects.filter(
                        event__training=obj,
                        nik__division_id=div_id
                    ).select_related('nik').order_by('nik__full_name')
                    
                    names = [p.nik.full_name for p in participants]
                    return ", ".join(sorted(list(set(names))))
                elif "Employee" in user_groups or "Administrator" in user_groups or "Super Administrator" in user_groups or "Dean" in user_groups or user.is_superuser:
                    # Check if employee actually attended training
                    if EventParticipant.objects.filter(event__training=obj, nik=emp).exists():
                        return emp.full_name
        return ""


class TrainingEventSerializer(serializers.ModelSerializer):
    training_code = serializers.CharField(source='training.training_code', read_only=True)
    training_title = serializers.CharField(source='training.training_title', read_only=True)

    class Meta:
        model = TrainingEvent
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class EventLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLocation
        fields = '__all__'
        read_only_fields = ['created_at']


class EventScheduleSerializer(serializers.ModelSerializer):
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = EventSchedule
        fields = '__all__'
        read_only_fields = ['created_at']


class EventParticipantSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='nik.full_name', read_only=True)

    class Meta:
        model = EventParticipant
        fields = '__all__'
        read_only_fields = ['created_at']

    def validate(self, data):
        event = data.get('event')
        nik = data.get('nik')
        
        if not event or not nik:
            return data

        # Get the dates of the current event
        new_start = event.start_date
        new_end = event.end_date
        
        # Check for overlapping events for this employee
        # We use Q objects to check for overlap: (StartA <= EndB) and (EndA >= StartB)
        conflicts = EventParticipant.objects.filter(
            nik=nik,
            event__start_date__lte=new_end,
            event__end_date__gte=new_start
        )
        
        if self.instance:
            conflicts = conflicts.exclude(pk=self.instance.pk)
            
        if conflicts.exists():
            conflict_event = conflicts.first().event
            raise serializers.ValidationError(
                f"Employee already registered for other training: {conflict_event.training_topic} ({conflict_event.start_date} to {conflict_event.end_date})"
            )
        
        return data


class EventCostSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCost
        fields = '__all__'
        read_only_fields = ['created_at']


class EventDocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.full_name', read_only=True)

    class Meta:
        model = EventDocument
        fields = '__all__'
        read_only_fields = ['uploaded_at']


class EvaluationQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationQuestionOption
        fields = '__all__'

class EvaluationQuestionSerializer(serializers.ModelSerializer):
    options = EvaluationQuestionOptionSerializer(many=True, required=False)

    class Meta:
        model = EvaluationQuestion
        fields = '__all__'

class EvaluationFormSerializer(serializers.ModelSerializer):
    questions = EvaluationQuestionSerializer(many=True, required=False)
    training_title = serializers.CharField(source='training_master.training_title', read_only=True)
    responses_count = serializers.SerializerMethodField()
    year = serializers.SerializerMethodField()

    class Meta:
        model = EvaluationForm
        fields = ['form_id', 'form_name', 'training_master', 'description', 'deadline', 'is_active', 'created_by', 'created_at', 'form_type', 'training_title', 'responses_count', 'questions', 'year']

    def get_responses_count(self, obj):
        from .models import EvaluationAnswer
        # Simplified to count all unique users who submitted, 
        # ensuring the count stays even if participant records are modified.
        return EvaluationAnswer.objects.filter(form=obj).values('user').distinct().count()

    def get_year(self, obj):
        if obj.training_master:
            event = obj.training_master.trainingevent_set.order_by('-start_date').first()
            if event and event.start_date:
                return event.start_date.year
        if obj.created_at:
            return obj.created_at.year
        return None

class EvaluationAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationAnswer
        fields = '__all__'

class EvaluationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationResult
        fields = '__all__'

# AI Serializers

class AiAdminConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiAdminConfig
        fields = ['config_id', 'config_key', 'config_value', 'is_active', 'updated_by', 'updated_at']



class AiChatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiChatLog
        fields = [
            'log_id', 'session', 'user', 'nik', 'role', 'user_message', 'ai_response', 
            'intent', 'faq', 'is_faq_triggered', 'is_out_of_scope', 'is_unanswered', 
            'redirected_to_wa', 'is_authorized', 'query_executed', 'context_sent', 
            'response_time_ms', 'tokens_used', 'created_at'
        ]

class AiChatSessionSerializer(serializers.ModelSerializer):
    logs = AiChatLogSerializer(many=True, read_only=True)

    class Meta:
        model = AiChatSession
        fields = ['session_id', 'user', 'nik', 'role', 'division_id', 'session_start', 'ip_address', 'user_agent', 'logs']
        read_only_fields = ['session_id', 'session_start', 'user', 'nik', 'role', 'division_id', 'ip_address', 'user_agent']

class AiUnauthorizedAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiUnauthorizedAttempt
        fields = '__all__'