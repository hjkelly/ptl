# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0004_remove_contact_owner'),
        ('profiles', '0007_auto_20141017_1737'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='confirmed',
        ),
        migrations.AddField(
            model_name='profile',
            name='confirmed_contact',
            field=models.OneToOneField(related_name=b'profile', null=True, blank=True, to='sms.Contact'),
            preserve_default=True,
        ),
    ]
