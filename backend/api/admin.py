from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import (
    Employee, Profile, Directorate, Division, 
    CourseCategory, Course, Hotel, Vendor, TnaPeriod, TnaMaster,
    TrainingMaster, TrainingEvent, EventLocation, EventSchedule,
    EventParticipant, EventCost, EventDocument, AiAdminConfig, AiFaq, AiChatSession, AiChatLog, AiUnauthorizedAttempt
)

@admin.register(AiAdminConfig)
class AiAdminConfigAdmin(admin.ModelAdmin):
    list_display = ('config_key', 'config_value', 'updated_at')

@admin.register(AiFaq)
class AiFaqAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_published', 'sequence', 'created_at')

@admin.register(AiChatSession)
class AiChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'role', 'session_start')

@admin.register(AiChatLog)
class AiChatLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'session', 'user_message', 'created_at')

@admin.register(AiUnauthorizedAttempt)
class AiUnauthorizedAttemptAdmin(admin.ModelAdmin):
    list_display = ('attempt_id', 'log', 'user', 'attempted_access', 'role', 'created_at')

@admin.register(TrainingMaster)
class TrainingMasterAdmin(admin.ModelAdmin):
    list_display = ('training_code', 'training_title', 'training_type', 'training_category', 'pic', 'is_active')
    search_fields = ('training_code', 'training_title')
    list_filter = ('training_type', 'training_category', 'is_active')

@admin.register(TrainingEvent)
class TrainingEventAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'training', 'training_topic', 'start_date', 'end_date', 'status')
    search_fields = ('training_topic', 'training__training_title')
    list_filter = ('status',)

@admin.register(EventLocation)
class EventLocationAdmin(admin.ModelAdmin):
    list_display = ('event_location_id', 'event', 'city', 'venue', 'room', 'address')

@admin.register(EventSchedule)
class EventScheduleAdmin(admin.ModelAdmin):
    list_display = ('event', 'training_date', 'start_time', 'end_time', 'instructor_name')
    list_filter = ('training_date',)

@admin.register(EventParticipant)
class EventParticipantAdmin(admin.ModelAdmin):
    list_display = ('event', 'nik', 'attendance_status', 'l1_score', 'l2_score')
    search_fields = ('nik__full_name', 'nik__nik')
    list_filter = ('attendance_status',)

@admin.register(EventCost)
class EventCostAdmin(admin.ModelAdmin):
    list_display = ('event', 'cost_center', 'cost_type', 'currency', 'room_cost', 'training_cost', 'sppd_cost', 'status_cost')
    list_filter = ('cost_type', 'status_cost', 'currency')

@admin.register(EventDocument)
class EventDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_id', 'event', 'document_type', 'file_name', 'uploaded_by', 'uploaded_at')
    search_fields = ('file_name', 'document_type')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'User Profiles'

class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'get_nik', 'is_staff')

    def get_nik(self, obj):
        return obj.profile.employee.nik if hasattr(obj, 'profile') else "-"
    get_nik.short_description = 'NIK'

@admin.register(Directorate)
class DirectorateAdmin(admin.ModelAdmin):
    list_display = ('directorate_id', 'directorate_name', 'is_active')
    search_fields = ('directorate_id', 'directorate_name')

@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ('division_id', 'division_name', 'directorate', 'is_active')
    search_fields = ('division_id', 'division_name')
    list_filter = ('directorate',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('nik', 'full_name', 'email', 'division', 'position_name')
    search_fields = ('nik', 'full_name', 'email')
    list_filter = ('division', 'employment_status')

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('course_category_id', 'category_name', 'is_active')
    search_fields = ('course_category_id', 'category_name')

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'course_category', 'is_active')
    search_fields = ('course_id', 'course_name')
    list_filter = ('course_category',)

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('hotel_id', 'hotel_name', 'hotel_city', 'hotel_star', 'price_estimation')
    search_fields = ('hotel_id', 'hotel_name', 'hotel_city')
    list_filter = ('hotel_city', 'hotel_star')

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('vendor_id', 'vendor_name', 'city', 'speciality', 'is_active')
    search_fields = ('vendor_id', 'vendor_name', 'speciality', 'city')
    list_filter = ('is_active', 'city', 'provider_type')

@admin.register(TnaPeriod)
class TnaPeriodAdmin(admin.ModelAdmin):
    list_display = ('tna_period_id', 'period_code', 'year', 'status')
    search_fields = ('period_code', 'period_name')
    list_filter = ('status', 'year')

@admin.register(TnaMaster)
class TnaMasterAdmin(admin.ModelAdmin):
    list_display = ('tna_id', 'tna_period', 'course', 'group_name', 'created_by')
    search_fields = ('tna_id', 'course__course_name')
    list_filter = ('tna_period', 'group_name')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)