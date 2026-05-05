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
    AiAdminConfig, AiFaq, AiChatSession, AiChatLog, AiUnauthorizedAttempt,
    Budget
)


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
        if user.is_superuser:
            user_role = "Super Administrator"
        elif user.groups.exists():
            user_role = user.groups.first().name
        else:
            user_role = "Employee"
            
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

        if user.is_superuser:
            user_role = "Super Administrator"
        elif user.groups.exists():
            user_role = user.groups.first().name
        else:
            user_role = "Employee"

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
        if obj.is_superuser:
            return "Super Administrator"
        elif obj.groups.exists():
            return obj.groups.first().name
        return "Employee"



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
    
    class Meta:
        model = Employee
        fields = [
            'nik', 'full_name', 'division', 'division_name', 
            'level', 'position_name', 'special_position', 'role', 'is_active',
            'attendance', 'inhouse_training', 'public_training', 'knowledge_sharing', 'elearning', 'iht_plus_public',
            'total_hours', 'inhouse_hours', 'public_hours', 'ks_hours', 'elearning_hours',
            'tna_count', 'tna_fulfilled', 'attendance_details'
        ]

    def get_role(self, obj):
        try:
            user = obj.profile_set.first().user
            if user.is_superuser:
                return "Super Administrator"
            elif user.groups.exists():
                return user.groups.first().name
        except Exception:
            pass
        return "Employee"

    def get_attendance_details(self, obj):
        events = obj.completed_events
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
                'hours': round(event_hours, 2)
            })
        return details

    def get_attendance(self, obj):
        return obj.attendance

    def get_inhouse_training(self, obj):
        return obj.training_stats['inhouse_count']

    def get_public_training(self, obj):
        return obj.training_stats['public_count']

    def get_knowledge_sharing(self, obj):
        return obj.training_stats['ks_count']

    def get_elearning(self, obj):
        return obj.training_stats['elearning_count']

    def get_iht_plus_public(self, obj):
        return obj.iht_plus_public

    def get_total_hours(self, obj):
        return obj.total_hours

    def get_inhouse_hours(self, obj):
        return round(obj.training_stats['inhouse_hours'], 2)

    def get_public_hours(self, obj):
        return round(obj.training_stats['public_hours'], 2)

    def get_ks_hours(self, obj):
        return round(obj.training_stats['ks_hours'], 2)

    def get_elearning_hours(self, obj):
        return round(obj.training_stats['elearning_hours'], 2)

    def get_tna_count(self, obj):
        return obj.tnaparticipant_set.count()

    def get_tna_fulfilled(self, obj):
        return obj.tna_fulfilled


class EmployeeMinimalSerializer(serializers.ModelSerializer):
    role = serializers.SerializerMethodField()
    tna_count = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = ['nik', 'full_name', 'role', 'position_name', 'tna_count']

    def get_role(self, obj):
        try:
            user = obj.profile_set.first().user
            if user.is_superuser:
                return "Super Administrator"
            elif user.groups.exists():
                return user.groups.first().name
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
    class Meta:
        model = Vendor
        fields = '__all__'
        read_only_fields = ['created_at']

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

    class Meta:
        model = TnaParticipant
        fields = [
            'tna_participant_id', 'tna', 'category_name', 'course_name', 
            'nik', 'employee_name', 'division_name', 'position_name',
            'iht_plus_public', 'tna_fulfilled'
        ]

    def get_iht_plus_public(self, obj):
        return obj.nik.iht_plus_public

    def get_tna_fulfilled(self, obj):
        return obj.nik.tna_fulfilled



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
        
        if hasattr(user, 'profile') and user.profile.employee:
            emp = user.profile.employee
            if "Head of Division" in user_groups:
                div_id = emp.division_id
                participants = EventParticipant.objects.filter(
                    event__training=obj,
                    nik__division_id=div_id
                ).select_related('nik').order_by('nik__full_name')
                
                names = [p.nik.full_name for p in participants]
                return ", ".join(sorted(list(set(names))))
            elif "Employee" in user_groups:
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

    class Meta:
        model = EvaluationForm
        fields = ['form_id', 'form_name', 'training_master', 'description', 'deadline', 'is_active', 'created_by', 'created_at', 'form_type', 'training_title', 'responses_count', 'questions']

    def get_responses_count(self, obj):
        return EvaluationAnswer.objects.filter(form=obj).values('user').distinct().count()

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
        fields = ['config_id', 'config_key', 'config_value', 'description', 'is_active', 'updated_by', 'updated_at']

class AiFaqSerializer(serializers.ModelSerializer):
    class Meta:
        model = AiFaq
        fields = ['faq_id', 'question', 'answer', 'sequence', 'is_published', 'created_by', 'updated_by', 'created_at', 'updated_at']
        read_only_fields = ['created_by', 'updated_by', 'created_at', 'updated_at']

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