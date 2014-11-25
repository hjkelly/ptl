from functools import wraps
import json

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponseNotAllowed, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.generic import FormView

from . import forms
from ...data_apps.profiles import models
from .responses import JsonResponseCreated, JsonResponseUnprocessable, HttpResponseNoContent


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

        profile = self.request.user.profile
        c.update({
            'profile': profile,
            'partners': profile.partnerships.all(),
        })
        return c
dashboard = login_required(DashboardView.as_view())


@login_required
def partner(request, pk=None):
    if request.method == 'POST':
        # Load the data into the form.
        form = forms.CreatePartnerForm(request.POST)
        # Should we create it?
        if form.is_valid():
            # Figure out the profile.
            profile = models.Profile.objects.get(user=request.user)
            # Create the thing.
            try:
                partner = models.Partnership.objects.create(
                        profile=profile,
                        name=form.cleaned_data['name'],
                        phone_number=str(form.cleaned_data['phone_number']))
            except IntegrityError:
                pass
            # Send it back at them.
            return JsonResponseCreated({
                    'pk': partner.pk,
                    'name': partner.pk,
                    'url': partner.get_absolute_url(),
                    'phone_number': str(partner.contact.phone_number)})
        # Ehhh... errors.
        else:
            return JsonResponseUnprocessable({'errors': form.errors})
    # If they're deleting one...
    elif request.method == 'DELETE':
        # ... look it up by PK, and make it so.
        partner = get_object_or_404(
                models.Partnership.objects.filter(profile__user=request.user),
                pk=pk)
        partner.delete()
        # Give them a 204 response.
        return HttpResponseNoContent("")
    else:
        return HttpResponseNotAllowed()


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
