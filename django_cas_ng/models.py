# Stub for pre django 1.7 apps.
# ⁻*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from .utils import (get_cas_client, get_service_url)


class ProxyError(ValueError):
    pass


class ProxyGrantingTicket(models.Model):
    class Meta:
        unique_together = ('session', 'user')
    session = models.ForeignKey(
        Session,
        related_name="+",
        blank=True,
        null=True
    )
    user = models.ForeignKey(
        User,
        related_name="+",
        null=True,
        blank=True
    )
    pgtiou = models.CharField(max_length=255, null=True, blank=True)
    pgt = models.CharField(max_length=255, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, auto_now=True)

    @classmethod
    def retrieve_pt(cls, request):
        """`request` should be the current HttpRequest object
        `service` a string representing the service for witch we want to
        retrieve a ticket.
        The function return a Proxy Ticket or raise `ProxyError`
        """
        session = Session.objects.get(session_key=request.session.session_key)
        try:
            pgt = cls.objects.get(user=request.user, session=session).pgt
        except cls.DoesNotExist:
            raise ProxyError(
                "INVALID_TICKET",
                "No proxy ticket found for this HttpRequest object"
            )
        else:
            service_url = get_service_url(request)
            client = get_cas_client(service_url=service_url)
            try:
                return client.get_proxy_ticket(pgt)
            except Exception, e:
                raise ProxyError(unicode(e))


class SessionTicket(models.Model):
    session = models.ForeignKey(Session, related_name="+", unique=True)
    ticket = models.CharField(max_length=255)
