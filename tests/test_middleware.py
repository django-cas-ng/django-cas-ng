from django.contrib.auth.models import AnonymousUser
from django.test import RequestFactory
from django_cas_ng import views
from django_cas_ng.middleware import CASMiddleware


def _process_view_with_middleware(
        middleware_cls, url, view_func):
    middleware = middleware_cls(view_func)
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
        CASMiddleware, '/login/', views.LoginView)
    assert response is None


def test_root_as_cas_admin_prefix_with_cas_logout(monkeypatch, settings):
    monkeypatch.setattr('django_cas_ng.middleware.reverse',
                        lambda func: "/login/")
    settings.CAS_ADMIN_PREFIX = "/"
    response = _process_view_with_middleware(
        CASMiddleware, '/logout/', views.LogoutView)
    assert response is None
