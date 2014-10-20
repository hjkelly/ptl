# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20141017_1433'),
        ('interactions', '0004_auto_20141017_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkin',
            name='profile',
            field=models.ForeignKey(related_name=b'checkins', default=0, to='profiles.Profile'),
            preserve_default=False,
        ),
    ]
