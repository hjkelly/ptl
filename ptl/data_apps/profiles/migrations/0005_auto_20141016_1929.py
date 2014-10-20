# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_partnership'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='contact',
            field=models.ForeignKey(related_name=b'profiles', to='sms.Contact'),
        ),
    ]
