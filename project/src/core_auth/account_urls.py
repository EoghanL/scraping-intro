from django.conf.urls import url

from src.core_auth import views

urlpatterns = [
    url(r'^$', views.UserDetailView.as_view(), name='detail'),
    url(r'^change-password/$', views.ChangePasswordView.as_view(), name='request_password_change'),
    url(r'^reset-password/$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^sign-up/$', views.SignUpView.as_view(), name='sign_up'),
]
