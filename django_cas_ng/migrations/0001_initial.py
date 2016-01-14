# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyGrantingTicket',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('session_key', models.CharField(null=True, max_length=255, blank=True)),
                ('pgtiou', models.CharField(null=True, max_length=255, blank=True)),
                ('pgt', models.CharField(null=True, max_length=255, blank=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(null=True, related_name='+', to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SessionTicket',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('session_key', models.CharField(max_length=255)),
                ('ticket', models.CharField(max_length=255)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='proxygrantingticket',
            unique_together=set([('session_key', 'user')]),
        ),
    ]
