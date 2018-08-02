from model_mommy import mommy

from django.conf import settings
from django.test import TestCase

from src.core_auth.serializers import RequestPasswordChangeSerializer, ChangePasswordSerializer


class RequestPasswordChangeSerializerTests(TestCase):

    def setUp(self):
        self.data = {'email': 'foo@exammple.com'}

    def test_required_fields(self):
        serializer = RequestPasswordChangeSerializer(data={})
        serializer.is_valid()

        assert 'email' in serializer.errors

    def test_populate_user_in_validate_data_if_exists(self):
        user = mommy.make(settings.AUTH_USER_MODEL, email=self.data['email'])
        serializer = RequestPasswordChangeSerializer(data=self.data)
        serializer.is_valid()
        assert user == serializer.validated_data['user']

    def test_does_not_populate_user_in_validate_data_if_do_not_exist(self):
        serializer = RequestPasswordChangeSerializer(data=self.data)
        serializer.is_valid()
        assert 'user' not in serializer.validated_data


class ChangePasswordSerializerTests(TestCase):

    def setUp(self):
        self.data = {'password1': '123', 'password2': '123'}

    def test_required_fields(self):
        serializer = ChangePasswordSerializer(data={})
        serializer.is_valid()

        assert 'password1' in serializer.errors
        assert 'password2' in serializer.errors

    def test_passwords_have_to_match(self):
        self.data['password1'] = '321321'

        serializer = ChangePasswordSerializer(data=self.data)
        serializer.is_valid()

        assert 'non_field_errors' in serializer.errors
