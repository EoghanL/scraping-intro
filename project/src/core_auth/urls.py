from rest_framework.authtoken.views import ObtainAuthToken

from django.conf.urls import url

from src.core_auth import views

urlpatterns = [
    url(r'^login/$', ObtainAuthToken.as_view(), name='login'),
    url(r'^logout/$', views.UserLogoutView.as_view(), name='logout'),
]
