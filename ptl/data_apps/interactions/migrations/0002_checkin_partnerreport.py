# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_auto_20141014_1536'),
        ('interactions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Checkin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_text', models.TextField()),
                ('status', models.PositiveSmallIntegerField(choices=[(3, 'Good'), (2, 'Bad'), (1, 'Ugly')])),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(related_name=b'checkins', to='profiles.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PartnerReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('checkin', models.ForeignKey(blank=True, to='interactions.Checkin', null=True)),
                ('profile', models.ForeignKey(related_name=b'partner_reports', to='profiles.Profile')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
