
Proxy Granting Ticket
---------------------

If you want your application to be able to issue Proxy Ticket to authenticate against some other CAS application,
setup the CAS_PROXY_CALLBACK parameter.
Allow on the CAS config django_cas_ng to act as a Proxy application.
Then after a user has logged in using the CAS, you can retrieve a Proxy Ticket as follow:

..  code-block:: python

    from django_cas_ng.models import ProxyGrantingTicket

    def my_pretty_view(request, ...):
        proxy_ticket = ProxyGrantingTicket.retrieve_pt(request, service)

where ``service`` is the service url for which you want a proxy ticket.



