# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0007_auto_20141017_1737'),
        ('sms', '0002_contact_last_sid'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='owner',
            field=models.OneToOneField(null=True, blank=True, to='profiles.Profile'),
            preserve_default=True,
        ),
    ]
