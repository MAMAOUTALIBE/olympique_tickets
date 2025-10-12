from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from tickets_bah.core import permissions
from tickets_bah.constance import user_role
from tickets_bah.models import Utilisateur


class DummyUser:
    def __init__(self, roles, is_authenticated=True):
        self._roles = roles
        self.is_authenticated = is_authenticated
        self.is_anonymous = not is_authenticated

    def rolesArray(self):
        return self._roles


class PermissionsTests(TestCase):
    def setUp(self):
        self.super_admin = Utilisateur.objects.create_user(
            email="admin@example.com",
            password="adminpass",
            nom="Admin",
            prenom="User",
            default_role=user_role.super_admin,
            cle_utilisateur="CLE-ADMIN",
        )
        self.super_admin.is_superuser = True
        self.super_admin.is_staff = True
        self.super_admin.save(update_fields=["is_superuser", "is_staff"])

        self.standard_user = Utilisateur.objects.create_user(
            email="user@example.com",
            password="userpass",
            nom="User",
            prenom="Standard",
            default_role=user_role.user,
            cle_utilisateur="CLE-USER",
        )

    def test_is_super_admin(self):
        self.assertTrue(permissions.is_super_admin(self.super_admin))
        self.assertFalse(permissions.is_super_admin(self.standard_user))

    def test_is_admin(self):
        self.assertTrue(permissions.is_admin(self.super_admin))
        self.assertFalse(permissions.is_admin(self.standard_user))

    def test_user_is_authenticate(self):
        self.assertTrue(permissions.user_is_authenticate(self.super_admin))
        self.assertTrue(permissions.user_is_authenticate(self.standard_user))
        self.assertFalse(permissions.user_is_authenticate(AnonymousUser()))

    def test_admin_is_authenticate(self):
        self.assertTrue(permissions.admin_is_authenticate(self.super_admin))
        self.assertFalse(permissions.admin_is_authenticate(self.standard_user))

    def test_can_access_app_admin(self):
        admin_candidate = DummyUser([user_role.super_admin], is_authenticated=True)
        self.assertTrue(permissions.can_access_app_admin(admin_candidate))

        regular_candidate = DummyUser([user_role.user], is_authenticated=True)
        self.assertFalse(permissions.can_access_app_admin(regular_candidate))

        anonymous_candidate = DummyUser([user_role.super_admin], is_authenticated=False)
        self.assertFalse(permissions.can_access_app_admin(anonymous_candidate))
