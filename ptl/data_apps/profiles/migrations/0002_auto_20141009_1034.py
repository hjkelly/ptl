# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='send_reminders',
            new_name='confirmed',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='reminder_confirmation',
        ),
        migrations.AddField(
            model_name='profile',
            name='confirmation_code',
            field=models.CharField(default=b'8143', max_length=5),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='name',
            field=models.CharField(default='', max_length=25),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='profile',
            name='contact',
            field=models.ForeignKey(related_name=b'profile', to='sms.Contact'),
        ),
    ]
