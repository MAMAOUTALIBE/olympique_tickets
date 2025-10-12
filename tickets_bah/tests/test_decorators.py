from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from tickets_bah.views import login_required


@login_required
def sample_view(request):
    return HttpResponse("OK")


class LoginRequiredDecoratorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _add_session(self, request):
        middleware = SessionMiddleware(lambda req: HttpResponse(""))
        middleware.process_request(request)
        request.session.save()

    def test_redirect_when_user_not_in_session(self):
        request = self.factory.get("/protected")
        self._add_session(request)

        response = sample_view(request)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_allows_access_when_user_in_session(self):
        request = self.factory.get("/protected")
        self._add_session(request)
        request.session["user_id"] = 1

        response = sample_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"OK")
