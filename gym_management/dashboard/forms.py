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

class PaymentPlanForm(forms.Form):
    # Example plans - you can make this dynamic from a database if needed
    PLAN_CHOICES = [
        ('monthly', 'Monthly - ₹500'),
        ('quarterly', 'Quarterly - ₹1200'),
        ('yearly', 'Yearly - ₹4000'),
    ]
    plan = forms.ChoiceField(choices=PLAN_CHOICES, widget=forms.RadioSelect, label="Choose a Payment Plan")

    def get_amount(self):
        plan = self.cleaned_data.get('plan')
        if plan == 'monthly':
            return 500.00
        elif plan == 'quarterly':
            return 1200.00
        elif plan == 'yearly':
            return 4000.00
        return 0.00