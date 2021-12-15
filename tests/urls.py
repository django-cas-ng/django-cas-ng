from django.urls import path


def dummy_view():
    pass


urlpatterns = [
    path('', dummy_view, name="home"),
]
