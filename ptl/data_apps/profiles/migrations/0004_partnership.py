# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0002_contact_last_sid'),
        ('profiles', '0003_auto_20141014_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partnership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('confirmation_string', models.CharField(max_length=10)),
                ('confirmed', models.BooleanField(default=False, db_index=True)),
                ('contact', models.ForeignKey(related_name=b'partnerships', to='sms.Contact')),
                ('profile', models.ForeignKey(related_name=b'partnerships', to='profiles.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
