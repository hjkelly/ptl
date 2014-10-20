# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0002_contact_last_sid'),
        ('interactions', '0002_checkin_partnerreport'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='checkin',
            name='profile',
        ),
        migrations.AddField(
            model_name='checkin',
            name='contact',
            field=models.ForeignKey(related_name=b'checkins', default=0, to='sms.Contact'),
            preserve_default=False,
        ),
    ]
