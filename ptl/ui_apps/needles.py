"""
These are lists of things we should find when examining responses for things
like forms.
"""
from django.core.urlresolvers import reverse

ANONYMOUS_CONTROLS = (
    "Sign In",
    reverse('login'),
)

UNCONFIRMED_CONTROLS = (
    "Sign Out",
    reverse('logout'),
)

CONFIRMED_CONTROLS = UNCONFIRMED_CONTROLS + (
    "Dashboard",
    reverse('dashboard'),
)

REGISTRATION_FORM = (
    '<form',
    'method="post"',
    'name="email"',
    'name="password"',
    'name="phone_number"',
    'type="submit"',
    "name='csrfmiddlewaretoken'",
)

CONFIRMATION_FORM = (
    '<form',
    'method="post"',
    'name="code"',
    'type="submit"',
    "name='csrfmiddlewaretoken'",
)

LOGIN_FORM = (
    '<form',
    'method="post"',
    'name="username"',
    'name="password"',
    'type="submit"',
    "name='csrfmiddlewaretoken'",
)

DASHBOARD = (
    'Your Dashboard',
    'Partners',
)
