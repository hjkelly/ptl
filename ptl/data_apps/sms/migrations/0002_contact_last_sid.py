# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='last_sid',
            field=models.CharField(max_length=34, null=True, blank=True),
            preserve_default=True,
        ),
    ]
