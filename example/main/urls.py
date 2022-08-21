from django.urls import path
from main.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path("", HomePageView.as_view(), name="main-home"),
    path("person-lookup", PersonLookup.as_view(), name="person-lookup"),
    path("person-lookup/<int:foopk>", PersonLookup.as_view(), name="person-lookup"),
    path("person-delete/<int:pk>", PersonDelete.as_view(), name="person-delete"),
    path("person-create", PersonCreate.as_view(), name="person-create"),
    path("person-update/<int:pk>", PersonUpdate.as_view(), name="person-update"),
    path("person-update-inline/<int:pk>", PersonUpdateInline.as_view(), name="person-update-inline"),
    
]
