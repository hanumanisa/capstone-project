import requests
import time
import json
import os
import re
from django.utils import timezone
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Count, Sum, Case, When, F
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
    EvaluationAnswer, EvaluationResult, Profile,
    AiAdminConfig, AiChatSession, AiChatLog, AiUnauthorizedAttempt,
    Budget
)
from .serializers import (
    UserSerializer, MyTokenObtainPairSerializer,
    EmployeeSerializer, EmployeeMinimalSerializer, CourseCategorySerializer, CourseSerializer,
    VendorSerializer, TnaPeriodSerializer, TnaMasterSerializer,
    TnaParticipantSerializer, HotelSerializer,
    TrainingMasterSerializer, TrainingEventSerializer, EventLocationSerializer,
    EventScheduleSerializer, EventParticipantSerializer, EventCostSerializer,
    EventDocumentSerializer, DivisionSerializer, EvaluationFormSerializer, EvaluationQuestionSerializer,
    EvaluationQuestionOptionSerializer, EvaluationAnswerSerializer,
    EvaluationResultSerializer,
    AiAdminConfigSerializer, AiChatSessionSerializer, 
    AiChatLogSerializer, AiUnauthorizedAttemptSerializer,
    BudgetSerializer
)



# Custom Permission
class IsSuperAdmin(permissions.BasePermission):
    """
    Hanya mengizinkan Super Administrator untuk endopint autentikasi
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
        return 'Administrator' in user_groups or 'Super Administrator' in user_groups


class BudgetViewSet(viewsets.ModelViewSet):
    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        qs = Budget.objects.all().order_by('-start_date_budget')
        year = self.request.query_params.get('year', None)
        if year:
            qs = qs.filter(start_date_budget__year=year)
        return qs


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
        qs = CourseCategory.objects.all().order_by('course_category_id')
        year = self.request.query_params.get('year', None)
        if year:
            qs = qs.filter(created_at__year=year)
        return qs


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
        year = self.request.query_params.get('year', None)
        if category_id:
            qs = qs.filter(course_category_id=category_id)
        if year:
            qs = qs.filter(created_at__year=year)
        return qs


class VendorViewSet(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by('vendor_name')
    serializer_class = VendorSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['vendor_id', 'vendor_name', 'speciality', 'city', 'pic_name', 'provider_type', 'province']

    def get_queryset(self):
        qs = Vendor.objects.all().order_by('vendor_name')
        year = self.request.query_params.get('year', None)
        if year:
            qs = qs.filter(created_at__year=year)
        return qs


class TnaPeriodViewSet(viewsets.ModelViewSet):
    queryset = TnaPeriod.objects.all().order_by('-year', 'tna_period_id')
    serializer_class = TnaPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['period_code', 'period_name']

    def get_queryset(self):
        qs = TnaPeriod.objects.all().order_by('-year', 'tna_period_id')
        year = self.request.query_params.get('year', None)
        if year:
            qs = qs.filter(year=year)
        return qs


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

        view_mode = self.request.query_params.get('view_mode', 'admin')

        # RBAC Logic
        if view_mode == 'employee':
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(tnaparticipant__nik=user.profile.employee).distinct()
            else:
                return TnaMaster.objects.none()
        elif user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            pass
        elif "Head of Division" in user_groups or "Team Leader" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(tnaparticipant__nik__division_id=user.profile.employee.division_id).distinct()
            else:
                return TnaMaster.objects.none()
        else:
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(tnaparticipant__nik=user.profile.employee).distinct()
            else:
                return TnaMaster.objects.none()

        category_id = self.request.query_params.get('category', None)
        period_id = self.request.query_params.get('period', None)
        course_id = self.request.query_params.get('course', None)
        group_name = self.request.query_params.get('group_name', None)
        year = self.request.query_params.get('year', None)

        if category_id:
            qs = qs.filter(course_category_id=category_id)
        if period_id:
            qs = qs.filter(tna_period_id=period_id)
        if course_id:
            qs = qs.filter(course_id=course_id)
        if group_name:
            qs = qs.filter(group_name=group_name)
        if year:
            qs = qs.filter(tna_period__year=year)
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
            'tna__course_category', 'tna__course', 'tna__tna_period', 'nik__division'
        ).prefetch_related(
            'nik__eventparticipant_set__event__training',
            'nik__eventparticipant_set__event__schedules',
            'nik__tnaparticipant_set__tna__course'
        ).order_by('tna__course_category__category_name', 'tna__course__course_name')

        view_mode = self.request.query_params.get('view_mode', 'admin')

        # RBAC Logic
        if view_mode == 'employee':
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(nik=user.profile.employee)
            else:
                return TnaParticipant.objects.none()
        elif user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            pass
        elif "Head of Division" in user_groups or "Team Leader" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(nik__division_id=user.profile.employee.division_id)
            else:
                return TnaParticipant.objects.none()
        else:
            if hasattr(user, 'profile') and user.profile.employee:
                qs = qs.filter(nik=user.profile.employee)
            else:
                return TnaParticipant.objects.none()

        tna_id = self.request.query_params.get('tna_id', None)
        period_id = self.request.query_params.get('period', None)
        course_id = self.request.query_params.get('course', None)
        course_name = self.request.query_params.get('course_name', None)
        division = self.request.query_params.get('division', None)
        group_name = self.request.query_params.get('group_name', None)
        year = self.request.query_params.get('year', None)

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
        if year:
            qs = qs.filter(tna__tna_period__year=year)
        return qs


class HotelViewSet(viewsets.ModelViewSet):
    """
    Super Administrator & Administrator → full CRUD, yang lain read-only
    """
    queryset = Hotel.objects.all().order_by('hotel_id')
    serializer_class = HotelSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['hotel_id', 'hotel_name', 'hotel_city']


class EmployeeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user = self.request.user
        user_groups = list(user.groups.values_list('name', flat=True))

        queryset = Employee.objects.all().select_related(
            'division'
        ).prefetch_related(
            'eventparticipant_set__event__training',
            'eventparticipant_set__event__schedules',
            'tnaparticipant_set__tna__course',
            'profile_set__user__groups'
        ).order_by('nik')
        
        view_mode = self.request.query_params.get('view_mode', 'admin')
        
        # RBAC Logic
        if view_mode == 'employee':
            if hasattr(user, 'profile') and user.profile.employee:
                queryset = queryset.filter(nik=user.profile.employee.nik)
            else:
                return Employee.objects.none()
        elif user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            division = self.request.query_params.get('division')
            if division:
                queryset = queryset.filter(division__division_name__icontains=division)
        elif "Head of Division" in user_groups or "Team Leader" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                queryset = queryset.filter(division_id=user.profile.employee.division_id)
            else:
                return Employee.objects.none()
        else:
            if hasattr(user, 'profile') and user.profile.employee:
                queryset = queryset.filter(nik=user.profile.employee.nik)
            else:
                return Employee.objects.none()
            
        return queryset

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('nopage') == 'true':
            return None
        return super().paginate_queryset(queryset)
    
    def get_serializer_class(self):
        if self.request.query_params.get('nopage') == 'true' and self.request.query_params.get('report') != 'true':
            return EmployeeMinimalSerializer
        return EmployeeSerializer

    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['nik', 'full_name', 'division__division_name', 'level', 'position_name']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['year'] = self.request.query_params.get('year')
        context['start_date'] = self.request.query_params.get('start_date')
        context['end_date'] = self.request.query_params.get('end_date')
        context['status'] = self.request.query_params.get('status')
        context['category'] = self.request.query_params.get('category')
        context['type'] = self.request.query_params.get('type')
        return context


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
        
        view_mode = self.request.query_params.get('view_mode', 'admin')

        # If purely an Employee role, force employee mode to avoid race conditions/incorrect views
        is_employee_user = "Employee" in user_groups and not any(r in user_groups for r in ['Super Administrator', 'Administrator', 'Dean', 'Head of Division', 'Team Leader'])
        if is_employee_user:
            view_mode = 'employee'

        if view_mode == 'employee':
            if hasattr(user, 'profile') and user.profile.employee:
                emp = user.profile.employee
                active_events = TrainingEvent.objects.filter(
                    participants__nik=emp,
                    participants__attendance_status='Present',
                    status='completed'
                )
                qs = qs.filter(trainingevent__in=active_events).distinct()
            else:
                qs = qs.none()
        elif user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            # Apply standard filters
            division_filter = self.request.query_params.get('division')
            month_filter = self.request.query_params.get('month')
            year_filter = self.request.query_params.get('year')
            
            if division_filter:
                qs = qs.filter(trainingevent__participants__nik__division_id=division_filter).distinct()
            if month_filter:
                try:
                    m = int(month_filter)
                    qs = qs.filter(trainingevent__start_date__month=m).distinct()
                except (ValueError, TypeError):
                    pass
            if year_filter:
                qs = qs.filter(trainingevent__start_date__year=year_filter).distinct()
        elif "Head of Division" in user_groups or "Team Leader" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                div_id = user.profile.employee.division_id
                # Only show trainings that have at least one valid participant from their division
                # who is Present, and the event is not cancelled
                active_events = TrainingEvent.objects.filter(
                    participants__nik__division_id=div_id,
                    participants__attendance_status='Present'
                ).exclude(status='cancelled')
                qs = qs.filter(trainingevent__in=active_events).distinct()
            else:
                qs = qs.none()
        elif "Employee" in user_groups:
            if hasattr(user, 'profile') and user.profile.employee:
                emp = user.profile.employee
                # Only show trainings that they participated in and were completed/Present
                active_events = TrainingEvent.objects.filter(
                    participants__nik=emp,
                    participants__attendance_status='Present',
                    status='completed'
                )
                qs = qs.filter(trainingevent__in=active_events).distinct()
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
                    l1_val = part.get('l1')
                    l2_val = part.get('l2')

                    # Cap L1 at 4.0
                    if l1_val is not None and l1_val != "":
                        try:
                            if float(l1_val) > 4: l1_val = 4.0
                        except: pass

                    # Cap L2 at 4.0
                    if l2_val is not None and l2_val != "":
                        try:
                            if float(l2_val) > 4: l2_val = 4.0
                        except: pass

                    # Check for conflicts
                    conflicts = EventParticipant.objects.filter(
                        nik_id=part.get('employee'),
                        event__start_date__lte=event.end_date,
                        event__end_date__gte=event.start_date
                    )
                    if conflicts.exists():
                        conflict_event = conflicts.first().event
                        raise Exception(f"Employee {part.get('employee')} already registered for other training: {conflict_event.training_topic}")

                    EventParticipant.objects.create(
                        event=event,
                        nik_id=part.get('employee'),
                        l1_score=l1_val if l1_val != "" else None,
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
                    # Fallback to current user NIK if submitted_by is missing
                    uploader_id = doc.get('submitted_by')
                    if not uploader_id:
                        if hasattr(request.user, 'profile') and request.user.profile.employee:
                            uploader_id = request.user.profile.employee.nik
                        else:
                            # Final fallback to one of the known NIKs if still missing
                            uploader_id = 200335 

                    EventDocument.objects.create(
                        event=event,
                        document_type=doc.get('type') or 'Other',
                        file_name=doc.get('file_name') or 'Untitled',
                        file_url=doc.get('url'),
                        uploaded_by_id=uploader_id
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

            # For simplicity, update the LATEST event or create one if none exists
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

            # Update Participants (Smart Sync)
            new_participants_data = data.get('participants', [])
            existing_participants = {p.nik_id: p for p in event.participants.all()}
            processed_niks = set()
            
            for part in new_participants_data:
                if part.get('employee'):
                    nik = int(part.get('employee'))
                    if nik in processed_niks:
                        continue # Skip duplicates in payload
                    processed_niks.add(nik)

                    l1_val = part.get('l1')
                    l2_val = part.get('l2')
                    att_status = part.get('attendance', 'Present')

                    # Cap scores at 4.0
                    try:
                        if l1_val and l1_val != "" and float(l1_val) > 4: l1_val = 4.0
                        if l2_val and l2_val != "" and float(l2_val) > 4: l2_val = 4.0
                    except: pass

                    if nik in existing_participants:
                        # Update existing
                        p_obj = existing_participants[nik]
                        p_obj.attendance_status = att_status
                        p_obj.l1_score = l1_val if l1_val != "" else None
                        p_obj.l2_score = l2_val if l2_val != "" else None
                        p_obj.save()
                        del existing_participants[nik]
                    else:
                        # Create new
                        EventParticipant.objects.create(
                            event=event,
                            nik_id=nik,
                            attendance_status=att_status,
                            l1_score=l1_val if l1_val != "" else None,
                            l2_score=l2_val if l2_val != "" else None
                        )

            # Delete participants that are no longer in the list
            for p_to_del in existing_participants.values():
                p_to_del.delete()

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
                    # Fallback to current user NIK if submitted_by is missing
                    uploader_id = doc.get('submitted_by')
                    if not uploader_id:
                        if hasattr(request.user, 'profile') and request.user.profile.employee:
                            uploader_id = request.user.profile.employee.nik
                        else:
                            # Final fallback to one of the known NIKs if still missing
                            uploader_id = 200335 

                    EventDocument.objects.create(
                        event=event,
                        document_type=doc.get('type') or 'Other',
                        file_name=doc.get('file_name') or 'Untitled',
                        file_url=doc.get('url'),
                        uploaded_by_id=uploader_id
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

# Evaluation ViewSets 

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

        # Update questions intelligently to avoid wiping existing responses
        if 'questions' in data:
            now = timezone.now()
            questions_data = data.get('questions', [])
            existing_questions = {q.sequence: q for q in form.questions.all()}
            
            for seq_idx, q_data in enumerate(questions_data):
                sequence = seq_idx + 1
                question_text = q_data.get('question_text', '')
                question_type = q_data.get('question_type', 'Rating Scale')
                evaluation_type = q_data.get('evaluation_type', form.form_type)
                is_required = q_data.get('is_required', True)
                score = q_data.get('score')
                
                if sequence in existing_questions:
                    # Update existing question
                    question = existing_questions[sequence]
                    question.question_text = question_text
                    question.question_type = question_type
                    question.evaluation_type = evaluation_type
                    question.is_required = is_required
                    question.score = score
                    question.save()
                    # Remove from map so we know it's handled
                    del existing_questions[sequence]
                else:
                    # Create new question
                    question = EvaluationQuestion.objects.create(
                        form=form,
                        question_text=question_text,
                        question_type=question_type,
                        evaluation_type=evaluation_type,
                        sequence=sequence,
                        is_required=is_required,
                        score=score,
                        is_active=True,
                        created_by=request.user,
                        created_at=now
                    )

                # Sync options for the question
                options_data = q_data.get('options', [])
                # Wipe old options for THIS question is safer since they don't have direct answer links 
                # (answers link to question, not option, in most models, but EvaluationAnswer has selected_option)
                # Wait, if EvaluationAnswer has selected_option, wiping options will SET NULL or CASCADE.
                # Let's check models.py again.
                # EvaluationAnswer.selected_option is models.SET_NULL. So it's safe to recreate options.
                question.options.all().delete()
                for opt_idx, opt_data in enumerate(options_data):
                    EvaluationQuestionOption.objects.create(
                        question=question,
                        option_text=opt_data.get('option_text', ''),
                        sequence=opt_idx + 1,
                        is_correct=opt_data.get('is_correct', False),
                        is_active=True
                    )
            
            # Any remaining questions in existing_questions were removed in the new data
            # We mark them as inactive instead of deleting to preserve historical answers
            for q in existing_questions.values():
                q.is_active = False
                q.save()

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
            
        year = request.query_params.get('year')
        participants = EventParticipant.objects.filter(
            nik=employee, 
            event__enable_course_access=True
        ).select_related('event')
        if year:
            participants = participants.filter(event__start_date__year=year)
        
        result = []
        for p in participants:
            event = p.event
            # Get active forms for this specific training
            forms = EvaluationForm.objects.filter(
                training_master_id=event.training_id, 
                is_active=True
            ).prefetch_related('questions', 'questions__options')
            
            for form in forms:
                # Type is '[L1] ...'
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
        
        # Check permission: Only Admin and Dean can see respondents
        is_admin = request.user.is_superuser or request.user.groups.filter(name__in=['Super Administrator', 'Administrator', 'Dean']).exists()
        if not is_admin:
            return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

        # Get unique users who have submitted answers for this form
        submitted_user_ids = EvaluationAnswer.objects.filter(form=form).values_list('user_id', flat=True).distinct()

        # Use EvaluationResult as primary source (faster), fallback to direct query if missing
        result = []
        
        # Pre-fetch profiles and employees
        profiles = Profile.objects.filter(user_id__in=submitted_user_ids).select_related('employee', 'user')
        profile_map = {p.user_id: p for p in profiles}
        
        # Pre-fetch existing results summaries
        existing_results = EvaluationResult.objects.filter(form=form, user_id__in=submitted_user_ids)
        results_map = {res.user_id: res for res in existing_results}
        
        # Pre-fetch participant scores if needed
        participant_map = {}
        if form.training_master_id:
            participants = EventParticipant.objects.filter(
                event__training_id=form.training_master_id,
                nik_id__in=[p.employee_id for p in profiles if p.employee_id]
            )
            for p in participants:
                participant_map[p.nik_id] = p

        form_type = form.form_type or ('L2' if '[L2]' in (form.form_name or '') else 'L1')

        for user_id in submitted_user_ids:
            profile = profile_map.get(user_id)
            if not profile: continue
            
            res = results_map.get(user_id)
            
            nik_val = profile.employee.nik if profile.employee else 'N/A'
            name_val = profile.employee.full_name if profile.employee else (profile.user.get_full_name() or profile.user.username)
            
            # Use snapshot if available
            if res:
                if res.user_name: name_val = res.user_name
                score_val = float(res.score) if res.score is not None else 0.0
            else:
                # Fallback to EventParticipant score
                score_val = 0.0
                if profile.employee and profile.employee.nik in participant_map:
                    p = participant_map[profile.employee.nik]
                    score_val = float(p.l2_score if form_type == 'L2' else p.l1_score) if (p.l2_score if form_type == 'L2' else p.l1_score) is not None else 0.0
            
            result.append({
                'nik': nik_val,
                'name': name_val,
                'score': score_val
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

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
            
        user_groups = list(user.groups.values_list('name', flat=True))
        
        if user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            return qs
        
        # Head of Division, Team Leader, Employee only see their own results
        return qs.filter(user=user)

# AI Assistant ViewSets 

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name__in=['Super Administrator', 'Administrator', 'Dean']).exists()

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



class AiChatSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
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

        # Ambil info tambahan agar tidak null
        employee_nik = None
        division_id = None
        try:
            profile = getattr(user, 'profile', None)
            if profile and profile.employee:
                employee_nik = profile.employee.nik
                division_id = profile.employee.division_id
        except:
            pass

        # Ambil IP Address (mendukung proxy)
        ip_address = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if ip_address:
            ip_address = ip_address.split(',')[0].strip()
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')
            
        # Ambil User Agent
        user_agent = self.request.META.get('HTTP_USER_AGENT')

        serializer.save(
            user=user, 
            role=user_role,
            nik=employee_nik,
            division_id=division_id,
            ip_address=ip_address,
            user_agent=user_agent
        )

    @action(detail=True, methods=['post'])
    def chat(self, request, pk=None):
        start_time = time.time()
        try:
            session = self.get_object()
            message = request.data.get('message')
            if not message:
                return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

            # Get User Info
            user_role = 'employee'
            groups = list(request.user.groups.values_list('name', flat=True)) if request.user.groups.exists() else []
            if request.user.is_superuser or 'Super Administrator' in groups:
                user_role = 'superadmin'
            elif 'Administrator' in groups:
                user_role = 'admin'
            elif 'Dean' in groups:
                user_role = 'dean'
            elif 'Head of Division' in groups:
                user_role = 'head_of_division'
            elif 'Team Leader' in groups:
                user_role = 'team_leader'
            else:
                user_role = 'employee'

            employee_nik = None
            try:
                profile = getattr(request.user, 'profile', None)
                if profile and profile.employee:
                    employee_nik = profile.employee.nik
            except: pass

            # Intercept personal data queries
            msg_lower = message.lower()
            personal_keywords = ['data pribadi', 'email', 'telepon', 'nomor hp', 'no hp', 'alamat', 'nik', 'nomor telepon', 'no telepon', 'phone number', 'email address', 'home address']
            if any(k in msg_lower for k in personal_keywords):
                ai_response = "Data pribadi hanya diketahui oleh HRD."
                AiChatLog.objects.create(
                    session=session, user=request.user, nik=employee_nik, role=user_role,
                    user_message=message, ai_response=ai_response, is_faq_triggered=False,
                    is_unanswered=False, response_time_ms=int((time.time() - start_time) * 1000),
                    tokens_used=0, context_sent="PERSONAL_DATA_BLOCKED", is_out_of_scope=False
                )
                return Response({'response': ai_response, 'is_faq': False})

            # Call LangGraph Agent
            from api.ai_agent import execute_ai_query
            history_data = request.data.get('history', [])

            stream_requested = request.query_params.get('stream', 'false').lower() == 'true' or request.data.get('stream') == True
            if stream_requested:
                from api.ai_agent import execute_ai_query_stream
                from django.http import StreamingHttpResponse
                import json
                
                def event_stream():
                    ai_response_text = ""
                    tokens_used = 0
                    is_unanswered = False
                    is_out_of_scope = False
                    redirected_to_wa = False
                    
                    try:
                        for chunk_json in execute_ai_query_stream(request.user, message, history_data):
                            if not chunk_json.strip(): continue
                            chunk_data = json.loads(chunk_json.strip())
                            if chunk_data.get("done"):
                                ai_response_text = chunk_data.get("full_response", "")
                                tokens_used = chunk_data.get("tokens_used", 0)
                                yield chunk_json
                                break
                            elif chunk_data.get("error"):
                                ai_response_text = "Maaf, SMI Assistant saat ini belum memiliki datanya dan hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D)."
                                if user_role not in ['superadmin', 'admin']:
                                    ai_response_text += " Jika ada pertanyaan lain, Anda bisa menghubungi Admin melalui whatsapp."
                                is_unanswered = True
                                yield chunk_json
                                break
                            else:
                                yield chunk_json
                    except Exception as e:
                        print(f"Streaming Error: {e}")
                        is_unanswered = True
                        ai_response_text = "Maaf, terjadi kendala."
                        yield json.dumps({"error": str(e)}) + "\n\n"
                    
                    # Determine flags
                    if "SMI Assistant hanya dapat menjawab pertanyaan" in ai_response_text:
                        is_unanswered = True
                        if "Silakan ajukan pertanyaan seputar pelatihan" in ai_response_text:
                            is_out_of_scope = True
                    elif "SMI Assistant saat ini belum memiliki datanya" in ai_response_text:
                        is_unanswered = True
                        if "menghubungi Admin melalui whatsapp" in ai_response_text:
                            redirected_to_wa = True

                    # Save Log
                    AiChatLog.objects.create(
                        session=session, user=request.user, nik=employee_nik, role=user_role,
                        user_message=message, ai_response=ai_response_text, is_faq_triggered=False,
                        is_unanswered=is_unanswered, is_out_of_scope=is_out_of_scope,
                        redirected_to_wa=redirected_to_wa,
                        response_time_ms=int((time.time() - start_time) * 1000),
                        tokens_used=tokens_used, context_sent="LangGraph React Agent Stream"
                    )
                
                return StreamingHttpResponse(event_stream(), content_type='text/event-stream')
            
            try:
                ai_response, tokens_used = execute_ai_query(request.user, message, history_data)
                is_unanswered = False
            except Exception as agent_err:
                print(f"Agent Execution Error: {agent_err}")
                if user_role in ['superadmin', 'admin']:
                    ai_response = "Maaf, SMI Assistant saat ini belum memiliki datanya dan hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D)."
                else:
                    ai_response = "Maaf, SMI Assistant saat ini belum memiliki datanya dan hanya dapat menjawab pertanyaan yang berkaitan dengan sistem manajemen pelatihan (L&D). Jika ada pertanyaan lain, Anda bisa menghubungi Admin melalui whatsapp."
                is_unanswered = True
                tokens_used = 0

            # Determine out_of_scope, unanswered and wa_redirect flags
            is_out_of_scope = False
            redirected_to_wa = False
            
            if "SMI Assistant hanya dapat menjawab pertanyaan" in ai_response:
                is_unanswered = True
                if "Silakan ajukan pertanyaan seputar pelatihan" in ai_response:
                    is_out_of_scope = True
            elif "SMI Assistant saat ini belum memiliki datanya" in ai_response:
                is_unanswered = True
                if "menghubungi Admin melalui whatsapp" in ai_response:
                    redirected_to_wa = True


            # Log execution
            AiChatLog.objects.create(
                session=session, user=request.user, nik=employee_nik, role=user_role,
                user_message=message, ai_response=ai_response, is_faq_triggered=False,
                is_unanswered=is_unanswered, is_out_of_scope=is_out_of_scope,
                redirected_to_wa=redirected_to_wa,
                response_time_ms=int((time.time() - start_time) * 1000),
                tokens_used=tokens_used, context_sent="LangGraph React Agent"
            )

            return Response({'response': ai_response, 'is_faq': False})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
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


        return Response({
            'total_chats': total_chats,
            'unanswered': unanswered,
            'wa_redirects': wa_redirects,
            'out_of_scope': out_of_scope
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
                    name = 'User'
                    nik_val = str(log.nik) if log.nik else ''
                    div_name = ''
                    
                    if log.nik:
                        emp = Employee.objects.filter(nik=log.nik).select_related('division').first()
                        if emp:
                            name = emp.full_name
                            div_name = emp.division.division_name if emp.division else ''
                    
                    if name == 'User' and log.user:
                        name = log.user.get_full_name() or log.user.username

                    data.append({
                        'id': log.log_id,
                        'nik': nik_val,
                        'name': name,
                        'division': div_name,
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
        if user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups or "Super Administrator" in user_groups:
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

        # Exclude Absent participants and Cancelled training events 
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
        event_hours_cache = {}
        
        for ep in qs:
            event = ep.event
            training = event.training
            emp = ep.nik
            
            # Hours calculation with caching
            if event.event_id not in event_hours_cache:
                event_hours = 0
                for sch in event.schedules.all():
                    if sch.start_time and sch.end_time:
                        dummy_date = date(2000, 1, 1)
                        t1 = datetime.combine(dummy_date, sch.start_time)
                        t2 = datetime.combine(dummy_date, sch.end_time)
                        event_hours += (t2 - t1).total_seconds() / 3600
                event_hours_cache[event.event_id] = event_hours
            
            event_hours = event_hours_cache[event.event_id]
            
            days = (event.end_date - event.start_date).days + 1 if event.start_date and event.end_date else 0
            
            # YearMonth calculation 
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

class CheckTrainingCodeView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        code = request.query_params.get('code')
        exclude_id = request.query_params.get('exclude_id')
        if not code:
            return Response({"exists": False})
        
        qs = TrainingMaster.objects.filter(training_code=code)
        if exclude_id:
            qs = qs.exclude(training_id=exclude_id)
            
        return Response({"exists": qs.exists()})

class CheckParticipantConflictView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        nik = request.query_params.get('nik')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        exclude_id = request.query_params.get('exclude_id') # training_id to exclude current latest event

        if not nik or not start_date or not end_date:
            return Response({"conflict": False})

        conflicts = EventParticipant.objects.filter(
            nik_id=nik,
            event__start_date__lte=end_date,
            event__end_date__gte=start_date
        )
        
        if exclude_id:
            conflicts = conflicts.exclude(event__training_id=exclude_id)

        if conflicts.exists():
            conflict_event = conflicts.first().event
            return Response({
                "conflict": True,
                "message": f"Employee already registered for other training: {conflict_event.training_topic} ({conflict_event.start_date} to {conflict_event.end_date})"
            })
        
        return Response({"conflict": False})

