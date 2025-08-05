from django import forms
from .models import Participant

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['name', 'mobile']

    def clean_mobile(self):
        mobile = self.cleaned_data.get('mobile', '')

        # Check if the input contains only digits
        if not mobile.isdigit():
            raise forms.ValidationError("Mobile number must contain only digits.")

        # Check for minimum length of 10 digits
        if len(mobile) < 10:
            raise forms.ValidationError("Mobile number must be at least 10 digits long.")

        return mobile
