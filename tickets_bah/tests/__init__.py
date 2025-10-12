"""
Test suite for the tickets_bah application.

Import individual test modules so Django's default test discovery
detects them consistently across environments.
"""

from .test_models import *  # noqa: F401,F403
from .test_utils import *  # noqa: F401,F403
from .test_permissions import *  # noqa: F401,F403
from .test_decorators import *  # noqa: F401,F403
from .test_forms import *  # noqa: F401,F403

__all__ = [
    "UtilisateurModelTests",
    "UtilisateurManagerTests",
    "ReservationModelTests",
    "EnvoyerConfirmationReservationTests",
    "PermissionsTests",
    "LoginRequiredDecoratorTests",
    "RegisterFormTests",
    "LoginFormTests",
]
