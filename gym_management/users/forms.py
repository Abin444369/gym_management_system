# users/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(required=False)
    age = forms.IntegerField(required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    phone = forms.CharField(required=False)
    experience = forms.IntegerField(required=False)
    weight = forms.FloatField(required=False)
    height = forms.FloatField(required=False)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def clean_role(self):
        role = self.cleaned_data.get('role')
        if role == 'admin':
            raise forms.ValidationError("Admin registration is not allowed.")
        return role

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        name = cleaned_data.get('name')
        age = cleaned_data.get('age')
        address = cleaned_data.get('address')
        phone = cleaned_data.get('phone')

        if role in ['trainer', 'member']:
            if not all([name, age, address, phone]):
                raise forms.ValidationError("Name, age, address, and phone are required.")

            if not str(age).isdigit() or int(age) <= 0:
                raise forms.ValidationError("Age must be a positive number.")

            if not phone.isdigit() or len(phone) != 10:
                raise forms.ValidationError("Phone must be a 10-digit number.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get('role')  # 🔴 this line is critical!
        user.name = self.cleaned_data.get('name')
        user.age = self.cleaned_data.get('age')
        user.address = self.cleaned_data.get('address')
        user.phone = self.cleaned_data.get('phone')

        if user.role == 'trainer':
            user.experience = self.cleaned_data.get('experience')
        elif user.role == 'member':
            user.weight = self.cleaned_data.get('weight')
            user.height = self.cleaned_data.get('height')

        if commit:
            user.save()
        return user
