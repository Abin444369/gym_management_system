from django import forms
from .models import Plan
from users.models import CustomUser

class PlanUploadForm(forms.ModelForm):
    class Meta:
        model = Plan
        fields = ['member', 'plan_type', 'file']

    def __init__(self, *args, **kwargs):
        super(PlanUploadForm, self).__init__(*args, **kwargs)
        self.fields['member'].queryset = CustomUser.objects.filter(role='member')
