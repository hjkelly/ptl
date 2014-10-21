# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sms', '0004_remove_contact_owner'),
    ]

    operations = [
        migrations.CreateModel(
            name='IncomingSMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('twilio_sid', models.CharField(max_length=34, null=True, blank=True)),
                ('twilio_timestamp', models.DateTimeField(db_index=True)),
                ('contact', models.ForeignKey(related_name=b'incoming_smses', to='sms.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutgoingSMS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('body', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('twilio_sid', models.CharField(max_length=34, null=True, blank=True)),
                ('contact', models.ForeignKey(related_name=b'outgoing_smses', to='sms.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='contact',
            name='last_sid',
        ),
        migrations.RemoveField(
            model_name='contact',
            name='num_messages_sent',
        ),
    ]
