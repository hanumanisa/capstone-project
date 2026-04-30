from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from .models import Employee, EventParticipant, EventSchedule, TnaParticipant, TrainingEvent

class DashboardCardsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.profile
            employee = profile.employee
        except Exception:
            # If user has no employee profile, return empty or zero stats
            return Response({
                "total_training": 0,
                "total_hours": "0",
                "average_hours": "0",
                "l1_score": "0.0",
                "l2_score": "0.0",
                "tna_coverage": "0%"
            })

        # Calculate Total Training
        participations = EventParticipant.objects.filter(nik=employee)
        total_training = participations.count()

        # Calculate Total Hours
        attended_event_ids = participations.values_list('event_id', flat=True)
        schedules = EventSchedule.objects.filter(event_id__in=attended_event_ids)
        
        total_hours_val = 0
        for sched in schedules:
            if sched.start_time and sched.end_time:
                h1, m1 = sched.start_time.hour, sched.start_time.minute
                h2, m2 = sched.end_time.hour, sched.end_time.minute
                duration = (h2 - h1) + (m2 - m1) / 60.0
                if duration > 0:
                    total_hours_val += duration
                    
        # Calculate Average Hours
        if total_training > 0:
            average_hours_val = total_hours_val / total_training
        else:
            average_hours_val = 0

        # Calculate L1 and L2 Averages
        l1_agg = participations.filter(l1_score__isnull=False).aggregate(Avg('l1_score'))['l1_score__avg']
        l2_agg = participations.filter(l2_score__isnull=False).aggregate(Avg('l2_score'))['l2_score__avg']
        
        l1_val = float(l1_agg) if l1_agg else 0.0
        l2_val = float(l2_agg) if l2_agg else 0.0

        # Calculate TNA Program Coverage
        tna_parts = TnaParticipant.objects.filter(nik=employee)
        total_tna = tna_parts.count()
        matched_tna = 0
        
        if total_tna > 0:
            attended_courses = set(
                TrainingEvent.objects.filter(event_id__in=attended_event_ids)
                .values_list('training__course_id', flat=True)
            )
            for tp in tna_parts:
                if tp.tna.course_id in attended_courses:
                    matched_tna += 1
            tna_coverage_val = (matched_tna / total_tna) * 100
        else:
            tna_coverage_val = 0

        return Response({
            "total_training": total_training,
            "total_hours": f"{total_hours_val:,.1f}".replace('.0', ''),
            "average_hours": f"{average_hours_val:,.1f}".replace('.0', ''),
            "l1_score": f"{l1_val:.2f}",
            "l2_score": f"{l2_val:.2f}",
            "tna_coverage": f"{tna_coverage_val:.1f}%".replace('.0%', '%')
        })
