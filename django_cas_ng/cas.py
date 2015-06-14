from django.utils.six.moves import urllib_parse
from django.utils.six.moves.urllib_request import urlopen, Request
from uuid import uuid4
import datetime

"""
if settings.CAS_VERSION not in _PROTOCOLS:
    raise ValueError('Unsupported CAS_VERSION %r' % settings.CAS_VERSION)

if settings.CAS_PROXY_CALLBACK and settings.CAS_VERSION not in ['2', '3']:
    raise ValueError('proxy callback only supported by CAS_VERSION 2 and 3')
"""

class CASError(ValueError):
    pass

class CASClient(object):
    def __new__(self, *args, **kwargs):
        version = kwargs.pop('version')
        if version in (1, '1'):
            return CASClientV1(*args, **kwargs)
        elif version in (2, '2'):
            return CASClientV2(*args, **kwargs)
        elif version in (3, '3'):
            return CASClientV3(*args, **kwargs)
        elif version == 'CAS_2_SAML_1_0':
            return CASClientWithSAMLV1(*args, **kwargs)
        raise ValueError('Unsupported CAS_VERSION %r' % version)

class CASClientBase(object):
    def __init__(self, service_url=None, server_url=None,
            extra_login_params=None, renew=False, 
            username_attribute=None
        ):

        self.service_url = service_url
        self.server_url = server_url
        self.extra_login_params = extra_login_params or {}
        self.renew = renew
        self.username_attribute = username_attribute
        pass


    def verify_ticket(self, ticket):
        """must return a triple"""
        raise NotImplementedError()


    def get_login_url(self):
        """Generates CAS login URL"""
        params = {'service': self.service_url}
        if self.renew:
            params.update({'renew': 'true'})

        params.update(self.extra_login_params)
        url = urllib_parse.urljoin(self.server_url, 'login')
        query = urllib_parse.urlencode(params)
        return url + '?' + query


    def get_logout_url(self, redirect_url=None):
        """Generates CAS logout URL"""
        url = urllib_parse.urljoin(self.server_url, 'logout')
        if redirect_url:
            url += '?' + urllib_parse.urlencode({'url': redirect_url})
        return url


    def get_proxy_url(self, pgt):
        """Returns proxy url, given the proxy granting ticket"""
        params = urllib_parse.urlencode({'pgt': pgt, 'targetService': self.get_service_url()})
        return "%s/proxy?%s" % (self.server_url, params)


    def get_proxy_ticket(self, pgt):
        """Returns proxy ticket given the proxy granting ticket"""
        response = urlopen(self.get_proxy_url(pgt))
        if response.code == 200:
            from lxml import etree
            root = etree.fromstring(response.read())
            tickets = root.xpath(
                "//cas:proxyTicket",
                namespaces={"cas": "http://www.yale.edu/tp/cas"}
            )
            if len(tickets) == 1:
                return tickets[0].text
            errors = root.xpath(
                "//cas:authenticationFailure",
                namespaces={"cas": "http://www.yale.edu/tp/cas"}
            )
            if len(errors) == 1:
                raise CASError(errors[0].attrib['code'], errors[0].text)
        raise CASError("Bad http code %s" % response.code)


    def get_saml_slos(self, logout_request):
        """returns saml logout ticket info"""
        from lxml import etree
        try:
            root = etree.fromstring(logout_request)
            return root.xpath(
                    "//samlp:SessionIndex",
                    namespaces={'samlp': "urn:oasis:names:tc:SAML:2.0:protocol"}
            )
        except etree.XMLSyntaxError:
            pass


class CASClientV1(CASClientBase):
    """CAS Client Version 1"""

    def verify_ticket(self, ticket):
        """Verifies CAS 1.0 authentication ticket.

        Returns username on success and None on failure.
        """
        params = [('ticket', ticket), ('service', self.service)]
        url = (urllib_parse.urljoin(self.server_url, 'validate') + '?' +
               urllib_parse.urlencode(params))
        page = urlopen(url)
        try:
            verified = page.readline().strip()
            if verified == 'yes':
                return page.readline().strip(), None, None
            else:
                return None, None, None
        finally:
            page.close()


class CASClientV2(CASClientBase):
    """CAS Client Version 2"""

    def __init__(self, proxy_callback=None, *args, **kwargs):
        #proxy_callback is for V2 and V3
        #so V3 is subclass of V2
        self.proxy_callback = proxy_callback
        super(CASClientV2, self).__init__(*args, **kwargs)


    def verify_ticket(self, ticket):
        """Verifies CAS 2.0+ XML-based authentication ticket.

        Returns username on success and None on failure.
        """
        try:
            from xml.etree import ElementTree
        except ImportError:
            from elementtree import ElementTree

        user = None
        pgtiou = None

        params = [('ticket', ticket), ('service', self.service_url)]
        if self.proxy_callback:
            params.append(('pgtUrl', self.proxy_callback))

        url = (urllib_parse.urljoin(self.server_url, 'serviceValidate') + '?' +
               urllib_parse.urlencode(params))
        page = urlopen(url)
        try:
            response = page.read()
            tree = ElementTree.fromstring(response)
            if tree[0].tag.endswith('authenticationSuccess'):
                for element in tree[0]:
                    if element.tag.endswith('user'):
                        user = element.text
                    elif element.tag.endswith('proxyGrantingTicket'):
                        pgtiou = element.text
                return user, None, pgtiou
            else:
                return None, None, None
        finally:
            page.close()


class CASClientV3(CASClientV2):
    """CAS Client Version 3"""

    def verify_ticket(self, ticket):
        """Verifies CAS 3.0+ XML-based authentication ticket and returns extended attributes.

        Returns username on success and None on failure.
        """
        response = self.get_verification_response(ticket)
        return self.verify_response(response)


    def get_verification_response(self, ticket):
        params = [('ticket', ticket), ('service', self.service_url)]
        if self.proxy_callback:
            params.append(('pgtUrl', self.proxy_callback))
        base_url = urllib_parse.urljoin(self.server_url, 'proxyValidate')
        url = base_url + '?' + urllib_parse.urlencode(params)
        page = urlopen(url)
        return page.read()


    @classmethod
    def verify_response(cls, response):
        user = None
        attributes = {}
        pgtiou = None

        try:
            from xml.etree import ElementTree
        except ImportError:
            from elementtree import ElementTree

        tree = ElementTree.fromstring(response)

        if tree[0].tag.endswith('authenticationSuccess'):
            for element in tree[0]:
                if element.tag.endswith('user'):
                    user = element.text
                elif element.tag.endswith('proxyGrantingTicket'):
                    pgtiou = element.text
                elif element.tag.endswith('attributes'):
                    for attribute in element:
                        tag = attribute.tag.split("}").pop()
                        if tag in attributes:
                            if isinstance(attributes[tag], list):
                                attributes[tag].append(attribute.text)
                            else:
                                attributes[tag] = [attributes[tag]]
                                attributes[tag].append(attribute.text)
                        else:
                            attributes[tag] = attribute.text

        return user, attributes, pgtiou


SAML_1_0_NS = 'urn:oasis:names:tc:SAML:1.0:'
SAML_1_0_PROTOCOL_NS = '{' + SAML_1_0_NS + 'protocol' + '}'
SAML_1_0_ASSERTION_NS = '{' + SAML_1_0_NS + 'assertion' + '}'
SAML_ASSERTION_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Header/>
<SOAP-ENV:Body>
<samlp:Request xmlns:samlp="urn:oasis:names:tc:SAML:1.0:protocol"
MajorVersion="1"
MinorVersion="1"
RequestID="{request_id}"
IssueInstant="{timestamp}">
<samlp:AssertionArtifact>{ticket}</samlp:AssertionArtifact></samlp:Request>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>"""

class CASClientWithSAMLV1(CASClientBase):
    """CASClient 3.0+ with SAML"""

    def verify_ticket(self, ticket):
        """Verifies CAS 3.0+ XML-based authentication ticket and returns extended attributes.

        @date: 2011-11-30
        @author: Carlos Gonzalez Vila <carlewis@gmail.com>

        Returns username and attributes on success and None,None on failure.
        """

        try:
            from xml.etree import ElementTree
        except ImportError:
            from elementtree import ElementTree

        page = self.fetch_saml_validation(ticket)

        try:
            user = None
            attributes = {}
            response = page.read()
            tree = ElementTree.fromstring(response)
            # Find the authentication status
            success = tree.find('.//' + SAML_1_0_PROTOCOL_NS + 'StatusCode')
            if success is not None and success.attrib['Value'].endswith(':Success'):
                # User is validated
                attrs = tree.findall('.//' + SAML_1_0_ASSERTION_NS + 'Attribute')
                for at in attrs:
                    if self.username_attribute in list(at.attrib.values()):
                        user = at.find(SAML_1_0_ASSERTION_NS + 'AttributeValue').text
                        attributes['uid'] = user

                    values = at.findall(SAML_1_0_ASSERTION_NS + 'AttributeValue')
                    if len(values) > 1:
                        values_array = []
                        for v in values:
                            values_array.append(v.text)
                            attributes[at.attrib['AttributeName']] = values_array
                    else:
                        attributes[at.attrib['AttributeName']] = values[0].text
            return user, attributes, None
        finally:
            page.close()


    def fetch_saml_validation(self, ticket):
        # We do the SAML validation
        headers = {
            'soapaction': 'http://www.oasis-open.org/committees/security',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'accept': 'text/xml',
            'connection': 'keep-alive',
            'content-type': 'text/xml; charset=utf-8',
        }
        params = [('TARGET', self.service_url)]
        saml_validate_url = urllib_parse.urljoin(
            self.server_url, 'samlValidate',
        )
        url = Request(
            saml_validate_url + '?' + urllib_parse.urlencode(params),
            '',
            headers,
        )
        page = urlopen(url, data=self.get_saml_assertion(ticket))

        return page


    @classmethod
    def get_saml_assertion(cls, ticket):
        """
        http://www.jasig.org/cas/protocol#samlvalidate-cas-3.0

        SAML request values:

        RequestID [REQUIRED]:
            unique identifier for the request
        IssueInstant [REQUIRED]:
            timestamp of the request
        samlp:AssertionArtifact [REQUIRED]:
            the valid CAS Service Ticket obtained as a response parameter at login.
        """
        # RequestID [REQUIRED] - unique identifier for the request
        request_id = uuid4()

        # e.g. 2014-06-02T09:21:03.071189
        timestamp = datetime.datetime.now().isoformat()

        return SAML_ASSERTION_TEMPLATE.format(
            request_id=request_id,
            timestamp=timestamp,
            ticket=ticket,
        ).encode('utf8')
