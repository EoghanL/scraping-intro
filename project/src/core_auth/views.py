from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME, logout
from django.core.urlresolvers import reverse
from django.db import transaction
from django.shortcuts import redirect

from src.core_auth.forms import UserCreationForm
from src.core_auth.models import User
from src.core_auth.serializers import ChangePasswordSerializer, UserSerializer, RequestPasswordChangeSerializer


class UserLogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        logout(request)
        user.auth_token.delete()
        return Response()


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.needs_change_password or request.user.check_password(serializer.validated_data['password']):
            request.user.set_password(serializer.validated_data['password1'])
            request.user.save()
            return Response({'success': True}, status=status.HTTP_200_OK)
        return Response({'success': False}, status=status.HTTP_403_FORBIDDEN)


class UserDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class PasswordResetView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RequestPasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.get('user')
        if user:
            new_password = User.objects.make_random_password()
            user.force_new_password(new_password)
            user.save()

        return Response()


class SignUpView(APIView):

    def post(self, request):
        form = UserCreationForm(request.data)
        if not form.is_valid():
            return Response(form.errors, status=400)

        with transaction.atomic():
            user = form.save()
            token, created = Token.objects.get_or_create(user=user)

        return Response({'token': token.key}, status=201)
