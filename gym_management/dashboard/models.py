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
    
