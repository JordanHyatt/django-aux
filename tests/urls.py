from django.urls import path
from .views import *

urlpatterns = [
    path("person-lookup", PersonLookup.as_view(), name="person-lookup"),
]
