# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_auto_20141120_1728'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='partnership',
            unique_together=set([('contact', 'confirmation_string')]),
        ),
    ]
