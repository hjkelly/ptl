from django import forms

from phonenumber_field.formfields import PhoneNumberField


class SimpleSignupForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'type': 'tel'}))
