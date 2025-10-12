"""
Compat shim so that ``python manage.py test`` without labels still discovers
the test modules placed under ``tickets_bah/tests/``.
"""

from . import tests as _tests_package
from .tests import *  # noqa: F401,F403

__all__ = getattr(_tests_package, "__all__", [])
