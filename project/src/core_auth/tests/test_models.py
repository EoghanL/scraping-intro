from model_mommy import mommy

from django.contrib.auth import get_user_model
from django.test import TestCase

from src.core_auth.models import User


class UserModelTests(TestCase):

    def test_use_custom_user_model(self):
        assert get_user_model() is User

    def test_model_config(self):
        assert User.username is None
        assert User.USERNAME_FIELD == 'email'
        assert User.REQUIRED_FIELDS == []

    def test_set_password_changes_needs_change_password(self):
        user = mommy.make(User, needs_change_password=True)
        user.set_password('123')
        user.save()
        user.refresh_from_db()

        assert user.check_password('123') is True
        assert user.needs_change_password is False

    def test_set_password_changes_needs_change_password_for_trye(self):
        user = mommy.make(User, needs_change_password=False)
        user.set_password('123', needs_change_password=True)
        user.save()
        user.refresh_from_db()

        assert user.check_password('123') is True
        assert user.needs_change_password is True

    def test_force_new_password(self):
        user = mommy.make(User, needs_change_password=False)
        user.force_new_password('123')
        user.save()
        user.refresh_from_db()

        assert user.check_password('123') is True
        assert user.needs_change_password is True



class UserModelManagerTests(TestCase):

    def setUp(self):
        self.data = {
            'email': 'email@example.com',
            'first_name': 'First',
            'last_name': 'Last',
            'password': 'passwd',
        }

    def test_create_common_user(self):
        user = User.objects.create_user(**self.data)

        assert bool(user.id) is True
        assert "First Last" == user.get_full_name()
        assert user.check_password('passwd') is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        user = User.objects.create_superuser(**self.data)

        assert bool(user.id) is True
        assert "First Last" == user.get_full_name()
        assert user.check_password('passwd') is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_user_without_password(self):
        self.data.pop('password')

        user = User.objects.create_user_without_password(**self.data)

        assert bool(user.id) is True
        assert "First Last" == user.get_full_name()
        assert '' == user.password
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_raise_value_error_if_no_email(self):
        self.data['email'] = ''
        with self.assertRaises(ValueError):
            User.objects.create_user(**self.data)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**self.data)

    def test_raise_value_error_super_user_not_staff(self):
        self.data['is_staff'] = False
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**self.data)

    def test_raise_value_error_super_user_not_superuser(self):
        self.data['is_superuser'] = False
        with self.assertRaises(ValueError):
            User.objects.create_superuser(**self.data)
