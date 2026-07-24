import re

def fix_year_filter(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    replacement = """    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return qs.none()
            
        user_groups = list(user.groups.values_list('name', flat=True))
        
        view_mode = self.request.query_params.get('view_mode', 'admin')
        year_filter = self.request.query_params.get('year')
        month_filter = self.request.query_params.get('month')
        division_filter = self.request.query_params.get('division')

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
                if year_filter:
                    active_events = active_events.filter(start_date__year=year_filter)
                if month_filter:
                    try:
                        m = int(month_filter)
                        active_events = active_events.filter(start_date__month=m)
                    except (ValueError, TypeError):
                        pass
                qs = qs.filter(trainingevent__in=active_events).distinct()
            else:
                qs = qs.none()
        elif user.is_superuser or "Administrator" in user_groups or "Dean" in user_groups:
            # Apply standard filters
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
                
                if year_filter:
                    active_events = active_events.filter(start_date__year=year_filter)
                if month_filter:
                    try:
                        m = int(month_filter)
                        active_events = active_events.filter(start_date__month=m)
                    except (ValueError, TypeError):
                        pass

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
                if year_filter:
                    active_events = active_events.filter(start_date__year=year_filter)
                if month_filter:
                    try:
                        m = int(month_filter)
                        active_events = active_events.filter(start_date__month=m)
                    except (ValueError, TypeError):
                        pass
                qs = qs.filter(trainingevent__in=active_events).distinct()
            else:
                qs = qs.none()
        else:
            qs = qs.none()
            
        return qs"""

    # We need to replace from '    def get_queryset(self):' to '        return qs\n' right before class TrainingEventViewSet
    pattern = r"    def get_queryset\(self\):.*?        return qs\n"
    new_content = re.sub(pattern, replacement + "\n", content, flags=re.DOTALL)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

fix_year_filter('c:/xampp/htdocs/capstone-project/backend/api/views.py')
print("Fixed year filter in TrainingMasterViewSet")
