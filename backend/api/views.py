import requests
import time
import json
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import viewsets, permissions, exceptions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import (
    Employee, CourseCategory, Course,
    Vendor, TnaPeriod, TnaMaster, TnaParticipant, Hotel,
    TrainingMaster, TrainingEvent, EventLocation, EventSchedule,
    EventParticipant, EventCost, EventDocument, Division,
    EvaluationForm, EvaluationQuestion, EvaluationQuestionOption,
    EvaluationAnswer, EvaluationResult,
    AiAdminConfig, AiFaq, AiChatSession, AiChatLog, AiUnauthorizedAttempt
)
from .serializers import (
    UserSerializer, MyTokenObtainPairSerializer,
    EmployeeSerializer, CourseCategorySerializer, CourseSerializer,
    VendorSerializer, TnaPeriodSerializer, TnaMasterSerializer,
    TnaParticipantSerializer, HotelSerializer,
    TrainingMasterSerializer, TrainingEventSerializer, EventLocationSerializer,
    EventScheduleSerializer, EventParticipantSerializer, EventCostSerializer,
    EventDocumentSerializer, DivisionSerializer, EvaluationFormSerializer, EvaluationQuestionSerializer,
    EvaluationQuestionOptionSerializer, EvaluationAnswerSerializer,
    EvaluationResultSerializer,
    AiAdminConfigSerializer, AiFaqSerializer, AiChatSessionSerializer, 
    AiChatLogSerializer, AiUnauthorizedAttemptSerializer
)


# Custom Permission
class IsSuperAdmin(permissions.BasePermission):
    """
    Hanya mengizinkan Super Administrator (is_superuser=True) untuk endopint autentikasi
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Super Administrator & Administrator → full CRUD, yang lain Read-Only
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser:
            return True
        user_groups = list(request.user.groups.values_list('name', flat=True))
        return 'Administrator' in user_groups


# Jwt login view
class MyTokenObtainPairView(TokenObtainPairView):
    """
    Custom login view yang menggunakan MyTokenObtainPairSerializer
    untuk menyertakan role, email, dan nik di JWT token.
    """
    serializer_class = MyTokenObtainPairSerializer

# viewset super admin

class UserViewSet(viewsets.ModelViewSet):
    """
    Hanya Super Administrator yang bisa mengelola data Autentikasi (User).
    """
    serializer_class = UserSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return User.objects.all()


class CourseCategoryViewSet(viewsets.ModelViewSet):
    """
    Super Administrator & Administrator → full CRUD, yang lain read-only
    """
    serializer_class = CourseCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['course_category_id', 'category_name', 'description']
    lookup_field = 'course_category_id'

    def get_queryset(self):
        return CourseCategory.objects.all().order_by('course_category_id')


class CourseViewSet(viewsets.ModelViewSet):
    """
    Super Administrator & Administrator → full CRUD, yang lain read-only
    """
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['course_id', 'course_name', 'description']
    lookup_field = 'course_id'

    def get_queryset(self):
        qs = Course.objects.all().order_by('course_id')
        category_id = self.request.query_params.get('category', None)
        if category_id:
            qs = qs.filter(course_category_id=category_id)
        return qs


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by('vendor_name')
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['vendor_id', 'vendor_name', 'speciality', 'city', 'pic_name', 'provider_type', 'province']


class TnaPeriodViewSet(viewsets.ModelViewSet):
    queryset = TnaPeriod.objects.all().order_by('-year', 'tna_period_id')
    serializer_class = TnaPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['period_code', 'period_name']


class TnaMasterViewSet(viewsets.ModelViewSet):
    queryset = TnaMaster.objects.all().order_by('course_category__category_name', 'course__course_name')
    serializer_class = TnaMasterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tna_id', 'course__course_name']

    def get_queryset(self):
        user = self.request.user
        user_groups = list(user.groups.values_list('name', flat=True))
        qs = TnaMaster.objects.all().order_by('course_category__category_name', 'course__course_name')

        # RBAC Logic
        if user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            pass
        elif "Head of Division" in user_groups or "Team Leader" in user_groups:
            if hasattr(user, 'profile'):
                qs = qs.filter(tnaparticipant__nik__division_id=user.profile.employee.division_id).distinct()
            else:
                return TnaMaster.objects.none()
        else:
            if hasattr(user, 'profile'):
                qs = qs.filter(tnaparticipant__nik=user.profile.employee).distinct()
            else:
                return TnaMaster.objects.none()

        category_id = self.request.query_params.get('category', None)
        period_id = self.request.query_params.get('period', None)
        course_id = self.request.query_params.get('course', None)
        group_name = self.request.query_params.get('group_name', None)

        if category_id:
            qs = qs.filter(course_category_id=category_id)
        if period_id:
            qs = qs.filter(tna_period_id=period_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        if group_name:
            qs = qs.filter(group_name=group_name)
        return qs



class TnaParticipantViewSet(viewsets.ModelViewSet):
    queryset = TnaParticipant.objects.all().order_by('tna__course_category__category_name', 'tna__course__course_name')
    serializer_class = TnaParticipantSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nik__full_name', 'tna__tna_id', 'tna__course_category__category_name', 'tna__course__course_name']

    def get_queryset(self):
        user = self.request.user
        user_groups = list(user.groups.values_list('name', flat=True))
        qs = TnaParticipant.objects.all().select_related(
            'tna__course_category', 'tna__course', 'nik__division'
        ).prefetch_related(
            'nik__eventparticipant_set__event__training',
            'nik__eventparticipant_set__event__schedules',
            'nik__tnaparticipant_set__tna__course'
        ).order_by('tna__course_category__category_name', 'tna__course__course_name')

        # RBAC Logic
        if user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            pass
        elif "Head of Division" in user_groups or "Team Leader" in user_groups:
            if hasattr(user, 'profile'):
                qs = qs.filter(nik__division_id=user.profile.employee.division_id)
            else:
                return TnaParticipant.objects.none()
        else:
            if hasattr(user, 'profile'):
                qs = qs.filter(nik=user.profile.employee)
            else:
                return TnaParticipant.objects.none()

        tna_id = self.request.query_params.get('tna_id', None)
        period_id = self.request.query_params.get('period', None)
        course_id = self.request.query_params.get('course', None)
        course_name = self.request.query_params.get('course_name', None)
        division = self.request.query_params.get('division', None)
        group_name = self.request.query_params.get('group_name', None)

        if tna_id:
            qs = qs.filter(tna_id=tna_id)
        if period_id:
            qs = qs.filter(tna__tna_period_id=period_id)
        if course_id:
            qs = qs.filter(tna__course_id=course_id)
        if course_name:
            qs = qs.filter(tna__course__course_name=course_name)
        if division:
            qs = qs.filter(nik__division__division_name=division)
        if group_name:
            qs = qs.filter(tna__group_name=group_name)
        return qs


class HotelViewSet(viewsets.ModelViewSet):
    """
    Super Administrator & Administrator → full CRUD, yang lain read-only
    """
    queryset = Hotel.objects.all().order_by('hotel_city', 'hotel_name')
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['hotel_id', 'hotel_name', 'hotel_city']


class EmployeeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        queryset = Employee.objects.all().select_related(
            'division'
        ).prefetch_related(
            'eventparticipant_set__event__training',
            'eventparticipant_set__event__schedules',
            'tnaparticipant_set__tna__course',
            'profile_set__user__groups'
        ).order_by('nik')
        
        division = self.request.query_params.get('division')
        if division:
            queryset = queryset.filter(division__division_name__icontains=division)
            
        return queryset

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('nopage') == 'true':
            return None
        return super().paginate_queryset(queryset)
    
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['nik', 'full_name', 'division__division_name', 'level', 'position_name']


class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all().order_by('division_id')
    serializer_class = DivisionSerializer
    permission_classes = [permissions.IsAuthenticated]


class TrainingMasterViewSet(viewsets.ModelViewSet):
    queryset = TrainingMaster.objects.all().select_related(
        'course', 'course_category', 'pic', 'vendor', 'pic__division'
    ).prefetch_related(
        'trainingevent_set',
        'trainingevent_set__location',
        'trainingevent_set__schedules',
        'trainingevent_set__participants',
        'trainingevent_set__costs'
    ).order_by('training_type', 'course_category__category_name', 'course__course_name', 'training_title')
    serializer_class = TrainingMasterSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['training_code', 'training_title', 'course__course_name']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
            
        user_groups = list(user.groups.values_list('name', flat=True))
        
        if user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            # Apply standard filters
            division_filter = self.request.query_params.get('division')
            month_filter = self.request.query_params.get('month')
            
            if division_filter:
                qs = qs.filter(trainingevent__participants__nik__division_id=division_filter).distinct()
            if month_filter:
                try:
                    m = int(month_filter)
                    qs = qs.filter(trainingevent__start_date__month=m).distinct()
                except (ValueError, TypeError):
                    pass
        elif "Head of Division" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                div_id = user.profile.employee.division_id
                # Only show trainings that have at least one participant from their division
                qs = qs.filter(trainingevent__participants__nik__division_id=div_id).distinct()
            else:
                qs = qs.none()
        elif "Employee" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                emp = user.profile.employee
                # Only show trainings that they participated in
                qs = qs.filter(trainingevent__participants__nik=emp).distinct()
            else:
                qs = qs.none()
        else:
            qs = qs.none()
            
        return qs


class TrainingEventViewSet(viewsets.ModelViewSet):
    queryset = TrainingEvent.objects.all().order_by('-start_date', 'event_id')
    serializer_class = TrainingEventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['training_topic', 'training__training_code']


class EventLocationViewSet(viewsets.ModelViewSet):
    queryset = EventLocation.objects.all().order_by('event_location_id')
    serializer_class = EventLocationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class EventScheduleViewSet(viewsets.ModelViewSet):
    queryset = EventSchedule.objects.all().order_by('training_date', 'start_time')
    serializer_class = EventScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class EventParticipantViewSet(viewsets.ModelViewSet):
    queryset = EventParticipant.objects.all().order_by('event_id', 'nik')
    serializer_class = EventParticipantSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nik__full_name', 'nik__nik']


class EventCostViewSet(viewsets.ModelViewSet):
    queryset = EventCost.objects.all().order_by('event_id')
    serializer_class = EventCostSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class EventDocumentViewSet(viewsets.ModelViewSet):
    queryset = EventDocument.objects.all().order_by('-uploaded_at')
    serializer_class = EventDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
class AddTrainingView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get(self, request, pk=None):
        if not pk:
            return Response({"error": "PK required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tm = TrainingMaster.objects.get(pk=pk)
            serializer = TrainingMasterSerializer(tm)
            return Response(serializer.data)
        except TrainingMaster.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            tm = TrainingMaster.objects.create(
                training_code=data.get('training_code'),
                training_type=data.get('training_type'),
                training_category=data.get('training_category'),
                course_category_id=data.get('course_category'),
                course_id=data.get('course'),
                training_title=data.get('training_title'),
                training_description=data.get('training_description'),
                pic_id=data.get('pic'),
                vendor_id=data.get('vendor_id'),
                estimated_cost=data.get('estimated_cost') or 0,
                is_active=True
            )

            eval_data = data.get('evaluation', {})
            event = TrainingEvent.objects.create(
                training=tm,
                training_topic=data.get('topic'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                status=data.get('status', 'draft').lower(),
                enable_course_access=eval_data.get('enable_course_access', False),
                enable_feedback=eval_data.get('enable_feedback', False),
                enable_evaluations=eval_data.get('enable_evaluations', False)
            )

            loc_data = data.get('location', {})
            EventLocation.objects.create(
                event=event,
                city=loc_data.get('city'),
                venue=loc_data.get('venue'),
                room=loc_data.get('room'),
                address=loc_data.get('address')
            )

            for sch in data.get('schedules', []):
                if sch.get('date'):
                    EventSchedule.objects.create(
                        event=event,
                        training_date=sch.get('date'),
                        start_time=sch.get('start') or None,
                        end_time=sch.get('end') or None,
                        material_link=sch.get('material'),
                        instructor_name=sch.get('instructor')
                    )

            for part in data.get('participants', []):
                if part.get('employee'):
                    l2_val = part.get('l2')
                    if l2_val is not None and l2_val != "":
                        try:
                            l2_num = float(l2_val)
                            if l2_num > 4:
                                if l2_num <= 25: l2_val = 1
                                elif l2_num <= 50: l2_val = 2
                                elif l2_num <= 75: l2_val = 3
                                else: l2_val = 4
                        except:
                            pass

                    EventParticipant.objects.create(
                        event=event,
                        nik_id=part.get('employee'),
                        l1_score=part.get('l1') or None,
                        l2_score=l2_val if l2_val != "" else None
                    )

            for cost in data.get('costs', []):
                if cost.get('training') or cost.get('room') or cost.get('sppd'):
                    EventCost.objects.create(
                        event=event,
                        cost_center=cost.get('cost_center'),
                        currency=cost.get('currency', 'IDR'),
                        room_cost=cost.get('room') or 0,
                        training_cost=cost.get('training') or 0,
                        sppd_cost=cost.get('sppd') or 0,
                        cost_type=data.get('cost_allocation_type', 'Estimate Cost'),
                        status_cost=cost.get('status', 'Unpaid')
                    )

            for doc in data.get('documents', []):
                if doc.get('url'):
                    EventDocument.objects.create(
                        event=event,
                        document_type=doc.get('type') or 'Other',
                        file_name=doc.get('file_name') or 'Untitled',
                        file_url=doc.get('url'),
                        uploaded_by_id=doc.get('submitted_by')
                    )

            return Response({"message": "Training saved successfully", "training_code": tm.training_code}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def put(self, request, pk=None):
        if not pk:
            return Response({"error": "PK required"}, status=status.HTTP_400_BAD_REQUEST)
        
        data = request.data
        try:
            tm = TrainingMaster.objects.get(pk=pk)
            # Update TrainingMaster
            tm.training_code = data.get('training_code', tm.training_code)
            tm.training_type = data.get('training_type', tm.training_type)
            tm.training_category = data.get('training_category', tm.training_category)
            tm.course_category_id = data.get('course_category', tm.course_category_id)
            tm.course_id = data.get('course', tm.course_id)
            tm.training_title = data.get('training_title', tm.training_title)
            tm.training_description = data.get('training_description', tm.training_description)
            tm.pic_id = data.get('pic', tm.pic_id)
            tm.vendor_id = data.get('vendor_id', tm.vendor_id)
            tm.estimated_cost = data.get('estimated_cost', tm.estimated_cost)
            tm.save()

            # For simplicity, we update the LATEST event or create one if none exists
            event = tm.trainingevent_set.order_by('-start_date').first()
            if not event:
                # This shouldn't happen if created via this flow, but handles legacy
                event = TrainingEvent.objects.create(training=tm, training_topic=data.get('topic', 'Untitled'), start_date='2026-01-01', end_date='2026-01-01')

            eval_data = data.get('evaluation', {})
            event.training_topic = data.get('topic', event.training_topic)
            event.start_date = data.get('start_date', event.start_date)
            event.end_date = data.get('end_date', event.end_date)
            event.status = data.get('status', event.status).lower()
            event.enable_course_access = eval_data.get('enable_course_access', event.enable_course_access)
            event.enable_feedback = eval_data.get('enable_feedback', event.enable_feedback)
            event.enable_evaluations = eval_data.get('enable_evaluations', event.enable_evaluations)
            event.save()

            # Update Location
            loc_data = data.get('location', {})
            if hasattr(event, 'location'):
                loc = event.location
                loc.city = loc_data.get('city', loc.city)
                loc.venue = loc_data.get('venue', loc.venue)
                loc.room = loc_data.get('room', loc.room)
                loc.address = loc_data.get('address', loc.address)
                loc.save()
            else:
                EventLocation.objects.create(event=event, **loc_data)

            # Update Schedules (easier to replace)
            event.schedules.all().delete()
            for sch in data.get('schedules', []):
                if sch.get('date'):
                    EventSchedule.objects.create(
                        event=event,
                        training_date=sch.get('date'),
                        start_time=sch.get('start') or None,
                        end_time=sch.get('end') or None,
                        material_link=sch.get('material'),
                        instructor_name=sch.get('instructor')
                    )

            # Update Participants
            event.participants.all().delete()
            for part in data.get('participants', []):
                if part.get('employee'):
                    l2_val = part.get('l2')
                    if l2_val is not None and l2_val != "":
                        try:
                            l2_num = float(l2_val)
                            if l2_num > 4:
                                if l2_num <= 25: l2_val = 1
                                elif l2_num <= 50: l2_val = 2
                                elif l2_num <= 75: l2_val = 3
                                else: l2_val = 4
                        except:
                            pass

                    EventParticipant.objects.create(
                        event=event,
                        nik_id=part.get('employee'),
                        l1_score=part.get('l1') or None,
                        l2_score=l2_val if l2_val != "" else None
                    )

            # Update Costs
            event.costs.all().delete()
            for cost in data.get('costs', []):
                if cost.get('training') or cost.get('room') or cost.get('sppd'):
                    EventCost.objects.create(
                        event=event,
                        cost_center=cost.get('cost_center'),
                        currency=cost.get('currency', 'IDR'),
                        room_cost=cost.get('room') or 0,
                        training_cost=cost.get('training') or 0,
                        sppd_cost=cost.get('sppd') or 0,
                        cost_type=data.get('cost_allocation_type', 'Estimate Cost'),
                        status_cost=cost.get('status', 'Unpaid')
                    )

            # Update Documents
            event.documents.all().delete()
            for doc in data.get('documents', []):
                if doc.get('url'):
                    EventDocument.objects.create(
                        event=event,
                        document_type=doc.get('type') or 'Other',
                        file_name=doc.get('file_name') or 'Untitled',
                        file_url=doc.get('url'),
                        uploaded_by_id=doc.get('submitted_by')
                    )

            return Response({"message": "Training updated successfully"})
        except TrainingMaster.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk=None):
        if not pk:
            return Response({"error": "PK required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            tm = TrainingMaster.objects.get(pk=pk)
            tm.delete()
            return Response({"message": "Training deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except TrainingMaster.DoesNotExist:
            return Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)

# ─── Evaluation ViewSets ─────────────────────────────────────────────────────

class EvaluationFormViewSet(viewsets.ModelViewSet):
    queryset = EvaluationForm.objects.prefetch_related('questions', 'questions__options').all().order_by('-created_at')
    serializer_class = EvaluationFormSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['form_name', 'training_master__training_title', 'training_master__training_code']

    def get_permissions(self):
        if self.action in ['submit_answers', 'my_evaluations']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        data = request.data
        now = timezone.now()
        form = EvaluationForm.objects.create(
            form_name=data.get('form_name'),
            training_master_id=data.get('training_id'),
            description=data.get('description'),
            deadline=data.get('deadline'),
            form_type=data.get('form_type'),
            is_active=True,
            created_by=request.user,
            created_at=now
        )

        questions_data = data.get('questions', [])
        for seq_idx, q_data in enumerate(questions_data):
            question = EvaluationQuestion.objects.create(
                form=form,
                question_text=q_data.get('question_text', ''),
                question_type=q_data.get('question_type', 'Rating Scale'),
                evaluation_type=q_data.get('evaluation_type', form.form_type),
                sequence=seq_idx + 1,
                is_required=q_data.get('is_required', True),
                score=q_data.get('score'),
                is_active=q_data.get('is_active', True),
                created_by=request.user,
                created_at=now
            )

            options_data = q_data.get('options', [])
            for opt_idx, opt_data in enumerate(options_data):
                EvaluationQuestionOption.objects.create(
                    question=question,
                    option_text=opt_data.get('option_text', ''),
                    sequence=opt_idx + 1,
                    is_correct=opt_data.get('is_correct', False),
                    is_active=opt_data.get('is_active', True)
                )

        return Response(self.serializer_class(form).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        form = self.get_object()
        data = request.data
        
        # Update main form info
        if 'form_name' in data:
            form.form_name = data['form_name']
        if 'training_id' in data:
            form.training_master_id = data['training_id']
        if 'description' in data:
            form.description = data['description']
        if 'deadline' in data:
            form.deadline = data['deadline']
        if 'form_type' in data:
            form.form_type = data['form_type']
        form.save()

        # Update questions only if provided
        if 'questions' in data:
            # Wipe old questions (cascade handles options if FK is set to CASCADE, which it is)
            form.questions.all().delete()
            
            now = timezone.now()
            questions_data = data.get('questions', [])
            for seq_idx, q_data in enumerate(questions_data):
                question = EvaluationQuestion.objects.create(
                    form=form,
                    question_text=q_data.get('question_text', ''),
                    question_type=q_data.get('question_type', 'Rating Scale'),
                    evaluation_type=q_data.get('evaluation_type', form.form_type),
                    sequence=seq_idx + 1,
                    is_required=q_data.get('is_required', True),
                    score=q_data.get('score'),
                    is_active=q_data.get('is_active', True),
                    created_by=request.user,
                    created_at=now
                )

                options_data = q_data.get('options', [])
                for opt_idx, opt_data in enumerate(options_data):
                    EvaluationQuestionOption.objects.create(
                        question=question,
                        option_text=opt_data.get('option_text', ''),
                        sequence=opt_idx + 1,
                        is_correct=opt_data.get('is_correct', False),
                        is_active=opt_data.get('is_active', True)
                    )

        return Response(self.serializer_class(form).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def my_evaluations(self, request):
        employee = None
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'employee'):
            employee = request.user.profile.employee
        elif hasattr(request.user, 'employee'):
            employee = request.user.employee

        if not employee:
            return Response([], status=status.HTTP_200_OK)
            
        # Find all events where this employee is a participant
        # We need to filter based on event flags: enable_course_access must be True
        participants = EventParticipant.objects.filter(
            nik=employee, 
            event__enable_course_access=True
        ).select_related('event')
        
        result = []
        for p in participants:
            event = p.event
            # Get active forms for this specific training
            forms = EvaluationForm.objects.filter(
                training_master_id=event.training_id, 
                is_active=True
            ).prefetch_related('questions', 'questions__options')
            
            for form in forms:
                # Type is typically marked in form_name like '[L1] ...'
                # Prioritize form_type from DB, fallback to name check
                form_type = form.form_type if form.form_type else ('L2' if '[L2]' in (form.form_name or '') else 'L1')
                
                # Filter based on event settings
                if form_type == 'L1' and not event.enable_feedback:
                    continue
                if form_type == 'L2' and not event.enable_evaluations:
                    continue
                
                # Check if submitted
                answers_qs = EvaluationAnswer.objects.filter(form=form, user=request.user)
                has_submitted = answers_qs.exists()
                submitted_at = None
                score = None

                if has_submitted:
                    submitted_at = answers_qs.first().created_at.strftime('%d %B %Y') if answers_qs.first().created_at else None
                    p_qs = participants.filter(event__training_id=form.training_master_id).first()
                    if form_type == 'L2':
                        score = p_qs.l2_score if p_qs else None
                    else:
                        score = p_qs.l1_score if p_qs else None
                
                questions_list = []
                has_questions = form.questions.exists()
                if has_questions and not has_submitted:
                    for q in form.questions.filter(is_active=True).order_by('sequence'):
                        q_dict = {
                            'id': q.question_id,
                            'q': q.question_text,
                            'type': q.question_type,
                            'score': q.score,
                        }
                        if q.question_type in ['Multiple Choice', 'MultipleChoice']:
                            opts = []
                            correct_ans_label = 'A'
                            for idx, opt in enumerate(q.options.filter(is_active=True).order_by('sequence')):
                                opts.append({ 'id': opt.option_id, 'text': opt.option_text })
                                if opt.is_correct:
                                    correct_ans_label = chr(65 + idx)
                            q_dict['opts'] = opts
                            q_dict['answer'] = correct_ans_label 
                        questions_list.append(q_dict)
                
                # Strip [L1] / [L2] prefix for clean title
                clean_title = (form.form_name or '').replace('[L1] ', '').replace('[L2] ', '')
                result.append({
                    'id': form.form_id,
                    'title': clean_title,
                    'description': form.description,
                    'deadline': form.deadline.isoformat() if form.deadline else None,
                    'type': form_type,
                    'year': form.created_at.year if form.created_at else None,
                    'hasQuestions': has_questions,
                    'questions': questions_list,
                    'is_submitted': has_submitted,
                    'submittedAt': submitted_at,
                    'score': score
                })
            
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        form = self.get_object()
        user = request.user
        data = request.data # Expects: {'answers': [{'question_id': 1, 'rating': 4}, ...]}
        
        # Check if already submitted
        if EvaluationAnswer.objects.filter(form=form, user=user).exists():
            return Response({'error': 'Already submitted'}, status=status.HTTP_400_BAD_REQUEST)
            
        answers_data = data.get('answers', [])
        total_score = 0
        rating_sum = 0
        rating_count = 0
        form_type = form.form_type or ('L2' if '[L2]' in (form.form_name or '') else 'L1')
        
        with transaction.atomic():
            for ans in answers_data:
                question = EvaluationQuestion.objects.filter(question_id=ans.get('question_id')).first()
                if not question:
                    continue
                    
                selected_option = None
                text_ans = ans.get('text', None)
                rating = ans.get('rating', None)
                ans_score = 0
                
                if form_type == 'L2':
                    if 'option_id' in ans and ans['option_id']:
                        selected_option = EvaluationQuestionOption.objects.filter(option_id=ans['option_id']).first()
                        if selected_option and selected_option.is_correct:
                            ans_score = (question.score or 0)
                            total_score += ans_score
                else: # L1 Logic
                    # Hanya hitung yang tipenya Rating
                    if question.question_type in ['Rating', 'Rating Scale'] and rating is not None:
                        try:
                            val = float(rating)
                            ans_score = val
                            rating_sum += val
                            rating_count += 1
                        except (ValueError, TypeError):
                            pass
                
                EvaluationAnswer.objects.create(
                    question=question,
                    form=form,
                    user=user,
                    rating_value=rating if form_type == 'L1' else None,
                    selected_option=selected_option,
                    text_answer=text_ans,
                    l1_score=ans_score if form_type == 'L1' else None,
                    l2_score=ans_score if form_type == 'L2' else None,
                    created_at=timezone.now()
                )

            # Final Score Calculation
            if form_type == 'L2':
                total_possible = sum(q.score or 0 for q in form.questions.all())
                final_result = (total_score / total_possible * 100) if total_possible > 0 else 0
            else:
                final_result = (rating_sum / rating_count if rating_count > 0 else 0)

            # Update Participant score if linked to a training
            employee = getattr(user, 'employee', None) or (user.profile.employee if hasattr(user, 'profile') and hasattr(user.profile, 'employee') else None)
            if form.training_master_id and employee:
                participant = EventParticipant.objects.filter(event__training_id=form.training_master_id, nik=employee).first()
                if participant:
                    if form_type == 'L2':
                        # Convert 0-100 to 1-4
                        if final_result <= 25:
                            converted_score = 1
                        elif final_result <= 50:
                            converted_score = 2
                        elif final_result <= 75:
                            converted_score = 3
                        else:
                            converted_score = 4
                        participant.l2_score = converted_score
                        # Update final_result to match the converted score for the snapshot
                        final_result = converted_score
                    else:
                        participant.l1_score = final_result
                    participant.save()
                    
        # Update Summary Snapshot in EvaluationResult
        try:
            tm = TrainingMaster.objects.filter(training_id=form.training_master_id).first()
            training_name = tm.training_title if tm else "N/A"
            res_user_name = (employee.full_name if employee else (user.first_name + ' ' + user.last_name).strip() or user.username)[:200]
            
            EvaluationResult.objects.update_or_create(
                user=user,
                form=form,
                defaults={
                    'user_name': res_user_name,
                    'evaluation_name': (form.form_name or "N/A")[:200],
                    'training_name': (training_name or "N/A")[:200],
                    'template': form_type,
                    'score': round(float(final_result), 2),
                }
            )
        except Exception as e:
            print(f"Summary Sync Error: {e}")

        return Response({'message': 'Success', 'score': final_result}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def respondents(self, request, pk=None):
        form = self.get_object()
        # Query directly from EvaluationResult summary table
        results = EvaluationResult.objects.filter(form=form).order_by('-created_at')
        
        result = []
        for res in results:
            nik_val = 'N/A'
            if res.user:
                if hasattr(res.user, 'profile') and hasattr(res.user.profile, 'employee'):
                    nik_val = res.user.profile.employee.nik
                elif hasattr(res.user, 'employee'):
                    nik_val = res.user.employee.nik

            result.append({
                'nik': nik_val,
                'name': res.user_name or 'Anonymous',
                'score': float(res.score) if res.score is not None else 0.0
            })
            
        return Response(result, status=status.HTTP_200_OK)


class EvaluationQuestionViewSet(viewsets.ModelViewSet):
    queryset = EvaluationQuestion.objects.all().order_by('sequence')
    serializer_class = EvaluationQuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class EvaluationQuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = EvaluationQuestionOption.objects.all().order_by('sequence')
    serializer_class = EvaluationQuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

class EvaluationAnswerViewSet(viewsets.ModelViewSet):
    queryset = EvaluationAnswer.objects.all().order_by('-created_at')
    serializer_class = EvaluationAnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

class EvaluationResultViewSet(viewsets.ModelViewSet):
    queryset = EvaluationResult.objects.all().order_by('-created_at')
    serializer_class = EvaluationResultSerializer
    permission_classes = [permissions.IsAuthenticated]

# ─── AI Assistant ViewSets ──────────────────────────────────────────────────

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Super Administrator', 'Administrator']).exists()

class AiAdminConfigViewSet(viewsets.ModelViewSet):
    queryset = AiAdminConfig.objects.all()
    serializer_class = AiAdminConfigSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    @action(detail=False, methods=['get'])
    def get_wa_number(self, request):
        config = AiAdminConfig.objects.filter(config_key='admin_wa_number').first()
        return Response({'wa_number': config.config_value if config else '6281234567890'})

    @action(detail=False, methods=['post'])
    def set_wa_number(self, request):
        try:
            wa_number = request.data.get('wa_number')
            if not wa_number:
                return Response({'error': 'wa_number is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            config = AiAdminConfig.objects.filter(config_key='admin_wa_number').first()
            if config:
                config.config_value = str(wa_number)
                config.updated_by = request.user
                config.save()
            else:
                config = AiAdminConfig.objects.create(
                    config_key='admin_wa_number',
                    config_value=str(wa_number),
                    updated_by=request.user
                )
            
            return Response({'message': 'Success', 'wa_number': config.config_value})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AiFaqViewSet(viewsets.ModelViewSet):
    queryset = AiFaq.objects.all().order_by('sequence')
    serializer_class = AiFaqSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        is_admin = self.request.user.is_superuser or self.request.user.groups.filter(name__in=['Super Administrator', 'Administrator']).exists()
        if not is_admin:
            return qs.filter(is_published=True)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

class AiChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = AiChatSessionSerializer

    def get_queryset(self):
        return AiChatSession.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        group_role_map = {
            'Super Administrator': 'superadmin',
            'Administrator': 'admin',
            'Dean': 'dean',
            'Head of Division': 'head_of_division',
            'Team Leader': 'team_leader',
            'Employee': 'employee',
        }
        user_role = 'superadmin' if user.is_superuser else 'employee'
        if not user.is_superuser and user.groups.exists():
            group_name = user.groups.first().name
            user_role = group_role_map.get(group_name, 'employee')
        serializer.save(user=user, role=user_role)

    def get_ai_context(self, user, role, message):
        context_data = {}
        try:
            employee = None
            try:
                profile = getattr(user, 'profile', None)
                employee = profile.employee if profile else None
            except:
                pass

            # Info personal user
            if employee:
                context_data['user_info'] = {
                    'full_name': employee.full_name,
                    'gender': employee.gender or 'Unknown',
                    'divisi': employee.division.division_name if employee.division else 'N/A',
                    'posisi': employee.position_name or 'N/A',
                }

            # 1. Training Info
            trainings = TrainingMaster.objects.all()
            if role in ['head_of_division', 'team_leader'] and employee:
                # Relationship: TrainingMaster -> TrainingEvent (trainingevent_set) -> EventParticipant (participants) -> Employee (nik)
                trainings = trainings.filter(trainingevent__participants__nik__division_id=employee.division_id).distinct()
            elif role == 'employee' and employee:
                trainings = trainings.filter(trainingevent__participants__nik=employee).distinct()
            
            context_data['recent_trainings'] = list(trainings.values('training_title', 'training_type', 'training_code')[:5])

            # 2. TNA Info
            tnas = TnaMaster.objects.all()
            if role in ['head_of_division', 'team_leader'] and employee:
                # Relationship: TnaMaster -> TnaParticipant -> Employee
                tnas = tnas.filter(tnaparticipant__nik__division_id=employee.division_id).distinct()
            elif role == 'employee' and employee:
                tnas = tnas.filter(tnaparticipant__nik=employee).distinct()
            
            context_data['tna_summary'] = list(tnas.values('tna_id')[:5]) 

            # 3. Vendor Info (Only for Admin/Dean)
            if role in ['superadmin', 'admin', 'dean']:
                context_data['vendors'] = list(Vendor.objects.all().values('vendor_name', 'provider_type')[:5])

        except Exception as e:
            print(f"Context Builder Error: {e}")
            context_data['error'] = str(e)

        return json.dumps(context_data)

    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        start_time = time.time()
        try:
            session = self.get_object()
            message = request.data.get('message')
            if not message:
                return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

            context = None 

            # 1. Get User Info
            group_role_map = {
                'Super Administrator': 'superadmin',
                'Administrator': 'admin',
                'Dean': 'dean',
                'Head of Division': 'head_of_division',
                'Team Leader': 'team_leader',
                'Employee': 'employee',
            }
            user_role = 'superadmin' if request.user.is_superuser else 'employee'
            if not request.user.is_superuser and request.user.groups.exists():
                group_name = request.user.groups.first().name
                user_role = group_role_map.get(group_name, 'employee')

            employee_nik = None
            division_id = None
            try:
                profile = getattr(request.user, 'profile', None)
                if profile and profile.employee:
                    employee_nik = profile.employee.nik
                    division_id = str(profile.employee.division_id) if profile.employee.division_id else None
            except Exception as e:
                print(f"Profile error: {e}")

            # 2. Scope Detection
            scope_keywords = ['training', 'tna', 'pelatihan', 'biaya', 'vendor', 'jadwal', 'evaluasi', 'sertifikat', 'lokasi', 'peserta']
            is_out_of_scope = False
            
            # 3. Check FAQ Match
            faq_match = AiFaq.objects.filter(question__iexact=message.strip(), is_published=True).first()
            
            ai_response = ""
            faq_obj = None
            is_faq = False
            is_unanswered = False
            redirected_to_wa = False
            intent = "unknown" # Match DB constraint (using more generic value)
            tokens_used = 0

            if faq_match:
                ai_response = faq_match.answer
                faq_obj = faq_match
                is_faq = True
                intent = "unknown"
            else:
                # 4. Gather Context and Call n8n
                context = self.get_ai_context(request.user, user_role, message)
                n8n_url = "http://localhost:5678/webhook/smi-ai-chat"
                history = request.data.get('history', [])
                payload = {
                    "message": message,
                    "role": user_role,
                    "nik": str(employee_nik) if employee_nik else None,
                    "division_id": division_id,
                    "context": context,
                    "history": history
                }
                
                try:
                    n8n_res = requests.post(n8n_url, json=payload, timeout=60)
                    if n8n_res.status_code == 200:
                        try:
                            data = n8n_res.json()
                            ai_response = data.get('response', '')
                            if not ai_response or ai_response.strip() == '':
                                ai_response = 'Maaf, saya tidak dapat memproses permintaan tersebut. Silakan coba dengan pertanyaan yang lebih spesifik.'
                                is_unanswered = True
                            tokens_used = data.get('tokens_used', 0)
                            raw_intent = data.get('intent', 'unknown')
                            valid_intents = ['training_history', 'tna_status', 'training_cost', 'vendor_info', 'event_schedule', 'evaluation_result', 'employee_info', 'division_summary', 'out_of_scope', 'unknown']
                            intent = raw_intent if raw_intent in valid_intents else 'unknown'
                        except:
                            ai_response = n8n_res.text if n8n_res.text else "Respon AI kosong."
                    else:
                        ai_response = "Maaf, sistem AI sedang sibuk. Silakan coba lagi nanti."
                        is_unanswered = True
                except Exception as e:
                    print(f"n8n Connection Error: {str(e)}")
                    ai_response = "Maaf, terjadi kendala koneksi ke sistem AI."
                    is_unanswered = True

            # 5. Save Chat Log
            response_time = int((time.time() - start_time) * 1000)
            
            # Set intent to None for AI Query to avoid DB constraint issues
            # Only use intent if it's a known FAQ or Out of Scope match, otherwise None is safer
            valid_intents = ['training_history', 'tna_status', 'training_cost', 'vendor_info', 'event_schedule', 'evaluation_result', 'employee_info', 'division_summary', 'out_of_scope', 'unknown']
            final_intent = intent if intent in valid_intents else None

            AiChatLog.objects.create(
                session=session,
                user=request.user,
                nik=employee_nik,
                role=user_role,
                user_message=message,
                ai_response=ai_response,
                intent=final_intent,
                faq=faq_obj,
                is_faq_triggered=is_faq,
                is_out_of_scope=is_out_of_scope,
                is_unanswered=is_unanswered,
                redirected_to_wa=redirected_to_wa,
                response_time_ms=response_time,
                tokens_used=tokens_used,
                context_sent=context
            )

            return Response({
                'response': ai_response,
                'is_faq': is_faq,
                'is_out_of_scope': is_out_of_scope,
                'redirected_to_wa': redirected_to_wa
            })

        except Exception as e:
            import traceback
            print("CHAT ACTION ERROR:")
            traceback.print_exc()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AiChatLogViewSet(viewsets.ModelViewSet):
    queryset = AiChatLog.objects.all()
    serializer_class = AiChatLogSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_chats = AiChatLog.objects.count()
        unanswered = AiChatLog.objects.filter(is_unanswered=True).count()
        wa_redirects = AiChatLog.objects.filter(redirected_to_wa=True).count()
        out_of_scope = AiChatLog.objects.filter(is_out_of_scope=True).count()
        faq_count = AiFaq.objects.count()

        return Response({
            'total_chats': total_chats,
            'unanswered': unanswered,
            'wa_redirects': wa_redirects,
            'out_of_scope': out_of_scope,
            'faq_count': faq_count
        })

    @action(detail=False, methods=['get'])
    def unanswered_logs(self, request):
        try:
            from django.db import connection
            # Check if is_unanswered column exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name='ai_chat_logs' AND column_name='is_unanswered'
                """)
                col_exists = cursor.fetchone()

            if not col_exists:
                return Response([])

            logs = AiChatLog.objects.filter(is_unanswered=True).select_related('session').order_by('-created_at')[:10]
            data = []
            for log in logs:
                try:
                    user = log.session.user if log.session else None
                    name = user.get_full_name() or user.username if user else 'N/A'
                    data.append({
                        'id': log.log_id,
                        'nik': 'N/A',
                        'name': name,
                        'division': 'N/A',
                        'message': log.user_message,
                        'date': log.created_at.strftime('%Y-%m-%d') if log.created_at else '',
                        'full_date': log.created_at.isoformat() if log.created_at else ''
                    })
                except Exception:
                    continue
            return Response(data)
        except Exception as e:
            return Response([], status=status.HTTP_200_OK)


class AiUnauthorizedAttemptViewSet(viewsets.ModelViewSet):
    queryset = AiUnauthorizedAttempt.objects.all()
    serializer_class = AiUnauthorizedAttemptSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


class ExportReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        status_filter = request.query_params.get('status', 'all')
        category_filter = request.query_params.get('category', 'all')
        employee_filter = request.query_params.get('employee')
        division_filter = request.query_params.get('division')
        type_filter = request.query_params.get('type', 'all')

        # Base queryset with RBAC
        user = request.user
        user_groups = list(user.groups.values_list('name', flat=True))

        qs = EventParticipant.objects.select_related(
            'event', 
            'event__training', 
            'event__training__course_category',
            'event__training__course',
            'event__training__vendor',
            'nik',
            'nik__division',
            'nik__division__directorate'
        ).prefetch_related('event__schedules').all()

        # Apply RBAC Scoping
        if user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            if employee_filter:
                qs = qs.filter(nik_id=employee_filter)
            if division_filter:
                qs = qs.filter(nik__division__division_name=division_filter)
        elif "Head of Division" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(nik__division_id=user.profile.employee.division_id)
            else:
                qs = qs.none()
        elif "Employee" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(nik=user.profile.employee)
            else:
                qs = qs.none()
        else:
            qs = qs.none()

        # Exclude Absent participants and Cancelled training events as requested
        qs = qs.exclude(attendance_status='Absent')
        qs = qs.exclude(event__status__iexact='cancelled')

        if start_date:
            qs = qs.filter(event__start_date__gte=start_date)
        if end_date:
            qs = qs.filter(event__end_date__lte=end_date)
        if status_filter != 'all':
            qs = qs.filter(event__status__iexact=status_filter)
        if category_filter != 'all':
            qs = qs.filter(event__training__training_category=category_filter)
        if type_filter != 'all':
            qs = qs.filter(event__training__training_type=type_filter)

        # Pre-fetch TNA for fulfillment check
        emp_ids = [ep.nik_id for ep in qs]
        tna_set = set(TnaParticipant.objects.filter(nik_id__in=emp_ids).values_list('nik_id', 'tna__course_id'))

        from datetime import datetime, date
        data_slide1 = []
        for ep in qs:
            event = ep.event
            training = event.training
            emp = ep.nik
            
            # Hours calculation
            event_hours = 0
            for sch in event.schedules.all():
                if sch.start_time and sch.end_time:
                    dummy_date = date(2000, 1, 1)
                    t1 = datetime.combine(dummy_date, sch.start_time)
                    t2 = datetime.combine(dummy_date, sch.end_time)
                    event_hours += (t2 - t1).total_seconds() / 3600
            
            days = (event.end_date - event.start_date).days + 1 if event.start_date and event.end_date else 0
            
            # YearMonth calculation (e.g., 20264 for April 2026)
            year_month = ""
            if event.start_date:
                year_month = f"{event.start_date.year}{event.start_date.month}"

            # TNA Fulfillment
            tna_fulfillment = 0
            if training.course_id and (emp.nik, training.course_id) in tna_set:
                tna_fulfillment = 1

            data_slide1.append({
                'course_category': training.course_category.category_name if training.course_category else '',
                'course_name': training.course.course_name if training.course else '',
                'training_title': training.training_title,
                'training_type': training.training_type,
                'training_category': training.training_category,
                'location': event.location.city if hasattr(event, 'location') else '',
                'hours': round(event_hours, 2),
                'start_date': event.start_date.strftime('%Y-%m-%d') if event.start_date else '',
                'end_date': event.end_date.strftime('%Y-%m-%d') if event.end_date else '',
                'duration_day': days,
                'vendor': training.vendor.vendor_name if training.vendor else '',
                'nik': emp.nik,
                'nama': emp.full_name,
                'divisi': emp.division.division_name if emp.division else '',
                'level': emp.level,
                'jabatan': emp.position_name,
                'direktorat': emp.division.directorate.directorate_name if emp.division and emp.division.directorate else '',
                'gender': emp.gender,
                'l1': ep.l1_score,
                'l2': ep.l2_score,
                'year_month': year_month,
                'tna_fulfillment': tna_fulfillment
            })

        # Total Employees count
        total_employees = Employee.objects.count()

        return Response({
            'realisasi_training': data_slide1,
            'total_employees': total_employees
        })

