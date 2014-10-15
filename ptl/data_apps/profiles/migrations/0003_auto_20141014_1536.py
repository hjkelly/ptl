# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20141009_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='confirmed',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
