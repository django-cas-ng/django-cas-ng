from django.test import RequestFactory

from django_cas_ng.views import (
    _service_url,
    _redirect_url,
    _login_url,
    _logout_url,
)


#
# _service_url tests
#
def test_service_url_helper():
    factory = RequestFactory()
    request = factory.get('/login/')

    actual = _service_url(request)
    expected = 'http://testserver/login/'

    assert actual == expected


def test_service_url_helper_as_https():
    factory = RequestFactory()
    request = factory.get('/login/', secure=True)

    actual = _service_url(request)
    expected = 'https://testserver/login/'

    assert actual == expected


def test_service_url_helper_with_redirect():
    factory = RequestFactory()
    request = factory.get('/login/', secure=True)

    actual = _service_url(request, redirect_to='https://testserver/landing-page/')
    expected = 'https://testserver/login/?next=https%3A%2F%2Ftestserver%2Flanding-page%2F'

    assert actual == expected


#
# _redirect_url tests
#
def test_redirect_url_with_url_as_get_parameter():
    factory = RequestFactory()
    request = factory.get('/login/', data={'next': '/landing-page/'}, secure=True)

    actual = _redirect_url(request)
    expected = '/landing-page/'

    assert actual == expected


def test_redirect_url_falls_back_to_cas_redirect_url_setting(settings):
    settings.CAS_IGNORE_REFERER = True
    settings.CAS_REDIRECT_URL = '/landing-page/'

    factory = RequestFactory()
    request = factory.get('/login/', secure=True)

    actual = _redirect_url(request)
    expected = '/landing-page/'

    assert actual == expected


def test_params_redirect_url_preceeds_settings_redirect_url(settings):
    settings.CAS_IGNORE_REFERER = True
    settings.CAS_REDIRECT_URL = '/landing-page/'

    factory = RequestFactory()
    request = factory.get('/login/', data={'next': '/override/'}, secure=True)

    actual = _redirect_url(request)
    expected = '/override/'

    assert actual == expected


def test_redirect_url_falls_back_to_http_referrer(settings):
    settings.CAS_IGNORE_REFERER = False
    settings.CAS_REDIRECT_URL = '/wrong-landing-page/'

    factory = RequestFactory()
    request = factory.get('/login/', secure=True, HTTP_REFERER='/landing-page/')

    actual = _redirect_url(request)
    expected = '/landing-page/'

    assert actual == expected


def test_redirect_url_strips_domain_prefix(settings):
    settings.CAS_IGNORE_REFERER = True
    settings.CAS_REDIRECT_URL = 'https://testserver/landing-page/'

    factory = RequestFactory()
    request = factory.get('/login/', secure=True)

    actual = _redirect_url(request)
    expected = '/landing-page/'

    assert actual == expected


#
# _login_url tests
#
def test_login_url_helper(settings):
    settings.CAS_RENEW = False
    settings.CAS_EXTRA_LOGIN_PARAMS = False
    settings.CAS_SERVER_URL = 'http://www.example.com/cas/'

    actual = _login_url('http://testserver/')
    expected = 'http://www.example.com/cas/login?service=http%3A%2F%2Ftestserver%2F'

    assert actual == expected


def test_login_url_helper_with_extra_params(settings):
    settings.CAS_RENEW = False
    settings.CAS_EXTRA_LOGIN_PARAMS = {'test': '1234'}
    settings.CAS_SERVER_URL = 'http://www.example.com/cas/'

    actual = _login_url('http://testserver/')
    # since the dictionary of parameters is unordered, we dont know which
    # parameter will be first, so just check that both are in the url.

    assert 'service=http%3A%2F%2Ftestserver%2F' in actual
    assert 'test=1234' in actual


def test_login_url_helper_with_renew(settings):
    settings.CAS_RENEW = True
    settings.CAS_EXTRA_LOGIN_PARAMS = None
    settings.CAS_SERVER_URL = 'http://www.example.com/cas/'

    actual = _login_url('http://testserver/')
    # since the dictionary of parameters is unordered, we dont know which
    # parameter will be first, so just check that both are in the url.

    assert 'service=http%3A%2F%2Ftestserver%2F' in actual
    assert 'renew=true' in actual


#
# _login_url tests
#
def test_logout_url_helper(settings):
    settings.CAS_SERVER_URL = 'https://www.example.com/cas/'

    factory = RequestFactory()
    request = factory.get('/logout/')

    actual = _logout_url(request)
    expected = 'https://www.example.com/cas/logout'

    assert actual == expected


def test_logout_url_helper_with_redirect(settings):
    settings.CAS_SERVER_URL = 'https://www.example.com/cas/'

    factory = RequestFactory()
    request = factory.get('/logout/')

    actual = _logout_url(request, next_page='/landing-page/')
    expected = 'https://www.example.com/cas/logout?url=http%3A%2F%2Ftestserver%2Flanding-page%2F'

    assert actual == expected
