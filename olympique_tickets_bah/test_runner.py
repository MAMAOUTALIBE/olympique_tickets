from django.test.runner import DiscoverRunner


class DefaultAppDiscoverRunner(DiscoverRunner):
    """
    Ensure ``manage.py test`` without explicit labels exercises the project apps.
    """

    default_test_labels = ("tickets_bah.tests", "appAdmin.tests")

    def build_suite(self, test_labels=None, extra_tests=None, **kwargs):
        if not test_labels:
            test_labels = self.default_test_labels
        return super().build_suite(test_labels, extra_tests=extra_tests, **kwargs)
