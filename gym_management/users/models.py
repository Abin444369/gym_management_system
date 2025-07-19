# users/models.py

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

ROLE_CHOICES = (
    ('admin', 'Admin'),
    ('trainer', 'Trainer'),
    ('member', 'Member'),
)

class CustomUser(AbstractUser):
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    name = models.CharField(max_length=100, blank=True, default="")         # ✅ No NULL issues
    age = models.IntegerField(null=True, blank=True)                         # ✅ Optional
    phone = models.CharField(max_length=10, blank=True, default="")          # ✅ No NULL issues
    address = models.TextField(blank=True, default="Not Provided")           # ✅ No NULL issues

    weight = models.FloatField(null=True, blank=True)                        # ✅ Optional
    height = models.FloatField(null=True, blank=True)                        # ✅ Optional
    experience = models.IntegerField(null=True, blank=True)                  # ✅ Optional

    trainer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'trainer'},
        related_name='assigned_members'
    )
class Progress(models.Model):
    member = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    date = models.DateField(auto_now_add=True)
    weight = models.FloatField()
    height = models.FloatField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.member.username} - {self.date}"
