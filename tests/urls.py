from django.urls import path
from .views import *

urlpatterns = [
    path("person-lookup", PersonLookup.as_view(), name="person-lookup"),
    path("person-create-request", PersonCreateWithRequest.as_view(), name="person-create-request"),
    path("person-create", PersonCreate.as_view(), name="person-create"),
]
