from django import forms
from .models import Participant
import re


class ParticipantForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.exam = kwargs.pop("exam", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Participant
        fields = ["name", "mobile"]

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()

        if len(name) < 3:
            raise forms.ValidationError("Name must be at least 3 characters long.")

        if not re.match(r"^[a-zA-Z\s]+$", name):
            raise forms.ValidationError("Name should contain only letters and spaces.")

        return name

    def clean_mobile(self):
        mobile = self.cleaned_data.get("mobile", "").strip()
        mobile = re.sub(r"\D", "", mobile)

        if len(mobile) != 10:
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")

        if not mobile.startswith(("6", "7", "8", "9")):
            raise forms.ValidationError("Enter a valid Indian mobile number.")

        return mobile

    def clean(self):
        cleaned_data = super().clean()
        mobile = cleaned_data.get("mobile")

        if mobile and self.exam:
            try:
                participant = Participant.objects.get(mobile=mobile, exam=self.exam)

                # ❌ block only if already submitted
                if participant.is_submitted:
                    raise forms.ValidationError("You have already submitted this exam.")

            except Participant.DoesNotExist:
                pass

        return cleaned_data
