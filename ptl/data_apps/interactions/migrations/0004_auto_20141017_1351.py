# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interactions', '0003_auto_20141016_1929'),
    ]

    operations = [
        migrations.RenameField(
            model_name='checkin',
            old_name='raw_text',
            new_name='raw_content',
        ),
    ]
