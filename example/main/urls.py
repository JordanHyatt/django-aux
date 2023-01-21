from django.urls import path
from main.views import *
from django.views.generic import TemplateView

urlpatterns = [
    path("", HomePageView.as_view(), name="main-home"),
    path("person-lookup", PersonLookup.as_view(), name="person-lookup"),
    path("person-lookup/<int:foopk>", PersonLookup.as_view(), name="person-lookup"),
    path("person-delete/<int:pk>", PersonDelete.as_view(), name="person-delete"),
    path("person-create", PersonCreate.as_view(), name="person-create"),
    path("person-create-inline", PersonCreateInline.as_view(), name="person-create-inline"),
    path("person-update/<int:pk>", PersonUpdate.as_view(), name="person-update"),
    path("person-update-inline/<int:pk>", PersonUpdateInline.as_view(), name="person-update-inline"),


    path("sale-lookup", SaleLookup.as_view(), name="sale-lookup"),
    path("sale-lookup-buttons", SaleLookupButtons.as_view(), name="sale-lookup-buttons"),
    path("sale-lookup-form", SaleLookupWithForm.as_view(), name="sale-lookup-form"),
    path("sale-lookup-handle-form", SaleLookupHandleForm.as_view(), name="sale-lookup-handle-form"),
    path("sale-plotly", SalePlotly.as_view(), name="sale-plotly"),
    path("sale-delete/<int:pk>", SaleDelete.as_view(), name="sale-delete"),
]
