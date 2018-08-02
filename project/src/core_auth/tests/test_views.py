from model_mommy import mommy
from rest_framework.authtoken.models import Token
from unittest.mock import patch, Mock

from django.conf import settings
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.test import TestCase

from src.core_auth.models import User


class UserLoginViewTests(TestCase):

    def setUp(self):
        self.url = reverse('core_auth:login')
        self.user = mommy.prepare(settings.AUTH_USER_MODEL, email='foo@foo.com')
        self.user.set_password('123123')
        self.user.save()
        self.data = {'username': 'foo@foo.com', 'password': '123123'}

    def test_recover_token_key(self):
        response = self.client.post(self.url, self.data)

        assert 200 == response.status_code
        assert bool(response.json()['token']) is True

    def test_recover_token_key_with_case_insensitive_email(self):
        data = self.data
        data['username'] = 'Foo@Foo.Com'
        response = self.client.post(self.url, self.data)

        assert 200 == response.status_code
        assert bool(response.json()['token']) is True

    def test_returns_400_if_invalid_login(self):
        response = self.client.post(self.url, {})
        content = response.json()

        assert 400 == response.status_code
        assert 'username' in content
        assert 'password' in content


class UserLogoutViewTests(TestCase):

    def setUp(self):
        self.url = reverse('core_auth:logout')
        self.user = mommy.make(settings.AUTH_USER_MODEL)
        self.tokem = mommy.make(Token, user=self.user)
        self.client.force_login(self.user)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        assert 401 == response.status_code

    def test_get_logout_user(self):
        response = self.client.get(self.url)
        user = auth.get_user(self.client)

        assert 200 == response.status_code
        assert user.is_authenticated() is False
        assert not user == self.user

    def test_deletes_user_token(self):
        other_token = mommy.make(Token) # other user token
        assert 2 == Token.objects.count()

        response = self.client.get(self.url)

        assert 1 == Token.objects.count()
        assert other_token == Token.objects.get()


class ChangePasswordViewTests(TestCase):

    def setUp(self):
        self.url = reverse('account:request_password_change')
        self.user = mommy.make(settings.AUTH_USER_MODEL, needs_change_password=True)
        self.client.force_login(self.user)
        self.data = {'password1': '123', 'password2': '123'}

    def test_login_required(self):
        self.client.logout()

        response = self.client.post(self.url, self.data)

        assert 401 == response.status_code

    def test_returns_400_if_invalid_post(self):
        response = self.client.post(self.url, {})
        content = response.json()

        assert 400 == response.status_code
        assert 'password1' in content
        assert 'password2' in content

    def test_update_user_password(self):
        response = self.client.post(self.url, self.data)

        assert 200 == response.status_code
        self.user.refresh_from_db()
        assert self.user.check_password('123') is True
        assert self.user.needs_change_password is False


class AccountViewTests(TestCase):

    def setUp(self):
        self.url = reverse('account:detail')
        self.user = mommy.make(settings.AUTH_USER_MODEL, needs_change_password=True)
        self.client.force_login(self.user)

    def test_login_required(self):
        self.client.logout()

        response = self.client.get(self.url)

        assert 401 == response.status_code

    def test_user_info(self):
        response = self.client.get(self.url)
        content = response.json()

        assert 200 == response.status_code
        assert self.user.email == content['email']
        assert self.user.first_name == content['first_name']
        assert self.user.last_name == content['last_name']
        assert self.user.needs_change_password == content['needs_change_password']


class PasswordResetViewTests(TestCase):

    def setUp(self):
        self.url = reverse('account:password_reset')
        self.user = mommy.make(settings.AUTH_USER_MODEL, email='email@email.com', needs_change_password=False)
        self.data = {'email': self.user.email}

    def test_returns_400_if_invalid_post(self):
        response = self.client.post(self.url, {})
        content = response.json()

        assert 400 == response.status_code
        assert 'email' in content

    @patch.object(User.objects, 'make_random_password', Mock(return_value='123'))
    def test_update_user_password(self):
        response = self.client.post(self.url, self.data)

        assert 200 == response.status_code
        self.user.refresh_from_db()
        assert self.user.check_password('123') is True
        assert self.user.needs_change_password is True

    @patch.object(User.objects, 'make_random_password')
    def test_does_not_change_user_if_wrong_email(self, mocked_service):
        mocked_service.return_value = '123'
        self.data['email'] = 'email@other.com'

        response = self.client.post(self.url, self.data)

        assert 200 == response.status_code
        self.user.refresh_from_db()
        assert self.user.check_password('123') is False
        assert self.user.needs_change_password is False
        assert mocked_service.called is False


class SignUpViewTests(TestCase):

    def setUp(self):
        self.url = reverse('account:sign_up')
        self.data = {'email': 'foo@example.com', 'password1': '123abc', 'password2': '123abc'}

    def test_returns_400_if_invalid_post(self):
        response = self.client.post(self.url, {})
        content = response.json()

        assert 400 == response.status_code
        assert 'email' in content

    def test_create_user(self):
        response = self.client.post(self.url, self.data)

        assert 201 == response.status_code
        user = User.objects.get()
        assert user.email == 'foo@example.com'

    def test_create_token_for_user(self):
        response = self.client.post(self.url, self.data)
        user = User.objects.get()

        key = response.json()['token']
        token = Token.objects.get(key=key)
        assert token.user == user
