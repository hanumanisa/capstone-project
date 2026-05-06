from datetime import datetime, date
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

class Directorate(models.Model):
    directorate_id = models.IntegerField(primary_key=True)
    directorate_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'directorates'

    def __str__(self):
        return f"{self.directorate_id} - {self.directorate_name}"


class Division(models.Model):
    division_id = models.CharField(max_length=11, primary_key=True)
    division_name = models.CharField(max_length=100)
    directorate = models.ForeignKey(
        Directorate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='directorate_id'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'divisions'

    def __str__(self):
        return f"{self.division_id} - {self.division_name}"


class Employee(models.Model):
    nik = models.BigAutoField(primary_key=True)
    full_name = models.CharField(max_length=100)
    division = models.ForeignKey(
        Division, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='division_id'
    )
    position_name = models.CharField(max_length=50, null=True, blank=True)
    direct_supervisor = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='direct_supervisor_nik'
    )
    special_position = models.CharField(max_length=100, null=True, blank=True)
    level = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    email = models.EmailField(max_length=50, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    university = models.CharField(max_length=100, null=True, blank=True)
    major = models.CharField(max_length=100, null=True, blank=True)
    entry_date = models.DateField(null=True, blank=True)
    employment_status = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'employees'

    def __str__(self):
        return f"{self.nik} - {self.full_name}"

    @property
    def attended_events(self):
        if hasattr(self, '_prefetched_events'):
            return self._prefetched_events
        events = list(self.eventparticipant_set.select_related('event', 'event__training').prefetch_related('event__schedules').all())
        self._prefetched_events = events
        return events

    @property
    def completed_events(self):
        return [
            ep for ep in self.attended_events
            if ep.event.status.lower() != 'cancelled' and ep.attendance_status != 'Absent'
        ]

    @property
    def training_stats(self):
        if hasattr(self, '_training_stats'):
            return self._training_stats
        
        stats = {
            'inhouse_count': 0, 'public_count': 0, 'ks_count': 0, 'elearning_count': 0,
            'inhouse_hours': 0, 'public_hours': 0, 'ks_hours': 0, 'elearning_hours': 0,
            'total_hours': 0
        }
        
        events = self.completed_events
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
            
        self._training_stats = stats
        return stats

    @property
    def iht_plus_public(self):
        stats = self.training_stats
        return stats['inhouse_count'] + stats['public_count']

    @property
    def tna_fulfilled(self):
        tna_list = self.tnaparticipant_set.all()
        if not tna_list:
            return 0
            
        events = self.completed_events
        attended_course_ids = set(ep.event.training.course_id for ep in events)
        fulfilled_count = 0
        for tp in tna_list:
            if tp.tna.course_id in attended_course_ids:
                fulfilled_count += 1
        return fulfilled_count

    @property
    def attendance(self):
        return len(self.completed_events)

    @property
    def total_hours(self):
        return round(self.training_stats['total_hours'], 2)


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column='nik'
    )

    class Meta:
        db_table = 'user_profiles'

    def __str__(self):
        return f"Profile: {self.user.username} → {self.employee.nik}"


class CourseCategory(models.Model):
    course_category_id = models.CharField(max_length=50, primary_key=True)
    category_name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'course_categories'

    def __str__(self):
        return f"{self.course_category_id} - {self.category_name}"


class Course(models.Model):
    course_id = models.CharField(max_length=50, primary_key=True)
    course_category = models.ForeignKey(
        CourseCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='course_category_id'
    )
    course_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'courses'

    def __str__(self):
        return f"{self.course_id} - {self.course_name}"


class Hotel(models.Model):
    hotel_id = models.CharField(max_length=10, primary_key=True)
    hotel_city = models.CharField(max_length=50, null=True, blank=True)
    hotel_name = models.CharField(max_length=100, null=True, blank=True)
    hotel_phone = models.CharField(max_length=50, null=True, blank=True)
    price_estimation = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    hotel_star = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'hotels'

    def __str__(self):
        return f"{self.hotel_id} - {self.hotel_name}"


class Vendor(models.Model):
    vendor_id = models.CharField(max_length=10, primary_key=True)
    vendor_name = models.CharField(max_length=50, null=True, blank=True)
    provider_type = models.CharField(max_length=50, null=True, blank=True)
    pic_name = models.CharField(max_length=100, null=True, blank=True)
    speciality = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    province = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    postcode = models.CharField(max_length=10, null=True, blank=True)
    phone = models.CharField(max_length=15, null=True, blank=True)
    fax = models.CharField(max_length=20, null=True, blank=True)
    email = models.CharField(max_length=50, null=True, blank=True)
    web_address = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'vendors'

    def __str__(self):
        return f"{self.vendor_id} - {self.vendor_name}"


class TnaPeriod(models.Model):
    tna_period_id = models.AutoField(primary_key=True)
    period_code = models.CharField(max_length=50, unique=True)
    year = models.IntegerField()
    period_name = models.CharField(max_length=50, null=True, blank=True)
    open_date = models.DateField(null=True, blank=True)
    close_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=[('Open', 'Open'), ('Closed', 'Closed')]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tna_period'

    def __str__(self):
        return f"{self.period_code} - {self.period_name}"


class TnaMaster(models.Model):
    tna_id = models.CharField(max_length=20, primary_key=True)
    tna_period = models.ForeignKey(
        TnaPeriod,
        on_delete=models.CASCADE,
        db_column='tna_period_id'
    )
    course_category = models.ForeignKey(
        CourseCategory,
        on_delete=models.CASCADE,
        db_column='course_category_id'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        db_column='course_id'
    )
    group_name = models.IntegerField()
    created_by = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column='created_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tna_master'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(group_name__gte=1) & models.Q(group_name__lte=6),
                name='tna_master_group_name_check_new'
            ),
        ]

    def __str__(self):
        return f"{self.tna_id} - {self.group_name}"


class TnaParticipant(models.Model):
    tna_participant_id = models.AutoField(primary_key=True)
    tna = models.ForeignKey(
        TnaMaster,
        on_delete=models.CASCADE,
        db_column='tna_id'
    )
    nik = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        db_column='nik'
    )

    class Meta:
        db_table = 'tna_participant'

    def __str__(self):
        return f"{self.tna_participant_id} - Participant {self.nik_id} for {self.tna_id}"





# ─── Signals Otomatisasi (Employee -> User & Profile) ────────────────────────

@receiver(post_save, sender=Employee)
def create_user_and_profile(sender, instance, created, **kwargs):
    """
    Otomatis membuat akun User dan menghubungkannya dengan Profile
    Group assignment berdasarkan position_name:
      - Kepala Divisi → Head of Division
      - Team Leader   → Team Leader
      - Staff / lainnya → Employee
    """
    if created:
        email_str = instance.email if instance.email else f"{instance.nik}@company.com"
        username_str = email_str
        password_str = str(instance.nik)
        
        user, user_created = User.objects.get_or_create(
            username=username_str,
            defaults={'email': email_str}
        )
        
        if user_created:
            user.set_password(password_str)
            user.save()
            
            POSITION_TO_GROUP = {
                'Kepala Divisi': 'Head of Division',
                'Team Leader': 'Team Leader',
            }
            group_name = POSITION_TO_GROUP.get(instance.position_name, 'Employee')
            
            try:
                target_group = Group.objects.get(name=group_name)
                user.groups.add(target_group)
            except Group.DoesNotExist:
                pass
                
        Profile.objects.get_or_create(
            user=user,
            employee=instance
        )


class TrainingMaster(models.Model):
    training_id = models.AutoField(primary_key=True)
    training_code = models.CharField(max_length=20, unique=True)
    course = models.ForeignKey(
        Course, 
        on_delete=models.CASCADE, 
        db_column='course_id'
    )
    course_category = models.ForeignKey(
        CourseCategory, 
        on_delete=models.CASCADE, 
        db_column='course_category_id'
    )
    training_type = models.CharField(
        max_length=25,
        choices=[
            ('Inhouse Training', 'Inhouse Training'),
            ('Public Training', 'Public Training'),
            ('E-Learning', 'E-Learning'),
            ('Knowledge Sharing', 'Knowledge Sharing'),
        ],
        null=True, blank=True
    )
    training_category = models.CharField(
        max_length=50,
        choices=[
            ('ESG', 'ESG'),
            ('Hard Skill', 'Hard Skill'),
            ('Soft Skill', 'Soft Skill'),
        ],
        null=True, blank=True
    )
    training_title = models.CharField(max_length=150, null=True, blank=True)
    training_description = models.TextField(null=True, blank=True)
    pic = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        db_column='pic_nik',
        related_name='managed_trainings'
    )
    vendor = models.ForeignKey(
        Vendor, 
        on_delete=models.CASCADE, 
        db_column='vendor_id'
    )
    estimated_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_master'

    def __str__(self):
        return f"{self.training_code} - {self.training_title}"


class TrainingEvent(models.Model):
    event_id = models.AutoField(primary_key=True)
    training = models.ForeignKey(
        TrainingMaster, 
        on_delete=models.CASCADE, 
        db_column='training_id'
    )
    training_topic = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    is_active = models.BooleanField(default=True)
    enable_course_access = models.BooleanField(default=False)
    enable_feedback = models.BooleanField(default=False)
    enable_evaluations = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'training_events'

    def __str__(self):
        return f"{self.training_topic} ({self.start_date})"


class EventLocation(models.Model):
    event_location_id = models.AutoField(primary_key=True)
    event = models.OneToOneField(
        TrainingEvent, 
        on_delete=models.CASCADE, 
        db_column='event_id',
        related_name='location'
    )
    city = models.CharField(max_length=100)
    venue = models.CharField(max_length=150)
    room = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_locations'


class EventSchedule(models.Model):
    schedule_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        TrainingEvent, 
        on_delete=models.CASCADE, 
        db_column='event_id',
        related_name='schedules'
    )
    training_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    material_link = models.CharField(max_length=255, null=True, blank=True)
    instructor_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_schedules'


class EventParticipant(models.Model):
    event_participant_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        TrainingEvent, 
        on_delete=models.CASCADE, 
        db_column='event_id',
        related_name='participants'
    )
    nik = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        db_column='nik'
    )
    attendance_status = models.CharField(max_length=25, null=True, blank=True)
    l1_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    l2_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_participants'
        unique_together = ('event', 'nik')


class EventCost(models.Model):
    COST_TYPE_CHOICES = [
        ('Estimate Cost', 'Estimate Cost'),
        ('Actual Cost', 'Actual Cost'),
    ]

    cost_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        TrainingEvent, 
        on_delete=models.CASCADE, 
        db_column='event_id',
        related_name='costs'
    )
    cost_center = models.CharField(max_length=25, null=True, blank=True)
    currency = models.CharField(max_length=10, default='IDR')
    room_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    training_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sppd_cost = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cost_type = models.CharField(max_length=50, choices=COST_TYPE_CHOICES)
    status_cost = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_costs'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cost_type__in=['Estimate Cost', 'Actual Cost']),
                name='event_cost_cost_type_check'
            )
        ]


class EventDocument(models.Model):
    document_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(
        TrainingEvent, 
        on_delete=models.CASCADE, 
        db_column='event_id',
        related_name='documents'
    )
    document_type = models.CharField(max_length=50)
    file_name = models.CharField(max_length=150)
    file_url = models.TextField()
    uploaded_by = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        db_column='uploaded_by'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_documents'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(file_url__contains='drive.google.com'),
                name='check_google_drive_link'
            ),
        ]


class EvaluationForm(models.Model):
    form_id = models.AutoField(primary_key=True)
    form_name = models.CharField(max_length=200, blank=True, null=True)
    training_master = models.ForeignKey('TrainingMaster', on_delete=models.SET_NULL, db_column='training_id', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='created_by', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    form_type = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluation_forms'

    def __str__(self):
        return f"{self.form_id} - {self.form_name}"


class EvaluationQuestion(models.Model):
    question_id = models.AutoField(primary_key=True)
    form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20)
    sequence = models.IntegerField(blank=True, null=True)
    is_required = models.BooleanField(blank=True, null=True)
    score = models.IntegerField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, db_column='created_by', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    evaluation_type = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluation_questions'

    def __str__(self):
        return f"{self.question_id} - {self.question_type}"


class EvaluationQuestionOption(models.Model):
    option_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(EvaluationQuestion, on_delete=models.CASCADE, related_name='options')
    option_text = models.CharField(max_length=200)
    sequence = models.IntegerField(blank=True, null=True)
    is_correct = models.BooleanField(blank=True, null=True)
    is_active = models.BooleanField(default=True, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluation_question_options'

    def __str__(self):
        return str(self.option_text)


class EvaluationAnswer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(EvaluationQuestion, on_delete=models.CASCADE)
    form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    rating_value = models.IntegerField(blank=True, null=True)
    selected_option = models.ForeignKey(EvaluationQuestionOption, on_delete=models.SET_NULL, blank=True, null=True)
    text_answer = models.TextField(blank=True, null=True)
    l1_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    l2_score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluation_answers'


class EvaluationResult(models.Model):
    result_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    form = models.ForeignKey(EvaluationForm, on_delete=models.CASCADE, blank=True, null=True)
    user_name = models.CharField(max_length=200, blank=True, null=True)
    evaluation_name = models.CharField(max_length=200, blank=True, null=True)
    training_name = models.CharField(max_length=200, blank=True, null=True)
    template = models.CharField(max_length=10, blank=True, null=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        managed = False
        db_table = 'evaluation_results'

    def __str__(self):
        return f"{self.user_name} - {self.evaluation_name}"


# ─── AI Assistant Models ───────────────────────────────────────────────────

class AiAdminConfig(models.Model):
    config_id = models.AutoField(primary_key=True)
    config_key = models.CharField(max_length=100, unique=True)
    config_value = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, db_column='updated_by')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_admin_config'

    def __str__(self):
        return self.config_key


class AiFaq(models.Model):
    faq_id = models.AutoField(primary_key=True)
    question = models.TextField()
    answer = models.TextField()
    sequence = models.IntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='faq_created_by', db_column='created_by')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='faq_updated_by', db_column='updated_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ai_faq'

    def __str__(self):
        return self.question[:50]


import uuid as uuid_module

class AiChatSession(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid_module.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_sessions')
    nik = models.BigIntegerField(null=True, blank=True)
    role = models.CharField(max_length=100, default='Employee')
    division_id = models.CharField(max_length=100, null=True, blank=True)
    session_start = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'ai_chat_sessions'
        ordering = ['-session_start']

    def __str__(self):
        return f"Session {self.session_id} - {self.user.username}"


class AiChatLog(models.Model):
    log_id = models.AutoField(primary_key=True)
    session = models.ForeignKey(AiChatSession, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    nik = models.BigIntegerField(null=True, blank=True)
    role = models.CharField(max_length=50, default='Employee')
    user_message = models.TextField()
    ai_response = models.TextField(null=True, blank=True)
    intent = models.CharField(max_length=100, null=True, blank=True)
    faq = models.ForeignKey(AiFaq, on_delete=models.SET_NULL, null=True, blank=True)
    is_faq_triggered = models.BooleanField(default=False)
    is_out_of_scope = models.BooleanField(default=False)
    is_unanswered = models.BooleanField(default=False)
    redirected_to_wa = models.BooleanField(default=False)
    is_authorized = models.BooleanField(default=True)
    query_executed = models.TextField(null=True, blank=True)
    context_sent = models.TextField(null=True, blank=True)
    response_time_ms = models.IntegerField(null=True, blank=True)
    tokens_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_chat_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"Log {self.log_id} in Session {self.session_id}"


class AiUnauthorizedAttempt(models.Model):
    attempt_id = models.AutoField(primary_key=True)
    log = models.ForeignKey(AiChatLog, on_delete=models.SET_NULL, null=True, blank=True, db_column='log_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    nik = models.BigIntegerField(null=True, blank=True)
    role = models.CharField(max_length=50)
    attempted_access = models.TextField()
    division_requested = models.CharField(max_length=11, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_unauthorized_attempts'

    def __str__(self):
        return f"Attempt {self.attempt_id} by user {self.user_id}"


class Budget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    budget_name = models.CharField(max_length=150)
    start_date_budget = models.DateField()
    end_date_budget = models.DateField()
    total_budget = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'budgets'

    def __str__(self):
        return f"{self.budget_name} ({self.start_date_budget} - {self.end_date_budget})"

    def __str__(self):
        return f"Attempt {self.attempt_id} by user {self.user_id}"