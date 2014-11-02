"""
These are lists of things we should find when examining responses for things
like forms.
"""

REGISTRATION_FORM = (
    '<form',
    'method="post"',
    'name="email"',
    'name="password"',
    'name="phone_number"',
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
