# Stub for pre django 1.7 apps.
# ⁻*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session

import urllib
import urllib2
from lxml import etree


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
    def retrieve_pt(cls, request, service):
        """`request` should be the current HttpRequest object
        `service` a string representing the service for witch we want to
        retrieve a ticket.
        The function return a Proxy Ticket or raise `ProxyError`
        """
        session = Session.objects.get(session_key=request.session.session_key)
        try:
            pgt = cls.objects.get(user=request.user, session=session).pgt
            params = urllib.urlencode({'pgt':pgt, 'targetService':service})
            response = urllib2.urlopen(
                "%s/proxy?%s" % (settings.CAS_SERVER_URL, params)
            )
            if response.code == 200:
                root = etree.fromstring(response.read())
                tickets = root.xpath(
                    "//cas:proxyTicket",
                    namespaces={"cas":"http://www.yale.edu/tp/cas"}
                )
                if len(tickets) == 1:
                    return tickets[0].text
                errors = root.xpath(
                    "//cas:authenticationFailure",
                    namespaces={"cas":"http://www.yale.edu/tp/cas"}
                )
                if len(errors) == 1:
                    raise ProxyError(errors[0].attrib['code'], errors[0].text)
            raise ProxyError("Bad http code %s" % response.code)
        except urllib2.HTTPError as error:
            raise ProxyError(str(error))
        except cls.DoesNotExist:
            raise ProxyError(
                "INVALID_TICKET",
                "No proxy ticket found for this HttpRequest object"
            )


class SessionTicket(models.Model):
    session = models.ForeignKey(Session, related_name="+", unique=True)
    ticket = models.CharField(max_length=255)
