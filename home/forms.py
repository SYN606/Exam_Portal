from django import forms
from django.contrib.auth import get_user_model

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
    security_answer_input = forms.CharField(
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


class ResetPasswordStep1Form(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={
            'class':
            'w-full mt-1 px-4 py-2 border rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none',
            'placeholder': 'Enter your username',
        }))


class ResetPasswordStep2Form(forms.Form):
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
