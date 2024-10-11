from datetime import timedelta
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import admin
from .models import Course, PaymentScreenshot, UserProfile, ContactQuery


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    last_name = forms.CharField(max_length=30, required=True, help_text='Optional.')
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')
    mobile_number = forms.CharField(max_length=15, required=True)
    profile_photo = forms.ImageField(required=False, help_text='Optional')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'mobile_number', 'profile_photo', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = UserProfile.objects.create(user=user)
            profile.first_name = self.cleaned_data['first_name']
            profile.last_name = self.cleaned_data['last_name']
            profile.mobile_number = self.cleaned_data['mobile_number']
            if 'profile_photo' in self.cleaned_data:
                profile.profile_photo = self.cleaned_data['profile_photo']
            profile.save()
        return user
    
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'instructor', 'duration', 'students_count', 'price', 'is_free']

    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if isinstance(duration, str):
            try:
                hours, minutes, seconds = map(int, duration.split(':'))
                duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                raise forms.ValidationError("Invalid duration format. Use HH:MM:SS.")
        if duration > timedelta(days=3650):  # Example: maximum duration of 10 years
            raise forms.ValidationError("Duration is too long.")
        return duration
    
class CourseAdminForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
    
    def clean_duration(self):
        duration = self.cleaned_data['duration']
        if isinstance(duration, str):
            try:
                hours, minutes, seconds = map(int, duration.split(':'))
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            except ValueError:
                raise forms.ValidationError("Invalid duration format. Use HH:MM:SS.")
        return duration

from django import forms
from .models import PaymentScreenshot

class PaymentScreenshotForm(forms.ModelForm):
    class Meta:
        model = PaymentScreenshot
        fields = ['screenshot']

class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=15, required=True)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'mobile_number', 'profile_photo')

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user = user_profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            user_profile.save()
        return user_profile
    
class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactQuery
        fields = ['name', 'email', 'subject', 'message']
