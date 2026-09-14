from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':
            'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
            'placeholder': 'Enter username',
        }))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={
            'class':
            'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
            'placeholder': 'Enter password',
        }))


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                'class':
                'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                'placeholder': 'Create password',
            }))
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(
            attrs={
                'class':
                'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                'placeholder': 'Confirm password',
            }))
    security_answer = forms.CharField(
        label="Security Answer",
        widget=forms.TextInput(
            attrs={
                'class':
                'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                'placeholder': 'Your security answer',
            }))

    class Meta:
        model = User
        fields = ['username', 'email', 'security_question']
        widgets = {
            'username':
            forms.TextInput(
                attrs={
                    'class':
                    'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                    'placeholder': 'Choose a username',
                }),
            'email':
            forms.EmailInput(
                attrs={
                    'class':
                    'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                    'placeholder': 'Enter email',
                }),
            'security_question':
            forms.Select(
                attrs={
                    'class':
                    'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none bg-white',
                }),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email is already registered!")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2:
            if p1 != p2:
                self.add_error("password2", "Passwords do not match!")
            else:
                user = User(
                    username=cleaned_data.get("username", ""),
                    email=cleaned_data.get("email", ""),
                )
                try:
                    validate_password(p1, user=user)
                except forms.ValidationError as error:
                    self.add_error("password1", error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password(self.cleaned_data["password1"])
        user.set_security_answer(self.cleaned_data["security_answer"])
        if commit:
            user.save()
        return user


class ResetPasswordStep1Form(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':
            'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
            'placeholder': 'Enter your username',
        }))


class ResetPasswordStep2Form(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput(), required=False)
    security_answer = forms.CharField(
        label="Security Answer",
        widget=forms.TextInput(
            attrs={
                'class':
                'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                'placeholder': 'Enter your security answer',
            }))
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(
            attrs={
                'class':
                'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                'placeholder': 'Enter new password',
            }))
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(
            attrs={
                'class':
                'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
                'placeholder': 'Confirm new password',
            }))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password")
        p2 = cleaned_data.get("confirm_password")
        username = cleaned_data.get("username")

        if p1 and p2:
            if p1 != p2:
                self.add_error("confirm_password", "Passwords do not match!")
            else:
                user = None
                if username:
                    user = User.objects.filter(username=username).first()
                try:
                    validate_password(p1, user=user)
                except forms.ValidationError as error:
                    self.add_error("new_password", error)

        return cleaned_data
