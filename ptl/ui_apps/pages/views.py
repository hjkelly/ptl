from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views.generic import FormView

from ...data_apps.profiles.models import Profile
from .forms import SimpleSignupForm


class HomepageView(FormView):
    form_class = SimpleSignupForm
    success_url = '/dashboard/'
    template_name = 'homepage.html'

    def form_valid(self, form):
        """
        Create a Profile as well as a Contact and User if needed.
        """
        d = form.cleaned_data
        # Create the profile.
        p = Profile.objects.create(name=d['name'],
                                   email=d['email'],
                                   password=d['password'],
                                   phone_number=d['phone_number'])
        # Log them in.
        authed_user = authenticate(username=d['email'], password=d['password'])
        login(self.request, authed_user)
        return super(HomepageView, self).form_valid(form)
homepage = HomepageView.as_view()
