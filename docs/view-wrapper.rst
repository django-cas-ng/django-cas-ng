View-wrappers Example
=====================

The ``settings.CAS_EXTRA_LOGIN_PARAMS`` allows you to define a static
dictionary of extra parameters to be passed on to the CAS login page. But what
if you want this dictionary to be dynamic (e.g. based on user session)?

Our current advice is to implement simple wrappers for our default views, like these ones:

..  code-block:: python

    from django_cas_ng import views as baseviews

    @csrf_exempt
    def login(request, **kwargs):
        return _add_locale(request, baseviews.LoginView.as_view()(request, **kwargs))


    def logout(request, **kwargs):
        return _add_locale(request, baseviews.LoginView.as_view()(request, **kwargs))


    def _add_locale(request, response):
        """If the given HttpResponse is a redirect to CAS, then add the proper
        `locale` parameter to it (and return the modified response). If not, simply
        return the original response."""

        if (
            isinstance(response, HttpResponseRedirect)
            and response['Location'].startswith(settings.CAS_SERVER_URL)
        ):
            from ourapp.some_module import get_currently_used_language
            url = response['Location']
            url += '&' if '?' in url else '&'
            url += "locale=%s" % get_currently_used_language(request)
            response['Location'] = url
        return response
