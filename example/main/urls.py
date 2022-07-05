from django.urls import path
from main.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path("", HomePageView.as_view(), name="main-home"),

    path("person-lookup", PersonLookup.as_view(), name="person-lookup"),
]
