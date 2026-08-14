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

    def validate(self, data):
        import re
        def normalize(val):
            if not val:
                return ""
            return re.sub(r'[^a-zA-Z0-9]', '', str(val)).lower()

        def get_levenshtein_similarity(s1, s2):
            len1, len2 = len(s1), len(s2)
            if len1 == 0:
                return 1.0 if len2 == 0 else 0.0
            if len2 == 0:
                return 0.0

            track = [[0] * (len1 + 1) for _ in range(len2 + 1)]
            for i in range(len1 + 1):
                track[0][i] = i
            for j in range(1, len2 + 1):
                track[j][0] = j

            for j in range(1, len2 + 1):
                for i in range(1, len1 + 1):
                    indicator = 0 if s1[i - 1] == s2[j - 1] else 1
                    track[j][i] = min(
                        track[j][i - 1] + 1,
                        track[j - 1][i] + 1,
                        track[j - 1][i - 1] + indicator
                    )

            distance = track[len2][len1]
            return 1.0 - (distance / max(len1, len2))

        def is_similar(s1, s2):
            if s1 == s2:
                return True
            sim = get_levenshtein_similarity(s1, s2)
            if sim >= 0.70:
                return True
            if s1.startswith(s2) or s2.startswith(s1) or s1.endswith(s2) or s2.endswith(s1):
                if abs(len(s1) - len(s2)) <= 3:
                    return True
            return False

        budget_name = data.get('budget_name')
        if budget_name is None and self.instance:
            budget_name = self.instance.budget_name

        start_date = data.get('start_date_budget')
        if start_date is None and self.instance:
            start_date = self.instance.start_date_budget

        end_date = data.get('end_date_budget')
        if end_date is None and self.instance:
            end_date = self.instance.end_date_budget

        # 1. Full Year Date Check (Start date must be Jan 1 and End date must be Dec 31)
        if start_date and end_date:
            start_str = str(start_date)
            end_str = str(end_date)

            is_jan_1 = start_str.endswith('-01-01')
            is_dec_31 = end_str.endswith('-12-31')

            if not (is_jan_1 and is_dec_31):
                raise serializers.ValidationError({
                    "start_date_budget": "Budget date must be full year (1 January - 31 December)"
                })

            start_year = start_str.split('-')[0]
            end_year = end_str.split('-')[0]
            if start_year != end_year:
                raise serializers.ValidationError({
                    "start_date_budget": "Budget start date and end date must be in the same year"
                })

        # 2. Duplicate & Similarity Checks against existing budgets
        norm_name = normalize(budget_name)

        queryset = Budget.objects.all()
        for existing in queryset:
            if self.instance and existing.pk == self.instance.pk:
                continue

            existing_norm_name = normalize(existing.budget_name)

            # Budget name check
            if norm_name and existing_norm_name and is_similar(norm_name, existing_norm_name):
                raise serializers.ValidationError({
                    "budget_name": "Budget name already exist or writing is too similar"
                })

            # Date overlap check
            if start_date and end_date and existing.start_date_budget and existing.end_date_budget:
                if str(start_date) == str(existing.start_date_budget) or str(end_date) == str(existing.end_date_budget):
                    raise serializers.ValidationError({
                        "start_date_budget": f"Budget for year {str(start_date).split('-')[0]} already exist"
                    })

        return data



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

    def validate(self, data):
        import re
        def normalize(val):
            if not val:
                return ""
            return re.sub(r'[^a-zA-Z0-9]', '', val).lower()

        def get_levenshtein_similarity(s1, s2):
            len1, len2 = len(s1), len(s2)
            if len1 == 0:
                return 1.0 if len2 == 0 else 0.0
            if len2 == 0:
                return 0.0

            track = [[0] * (len1 + 1) for _ in range(len2 + 1)]
            for i in range(len1 + 1):
                track[0][i] = i
            for j in range(len2 + 1):
                track[j][0] = j

            for j in range(1, len2 + 1):
                for i in range(1, len1 + 1):
                    indicator = 0 if s1[i - 1] == s2[j - 1] else 1
                    track[j][i] = min(
                        track[j][i - 1] + 1,
                        track[j - 1][i] + 1,
                        track[j - 1][i - 1] + indicator
                    )

            distance = track[len2][len1]
            return 1.0 - (distance / max(len1, len2))

        def is_similar(s1, s2):
            if s1 == s2:
                return True
            sim = get_levenshtein_similarity(s1, s2)
            if sim >= 0.70:
                return True
            if s1.startswith(s2) or s2.startswith(s1) or s1.endswith(s2) or s2.endswith(s1):
                if abs(len(s1) - len(s2)) <= 3:
                    return True
            return False

        queryset = CourseCategory.objects.all()

        if self.instance is None:
            # Creation mode
            course_category_id = data.get('course_category_id')
            category_name = data.get('category_name')

            norm_id = normalize(course_category_id)
            norm_name = normalize(category_name)

            for existing in queryset:
                existing_norm_id = normalize(existing.course_category_id)
                existing_norm_name = normalize(existing.category_name)

                # Code check must be exact match (norm_id == existing_norm_id)
                if norm_id and existing_norm_id and norm_id == existing_norm_id:
                    raise serializers.ValidationError({
                        "course_category_id": "course category already exist, input course category code and other category name"
                    })
                # Name check uses similarity
                if norm_name and existing_norm_name and is_similar(norm_name, existing_norm_name):
                    raise serializers.ValidationError({
                        "category_name": "course category already exist, input course category code and other category name"
                    })
        else:
            # Edit mode
            category_name = data.get('category_name')
            if category_name is not None:
                norm_new_name = normalize(category_name)
                norm_old_name = normalize(self.instance.category_name)

                # Only check duplicate if category_name has actually been modified
                if norm_new_name != norm_old_name:
                    for existing in queryset:
                        if normalize(existing.course_category_id) == normalize(self.instance.course_category_id):
                            continue
                        existing_norm_name = normalize(existing.category_name)
                        if norm_new_name and existing_norm_name and is_similar(norm_new_name, existing_norm_name):
                            raise serializers.ValidationError({
                                "category_name": "course category already exist, input course category code and other category name"
                            })

        return data


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

    def validate(self, data):
        import re
        def normalize(val):
            if not val:
                return ""
            return re.sub(r'[^a-zA-Z0-9]', '', val).lower()

        def get_levenshtein_similarity(s1, s2):
            len1, len2 = len(s1), len(s2)
            if len1 == 0:
                return 1.0 if len2 == 0 else 0.0
            if len2 == 0:
                return 0.0

            track = [[0] * (len1 + 1) for _ in range(len2 + 1)]
            for i in range(len1 + 1):
                track[0][i] = i
            for j in range(len2 + 1):
                track[j][0] = j

            for j in range(1, len2 + 1):
                for i in range(1, len1 + 1):
                    indicator = 0 if s1[i - 1] == s2[j - 1] else 1
                    track[j][i] = min(
                        track[j][i - 1] + 1,
                        track[j - 1][i] + 1,
                        track[j - 1][i - 1] + indicator
                    )

            distance = track[len2][len1]
            return 1.0 - (distance / max(len1, len2))

        def is_similar(s1, s2):
            if s1 == s2:
                return True
            sim = get_levenshtein_similarity(s1, s2)
            if sim >= 0.70:
                return True
            if s1.startswith(s2) or s2.startswith(s1) or s1.endswith(s2) or s2.endswith(s1):
                if abs(len(s1) - len(s2)) <= 3:
                    return True
            return False

        queryset = Course.objects.all()

        if self.instance is None:
            # Creation mode
            course_id = data.get('course_id')
            course_name = data.get('course_name')

            norm_id = normalize(course_id)
            norm_name = normalize(course_name)

            for existing in queryset:
                existing_norm_id = normalize(existing.course_id)
                existing_norm_name = normalize(existing.course_name)

                # Code check must be exact match (norm_id == existing_norm_id)
                if norm_id and existing_norm_id and norm_id == existing_norm_id:
                    raise serializers.ValidationError({
                        "course_id": "course already exist, input other course code and course name"
                    })
                # Name check uses similarity
                if norm_name and existing_norm_name and is_similar(norm_name, existing_norm_name):
                    raise serializers.ValidationError({
                        "course_name": "course already exist, input other course code and course name"
                    })
        else:
            # Edit mode
            course_name = data.get('course_name')
            if course_name is not None:
                norm_new_name = normalize(course_name)
                norm_old_name = normalize(self.instance.course_name)

                # Only check duplicate if course_name has actually been modified
                if norm_new_name != norm_old_name:
                    for existing in queryset:
                        if normalize(existing.course_id) == normalize(self.instance.course_id):
                            continue
                        existing_norm_name = normalize(existing.course_name)
                        if norm_new_name and existing_norm_name and is_similar(norm_new_name, existing_norm_name):
                            raise serializers.ValidationError({
                                "course_name": "course already exist, input other course code and course name"
                            })

        return data


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

    def validate(self, data):
        vendor_id = data.get('vendor_id')
        if vendor_id is None and self.instance:
            vendor_id = self.instance.vendor_id
            
        vendor_name = data.get('vendor_name')
        if vendor_name is None and self.instance:
            vendor_name = self.instance.vendor_name

        import re
        def normalize(val):
            if not val:
                return ""
            return re.sub(r'[^a-zA-Z0-9]', '', val).lower()

        norm_id = normalize(vendor_id)
        norm_name = normalize(vendor_name)

        def get_levenshtein_similarity(s1, s2):
            len1, len2 = len(s1), len(s2)
            if len1 == 0:
                return 1.0 if len2 == 0 else 0.0
            if len2 == 0:
                return 0.0
                
            track = [[0] * (len1 + 1) for _ in range(len2 + 1)]
            for i in range(len1 + 1):
                track[0][i] = i
            for j in range(len2 + 1):
                track[j][0] = j
                
            for j in range(1, len2 + 1):
                for i in range(1, len1 + 1):
                    indicator = 0 if s1[i - 1] == s2[j - 1] else 1
                    track[j][i] = min(
                        track[j][i - 1] + 1,
                        track[j - 1][i] + 1,
                        track[j - 1][i - 1] + indicator
                    )
                    
            distance = track[len2][len1]
            return 1.0 - (distance / max(len1, len2))

        def is_similar(s1, s2):
            if s1 == s2:
                return True
            sim = get_levenshtein_similarity(s1, s2)
            if sim >= 0.70:
                return True
            if s1.startswith(s2) or s2.startswith(s1) or s1.endswith(s2) or s2.endswith(s1):
                if abs(len(s1) - len(s2)) <= 3:
                    return True
            return False

        queryset = Vendor.objects.all()
        for existing in queryset:
            if self.instance and normalize(existing.pk) == normalize(self.instance.pk):
                continue
            existing_norm_id = normalize(existing.vendor_id)
            existing_norm_name = normalize(existing.vendor_name)
            
            if norm_id and existing_norm_id and is_similar(norm_id, existing_norm_id):
                raise serializers.ValidationError({
                    "vendor_id": "vendor already exist, input vendor code and other vendor name"
                })
            if norm_name and existing_norm_name and is_similar(norm_name, existing_norm_name):
                raise serializers.ValidationError({
                    "vendor_name": "vendor already exist, input vendor code and other vendor name"
                })

        return data



class TnaPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = TnaPeriod
        fields = '__all__'
        read_only_fields = ['created_at']

    def validate(self, data):
        import re
        def normalize(val):
            if not val:
                return ""
            return re.sub(r'[^a-zA-Z0-9]', '', str(val)).lower()

        def get_levenshtein_similarity(s1, s2):
            len1, len2 = len(s1), len(s2)
            if len1 == 0:
                return 1.0 if len2 == 0 else 0.0
            if len2 == 0:
                return 0.0

            track = [[0] * (len1 + 1) for _ in range(len2 + 1)]
            for i in range(len1 + 1):
                track[0][i] = i
            for j in range(1, len2 + 1):
                track[j][0] = j

            for j in range(1, len2 + 1):
                for i in range(1, len1 + 1):
                    indicator = 0 if s1[i - 1] == s2[j - 1] else 1
                    track[j][i] = min(
                        track[j][i - 1] + 1,
                        track[j - 1][i] + 1,
                        track[j - 1][i - 1] + indicator
                    )

            distance = track[len2][len1]
            return 1.0 - (distance / max(len1, len2))

        def is_similar(s1, s2):
            if s1 == s2:
                return True
            sim = get_levenshtein_similarity(s1, s2)
            if sim >= 0.70:
                return True
            if s1.startswith(s2) or s2.startswith(s1) or s1.endswith(s2) or s2.endswith(s1):
                if abs(len(s1) - len(s2)) <= 3:
                    return True
            return False

        year = data.get('year')
        if year is None and self.instance:
            year = self.instance.year

        open_date = data.get('open_date')
        if open_date is None and self.instance:
            open_date = self.instance.open_date

        close_date = data.get('close_date')
        if close_date is None and self.instance:
            close_date = self.instance.close_date

        # 1. Full Year Date Check (Open date must be Jan 1 and Close date must be Dec 31)
        if open_date and close_date:
            open_str = str(open_date)
            close_str = str(close_date)

            is_jan_1 = open_str.endswith('-01-01')
            is_dec_31 = close_str.endswith('-12-31')

            if not (is_jan_1 and is_dec_31):
                raise serializers.ValidationError({
                    "open_date": "Period date must be full year (1 January - 31 December)"
                })

            if year:
                expected_open = f"{year}-01-01"
                expected_close = f"{year}-12-31"
                if open_str != expected_open or close_str != expected_close:
                    raise serializers.ValidationError({
                        "open_date": f"Date for year {year} must be {expected_open} to {expected_close}"
                    })

        # 2. Duplicate & Similarity Checks against existing periods
        period_code = data.get('period_code')
        if period_code is None and self.instance:
            period_code = self.instance.period_code

        period_name = data.get('period_name')
        if period_name is None and self.instance:
            period_name = self.instance.period_name

        norm_code = normalize(period_code)
        norm_name = normalize(period_name)

        queryset = TnaPeriod.objects.all()
        for existing in queryset:
            if self.instance and existing.pk == self.instance.pk:
                continue

            # Year uniqueness
            if year and existing.year == int(year):
                raise serializers.ValidationError({
                    "year": f"TNA Period for year {year} already exist"
                })

            existing_norm_code = normalize(existing.period_code)
            existing_norm_name = normalize(existing.period_name)

            # Period code check
            if norm_code and existing_norm_code and is_similar(norm_code, existing_norm_code):
                raise serializers.ValidationError({
                    "period_code": "Period code already exist or writing is too similar"
                })

            # Period name check
            if norm_name and existing_norm_name and is_similar(norm_name, existing_norm_name):
                raise serializers.ValidationError({
                    "period_name": "Period name already exist or writing is too similar"
                })

        return data


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

    def validate(self, data):
        tna_id = data.get('tna_id')
        if tna_id is None and self.instance:
            tna_id = self.instance.tna_id

        tna_period = data.get('tna_period')
        if tna_period is None and self.instance:
            tna_period = self.instance.tna_period

        course_category = data.get('course_category')
        if course_category is None and self.instance:
            course_category = self.instance.course_category

        course = data.get('course')
        if course is None and self.instance:
            course = self.instance.course

        group_name = data.get('group_name')
        if group_name is None and self.instance:
            group_name = self.instance.group_name

        # 1. TNA ID uniqueness check for creation
        if self.instance is None and tna_id:
            if TnaMaster.objects.filter(tna_id__iexact=tna_id).exists():
                raise serializers.ValidationError({
                    "tna_id": "TNA ID already exist"
                })

        # 2. Check (tna_period, course_category, course, group_name) combination
        period_pk = tna_period.pk if hasattr(tna_period, 'pk') else tna_period
        cat_pk = course_category.pk if hasattr(course_category, 'pk') else course_category
        course_pk = course.pk if hasattr(course, 'pk') else course

        if period_pk and cat_pk and course_pk and group_name is not None:
            queryset = TnaMaster.objects.filter(
                tna_period_id=period_pk,
                course_category_id=cat_pk,
                course_id=course_pk,
                group_name=group_name
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise serializers.ValidationError({
                    "non_field_errors": "TNA with the same Period, Category, and Course already exist"
                })

        return data


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

    def validate(self, data):
        tna = data.get('tna')
        if tna is None and self.instance:
            tna = self.instance.tna

        nik = data.get('nik')
        if nik is None and self.instance:
            nik = self.instance.nik

        if tna and nik:
            tna_pk = tna.pk if hasattr(tna, 'pk') else tna
            nik_pk = nik.pk if hasattr(nik, 'pk') else nik

            queryset = TnaParticipant.objects.filter(tna_id=tna_pk, nik_id=nik_pk)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                emp_name = nik.full_name if hasattr(nik, 'full_name') and nik.full_name else 'Employee'
                raise serializers.ValidationError({
                    "nik": f"{emp_name} already registered in this TNA"
                })

        return data

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

    def validate(self, data):
        hotel_id = data.get('hotel_id')
        if hotel_id is None and self.instance:
            hotel_id = self.instance.hotel_id
            
        hotel_name = data.get('hotel_name')
        if hotel_name is None and self.instance:
            hotel_name = self.instance.hotel_name

        hotel_city = data.get('hotel_city')
        if hotel_city is None and self.instance:
            hotel_city = self.instance.hotel_city

        import re
        def normalize(val):
            if not val:
                return ""
            return re.sub(r'[^a-zA-Z0-9]', '', val).lower()

        norm_id = normalize(hotel_id)
        norm_name = normalize(hotel_name)
        norm_city = normalize(hotel_city)

        def get_levenshtein_similarity(s1, s2):
            len1, len2 = len(s1), len(s2)
            if len1 == 0:
                return 1.0 if len2 == 0 else 0.0
            if len2 == 0:
                return 0.0
                
            track = [[0] * (len1 + 1) for _ in range(len2 + 1)]
            for i in range(len1 + 1):
                track[0][i] = i
            for j in range(len2 + 1):
                track[j][0] = j
                
            for j in range(1, len2 + 1):
                for i in range(1, len1 + 1):
                    indicator = 0 if s1[i - 1] == s2[j - 1] else 1
                    track[j][i] = min(
                        track[j][i - 1] + 1,
                        track[j - 1][i] + 1,
                        track[j - 1][i - 1] + indicator
                    )
                    
            distance = track[len2][len1]
            return 1.0 - (distance / max(len1, len2))

        def is_similar(s1, s2):
            if s1 == s2:
                return True
            sim = get_levenshtein_similarity(s1, s2)
            if sim >= 0.70:
                return True
            if s1.startswith(s2) or s2.startswith(s1) or s1.endswith(s2) or s2.endswith(s1):
                if abs(len(s1) - len(s2)) <= 3:
                    return True
            return False

        queryset = Hotel.objects.all()
        for existing in queryset:
            if self.instance and normalize(existing.pk) == normalize(self.instance.pk):
                continue
            existing_norm_id = normalize(existing.hotel_id)
            existing_norm_name = normalize(existing.hotel_name)
            existing_norm_city = normalize(existing.hotel_city)
            
            if norm_id and existing_norm_id and norm_id == existing_norm_id:
                raise serializers.ValidationError({
                    "hotel_id": "venue already exist, input other venue code and venue name"
                })
            if norm_name and existing_norm_name and is_similar(norm_name, existing_norm_name):
                if norm_city and existing_norm_city and is_similar(norm_city, existing_norm_city):
                    raise serializers.ValidationError({
                        "hotel_name": "venue already exist, input other venue code and venue name"
                    })

        return data


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

        # Check for duplicate in same event
        same_event_qs = EventParticipant.objects.filter(event=event, nik=nik)
        if self.instance:
            same_event_qs = same_event_qs.exclude(pk=self.instance.pk)
        if same_event_qs.exists():
            emp_name = nik.full_name if hasattr(nik, 'full_name') and nik.full_name else 'Employee'
            raise serializers.ValidationError({
                "nik": f"{emp_name} already registered in this training"
            })

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
            emp_name = nik.full_name if hasattr(nik, 'full_name') and nik.full_name else 'Employee'
            raise serializers.ValidationError(
                f"{emp_name} already registered for other training: {conflict_event.training_topic} ({conflict_event.start_date} to {conflict_event.end_date})"
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
            'intent', 'is_out_of_scope', 'is_unanswered', 
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