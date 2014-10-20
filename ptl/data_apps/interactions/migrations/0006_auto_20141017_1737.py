# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0005_checkin_profile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checkin',
            old_name='raw_content',
            new_name='raw_body',
        ),
    ]
