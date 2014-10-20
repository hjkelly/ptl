from functools import wraps

from django.contrib.auth.decorators import login_required  #, user_passes_test
from django.views.generic import FormView

from . import forms


class ConfirmView(FormView):
    form_class = forms.ConfirmForm
    template_name = 'dashboard/confirm.html'

    def get_form(self, form_class):
        """
        Get an instance of the form, but pass our custom positional arg too.
        """
        # Pass the logged-in user's confirmation code as a positional arg so
        # the form can declare their confirmation attempt as valid or invalid.
        return form_class(str(self.request.user.profile.confirmation_code),
                          **self.get_form_kwargs())

    def get_context_data(self, *args, **kwargs):
        c = super(ConfirmView, self).get_context_data(*args, **kwargs)
        c['already_confirmed'] = bool(self.request.user.profile.confirmed_contact)
        return c

    def form_valid(self, *args, **kwargs):
        p = self.request.user.profile
        p.confirm()
        return super(ConfirmView, self).form_valid(*args, **kwargs)

    def get_success_url(self):
        return self.request.path
confirm = login_required(ConfirmView.as_view())

"""
def confirmation_required(view_func):
    # If a user hasn't confirmed their phone number, force them to do so.
    def check_profile_confirmed(request, *args, **kwargs):
        if request.user.profile.confirmed:

    return login_required(_wrapped_view_func

    actual_decorator = user_passes_test(
        lambda u: u.profile.confirmed,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )
    if function:
        return login_required(actual_decorator(function)
    return actual_decorator


class ConfirmView(FormView):
    form_class = forms.ConfirmForm
    template_name = 'dashboard/confirm.html'
confirm = login_required(ConfirmView.as_view())
"""
