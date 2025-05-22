from tickets_bah.constance.user_role import roles_admin
from tickets_bah.models import Utilisateur
from tickets_bah.constance import user_role

def is_super_admin(user: Utilisateur):
    if not user.is_authenticated:
        return False
    
    return user.is_authenticated and user.is_superuser


def is_admin(user: Utilisateur):
    if not user.is_authenticated:
        return False
    return user.default_role in roles_admin


def can_access_app_admin(user: Utilisateur):
    roles = [
        user_role.super_admin
    ]
    _rolescheck = list(user.rolesArray())
    if not user.is_authenticated:
        return False

    for rlc in _rolescheck:
        if rlc in roles:
            return True
    return False


def user_is_authenticate(user: Utilisateur):
    roles = [
        user_role.super_admin,
        user_role.user,
    ]
    if not user.is_authenticated or user.is_anonymous:
        return False

    print(f"User {user} - default_role: {user.default_role}")  # Debug
    if user.default_role in roles:
        return True
    return False

def admin_is_authenticate(user: Utilisateur):
    roles = [
        user_role.super_admin,
    ]
    if not user.is_authenticated or user.is_anonymous:
        return False

    print(f"User {user} - default_role: {user.default_role}")  # Debug
    if user.default_role in roles:
        return True
    return False
