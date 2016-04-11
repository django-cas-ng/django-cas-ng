from __future__ import absolute_import

from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

from django_cas_ng.middleware import CASMiddleware
from django_cas_ng import views


def _process_view_with_middleware(
        middleware_cls, url, view_func):
    middleware = middleware_cls()
    request_factory = RequestFactory()
    request = request_factory.get(url)
    request.user = AnonymousUser()
    return middleware.process_view(request, view_func,
                                   view_args=(), view_kwargs={})


def test_root_as_cas_admin_prefix_with_cas_login(monkeypatch, settings):
    monkeypatch.setattr('django_cas_ng.middleware.reverse',
                        lambda func: "/login/")
    settings.CAS_ADMIN_PREFIX = "/"
    response = _process_view_with_middleware(
        CASMiddleware, '/login/', views.login)
    assert response is None


def test_root_as_cas_admin_prefix_with_cas_logout(monkeypatch, settings):
    monkeypatch.setattr('django_cas_ng.middleware.reverse',
                        lambda func: "/login/")
    settings.CAS_ADMIN_PREFIX = "/"
    response = _process_view_with_middleware(
        CASMiddleware, '/logout/', views.logout)
    assert response is None
