from functools import wraps

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.views.generic import FormView

from . import forms


class ConfirmView(FormView):
    form_class = forms.ConfirmForm
    template_name = 'confirm.html'

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
        return reverse('dashboard')
confirm = login_required(ConfirmView.as_view())


class DashboardView(FormView):
    form_class = forms.DashboardForm
    template_name = 'dashboard.html'

    def dispatch(self, request, *args, **kwargs):
        # Make them confirm their phone number first.
        if not request.user.profile.is_confirmed():
            return HttpResponseRedirect(reverse('confirm'))
        return super(DashboardView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        c = super(DashboardView, self).get_context_data(**kwargs)
        c.update({
            'profile': self.request.user.profile,
        })
        return c
dashboard = login_required(DashboardView.as_view())


def skippable_login(view):
    """
    If they're already logged in, forward them to the dashboard.
    """
    def view_wrapper(request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('dashboard'))
        else:
            return view(request, *args, **kwargs)
    return view_wrapper
login = skippable_login(django_login)


def logout(request):
    """
    Log them out if they're logged in; ALWAYS redirect them to the homepage.
    """
    if request.user.is_authenticated():
        auth_logout(request)
    return HttpResponseRedirect(reverse('homepage'))
