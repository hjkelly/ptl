# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0002_contact_last_sid'),
        ('profiles', '0006_auto_20141017_1433'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='contact',
        ),
        migrations.AddField(
            model_name='profile',
            name='claimed_contact',
            field=models.ForeignKey(related_name=b'profiles_claimed_by', default=0, to='sms.Contact'),
            preserve_default=False,
        ),
    ]
