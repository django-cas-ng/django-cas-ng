from __future__ import absolute_import
from django_cas_ng.backends import (
    verify_cas3_response,
)


SUCCESS_RESPONSE = """<?xml version=\'1.0\' encoding=\'UTF-8\'?>
<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas"><cas:authenticationSuccess><cas:user>user@example.com</cas:user></cas:authenticationSuccess></cas:serviceResponse>
"""


SUCCESS_RESPONSE_WITH_ATTRIBUTES = """<?xml version='1.0' encoding='UTF-8'?>
<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas"><cas:authenticationSuccess><cas:user>user@example.com</cas:user><cas:attributes><cas:foo>bar</cas:foo><cas:baz>1234</cas:baz></cas:attributes></cas:authenticationSuccess></cas:serviceResponse>
"""

FAILURE_RESPONSE = """<?xml version='1.0' encoding='UTF-8'?>
<cas:serviceResponse xmlns:cas="http://www.yale.edu/tp/cas"><cas:authenticationFailure code="INVALID_TICKET">service ticket ST-1415306486-qs5TfUWlwge23u013h8fivR21RklkeWI has already been used</cas:authenticationFailure></cas:serviceResponse>
"""


def test_basic_successful_response_verification():
    user, attributes = verify_cas3_response(SUCCESS_RESPONSE)

    assert user == 'user@example.com'
    assert not attributes


def test_successful_response_verification_with_attributes():
    user, attributes = verify_cas3_response(SUCCESS_RESPONSE_WITH_ATTRIBUTES)

    assert user == 'user@example.com'
    assert attributes['foo'] == 'bar'
    assert attributes['baz'] == '1234'


def test_unsuccessful_response():
    user, attributes = verify_cas3_response(FAILURE_RESPONSE)
    assert user is None
    assert not attributes
