# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0005_auto_20141021_1545'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='incomingsms',
            options={'ordering': ('-twilio_date_sent',)},
        ),
        migrations.RenameField(
            model_name='incomingsms',
            old_name='twilio_timestamp',
            new_name='twilio_date_sent',
        ),
        migrations.AlterField(
            model_name='incomingsms',
            name='twilio_sid',
            field=models.CharField(db_index=True, max_length=34, unique=True, null=True, blank=True),
        ),
    ]
