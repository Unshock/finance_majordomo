from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db.utils import IntegrityError
from .setting import SettingsUsers
from ..models import User
from ...stocks.tests.base_settings import BaseTest


class UsersModelsTest(BaseTest):

    def test_models_params(self):
        self.assertEqual(self.user_authenticated.username,
                         "user1")
        self.assertEqual(self.user_authenticated.first_name, "Ivan")
        self.assertEqual(self.user_authenticated.last_name, "Ivanov")
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(
            self.user_authenticated_no_assets._meta
                .get_field('creation_date').verbose_name, _("Creation_date"))

    def test_username_validation_fail(self):
        username_invalid = 'x$'

        user_invalid = User.objects.create(
            username=username_invalid,
            first_name='A',
            last_name='B',
            password="qwerty123UIOP"
        )

        with self.assertRaises(ValidationError):
            user_invalid.full_clean()


    def test_unique_name_validation_fail(self):
        name_ununique = "user1"

        with self.assertRaises(IntegrityError):
            user_invalid = User.objects.create(
                username=name_ununique,
                first_name='A',
                last_name='B',
                password="qwerty123UIOP"
            )
