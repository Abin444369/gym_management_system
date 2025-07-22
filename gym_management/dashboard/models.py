from django.db import models
from users.models import CustomUser

class Plan(models.Model):
    PLAN_TYPE_CHOICES = [
        ('workout', 'Workout Plan'),
        ('diet', 'Diet Plan'),
    ]
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='uploaded_plans')
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPE_CHOICES)
    file = models.FileField(upload_to='plans/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.member.username} - {self.plan_type}"

class Feedback(models.Model):
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.member.username}"
    


class MemberProgress(models.Model):
    PERFORMANCE_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('average', 'Average'),
        ('needs_improvement', 'Needs Improvement')
    ]
    
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, 
                             related_name='progress_records')
    trainer = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                              limit_choices_to={'role': 'trainer'},
                              related_name='recorded_progress',
                              null=True, blank=True)  # Make trainer optional
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()
    height = models.FloatField()
    bmi = models.FloatField(blank=True, null=True)
    performance = models.CharField(max_length=20, choices=PERFORMANCE_CHOICES, null=True, blank=True)
    attendance = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if self.weight and self.height:
            height_in_meters = self.height / 100
            self.bmi = round(self.weight / (height_in_meters ** 2), 2)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date']