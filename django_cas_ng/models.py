# Stub for pre django 1.7 apps.
# ⁻*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

class ProxyGrantingTicket(models.Model):
    user = models.ForeignKey(
        User,
        related_name="+",
        unique=True,
        null=True,
        blank=True
    )
    pgtiou = models.CharField(max_length=255, null=True, blank=True)
    pgt = models.CharField(max_length=255, null=True, blank=True)

class SessionTicket(models.Model):
    session = models.ForeignKey(Session, related_name="+", unique=True)
    ticket = models.CharField(max_length=255)
