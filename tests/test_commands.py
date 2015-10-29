"""Tests for the management commands"""
from __future__ import absolute_import
from django.conf import settings
from django.core import management
from importlib import import_module

from django_cas_ng.models import SessionTicket, ProxyGrantingTicket

import pytest

SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


@pytest.mark.django_db
def test_command_clean_session(django_user_model):
    # Use the configured session store to generate a fake session
    session = SessionStore()
    session['fake_session'] = 'fake-session'
    session.save()
    assert SessionStore(session_key=session.session_key) is not None

    # Create a fake session ticket and make sure it exists in the db
    session_ticket = SessionTicket.objects.create(
        session_key=session.session_key,
        ticket='fake-ticket'
    )
    assert session_ticket is not None
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is True

    # Create a fake user for the proxy granting ticket
    user = django_user_model.objects.create(username='test-user', email='test@example.com')
    assert user is not None
    assert django_user_model.objects.filter(username='test-user').exists() is True

    # Create a fake pgt
    pgt = ProxyGrantingTicket.objects.create(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket')
    assert pgt is not None
    assert ProxyGrantingTicket.objects.filter(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket').exists() is True


    # Call the clean sessions command and make sure things are cleaned up
    management.call_command('django_cas_ng_clean_sessions')
    assert SessionTicket.objects.filter(session_key=session.session_key,
                                        ticket='fake-ticket').exists() is False
    assert ProxyGrantingTicket.objects.filter(session_key=session.session_key,
                                       user=user, pgtiou='fake-ticket-iou',
                                       pgt='fake-ticket').exists() is False
