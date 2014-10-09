from django import forms

from phonenumber_field.formfields import PhoneNumberField


class SimpleSignupForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    phone_number = PhoneNumberField(widget=forms.TextInput(attrs={'type': 'tel'}))
