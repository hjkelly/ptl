from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from ...data_apps.profiles.models import Profile


class ConfirmForm(forms.Form):
    """
    Does this 
    """
    code = forms.CharField()
    expected_code = None

    def __init__(self, expected_code, *args, **kwargs):
        """
        Expect a positional arg that's the code to validate against.
        """
        # Store this on the object.
        self.expected_code = expected_code
        # Do the rest of the stuff.
        super(ConfirmForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        """
        Make sure the code they entered matches the one we were told about.
        """
        code = str(self.cleaned_data.get('code', '')).strip()
        # Does the code (or lack thereof) match the expected code?
        if code != self.expected_code:
            raise ValidationError(_("The code you entered doesn't match your account. Try again!"))
        return code


class DashboardForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('name',)
