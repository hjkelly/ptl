# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0008_auto_20141017_1924'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='partnership',
            unique_together=set([('profile', 'confirmation_string')]),
        ),
    ]
