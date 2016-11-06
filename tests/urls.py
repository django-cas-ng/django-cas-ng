from django.conf.urls import url


def dummy_view():
    pass

urlpatterns = [
    url(r'^$', dummy_view, name="home"),
]
