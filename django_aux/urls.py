from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(template_name='django_aux/login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='django_aux/logout.html'), name='logout'),
]
