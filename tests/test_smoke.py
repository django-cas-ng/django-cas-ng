def test_nothing_is_on_fire():
    """
    Simple smoke test to see that all of the modules load.
    """
    from django_cas_ng.models import *
    from django_cas_ng.backends import *
    from django_cas_ng.middleware import *
    from django_cas_ng.views import *
    from django_cas_ng.decorators import *
