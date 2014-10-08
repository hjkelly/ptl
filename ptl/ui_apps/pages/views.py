from django.shortcuts import render
from django.views.generic import FormView

from ...data_apps.profiles.models import Profile
from .forms import SimpleSignupForm


class HomepageView(FormView):
    form_class = SimpleSignupForm
    success_url = '/'
    template_name = 'homepage.html'

    def form_valid(self, form):
        """
        Create a Profile as well as a Contact and User if needed.
        """
        d = form.cleaned_data
        Profile.objects.create(d['email'], d['password'], d['phone_number'])
        return super(HomepageView, self).form_valid(form)
homepage = HomepageView.as_view()
