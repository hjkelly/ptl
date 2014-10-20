# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_auto_20141016_1929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='contact',
            field=models.OneToOneField(related_name=b'profile', to='sms.Contact'),
        ),
    ]
