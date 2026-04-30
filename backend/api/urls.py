from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    MyTokenObtainPairView, UserViewSet,
    EmployeeViewSet, CourseCategoryViewSet, CourseViewSet,
    VendorViewSet, TnaPeriodViewSet, TnaMasterViewSet,
    TnaParticipantViewSet, HotelViewSet,
    TrainingMasterViewSet, TrainingEventViewSet, EventLocationViewSet,
    EventScheduleViewSet, EventParticipantViewSet, EventCostViewSet,
    EventDocumentViewSet, AddTrainingView, DivisionViewSet, ExportReportView
)
from .dashboard_views import DashboardCardsAPIView
from .dashboard_admin_views import DashboardAdminAPIView

# DRF Router
router = DefaultRouter()

router.register(r'users', UserViewSet, basename='users')
router.register(r'employee', EmployeeViewSet, basename='employee')
router.register(r'divisions', DivisionViewSet, basename='divisions')
router.register(r'course-categories', CourseCategoryViewSet, basename='course-categories')
router.register(r'courses', CourseViewSet, basename='courses')
router.register(r'vendors', VendorViewSet, basename='vendors')
router.register(r'tna-period', TnaPeriodViewSet, basename='tna-period')
router.register(r'tna-master', TnaMasterViewSet, basename='tna-master')
router.register(r'tna-participant', TnaParticipantViewSet, basename='tna-participant')
router.register(r'hotels', HotelViewSet, basename='hotels')


router.register(r'training-master', TrainingMasterViewSet, basename='training-master')
router.register(r'training-events', TrainingEventViewSet, basename='training-events')
router.register(r'event-locations', EventLocationViewSet, basename='event-locations')
router.register(r'event-schedules', EventScheduleViewSet, basename='event-schedules')
router.register(r'event-participants', EventParticipantViewSet, basename='event-participants')
router.register(r'event-costs', EventCostViewSet, basename='event-costs')
router.register(r'event-documents', EventDocumentViewSet, basename='event-documents')

# Evaluation Viewsets
from .views import (
    EvaluationFormViewSet, EvaluationQuestionViewSet,
    EvaluationQuestionOptionViewSet, EvaluationAnswerViewSet,
    EvaluationResultViewSet, AiAdminConfigViewSet, AiFaqViewSet, 
    AiChatSessionViewSet, AiChatLogViewSet, AiUnauthorizedAttemptViewSet
)
router.register(r'evaluation-forms', EvaluationFormViewSet, basename='evaluation-forms')
router.register(r'evaluation-questions', EvaluationQuestionViewSet, basename='evaluation-questions')
router.register(r'evaluation-question-options', EvaluationQuestionOptionViewSet, basename='evaluation-options')
router.register(r'evaluation-answers', EvaluationAnswerViewSet, basename='evaluation-answers')
router.register(r'evaluation-results', EvaluationResultViewSet, basename='evaluation-results')

# AI Assistant Endpoints
router.register(r'ai-admin-config', AiAdminConfigViewSet, basename='ai-admin-config')
router.register(r'ai-faq', AiFaqViewSet, basename='ai-faq')
router.register(r'ai-sessions', AiChatSessionViewSet, basename='ai-sessions')
router.register(r'ai-logs', AiChatLogViewSet, basename='ai-logs')
router.register(r'ai-unauthorized', AiUnauthorizedAttemptViewSet, basename='ai-unauthorized')

urlpatterns = [
    # Auth endpoints
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('add-training/', AddTrainingView.as_view(), name='add-training'),
    path('add-training/<int:pk>/', AddTrainingView.as_view(), name='add-training-detail'),
    path('export-report/', ExportReportView.as_view(), name='export-report'),
    path('dashboard/cards/', DashboardCardsAPIView.as_view(), name='dashboard-cards'),
    path('dashboard/admin/', DashboardAdminAPIView.as_view(), name='dashboard-admin'),

    
    path('', include(router.urls)),
]