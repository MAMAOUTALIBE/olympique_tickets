import os
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import TestCase, override_settings

from tickets_bah.models import Offre, Reservation, Utilisateur


class UtilisateurModelTests(TestCase):
    def test_creation_utilisateur_via_manager(self):
        user = Utilisateur.objects.create_user(
            email="bah@example.com",
            password="motdepasse",
            nom="Bah",
            prenom="Mamadou",
            default_role="user",
            cle_utilisateur="CLE-12345",
        )

        self.assertEqual(user.nom, "Bah")
        self.assertEqual(user.prenom, "Mamadou")
        self.assertTrue(user.check_password("motdepasse"))


class UtilisateurManagerTests(TestCase):
    def test_create_user_hashes_password(self):
        user = Utilisateur.objects.create_user(
            email="utilisateur@example.com",
            password="secret",
            nom="Jean",
            prenom="Dupont",
            cle_utilisateur="CLE-67890",
        )

        self.assertNotEqual(user.password, "secret")
        self.assertTrue(user.check_password("secret"))

    def test_create_superuser_sets_flags(self):
        admin = Utilisateur.objects.create_superuser(
            email="admin@example.com",
            password="adminpass",
            nom="Admin",
            prenom="User",
            cle_utilisateur="CLE-ADMIN",
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.default_role, "super-admin")


class ReservationModelTests(TestCase):
    def setUp(self):
        self.utilisateur = Utilisateur.objects.create_user(
            email="client@example.com",
            password="pass1234",
            nom="Client",
            prenom="Test",
            cle_utilisateur="CLE-CLIENT",
        )
        self.offre = Offre.objects.create(
            nom="Billet Solo",
            description="Accès pour une personne",
            prix=100,
            nombre_de_places=10,
        )

    def test_offre_places_restantes_initialisee(self):
        self.assertEqual(self.offre.places_restantes, self.offre.nombre_de_places)

    def test_reservation_str(self):
        reservation = Reservation.objects.create(
            utilisateur=self.utilisateur,
            offre=self.offre,
            cle_billet="unique_key",
        )
        self.assertIn(self.utilisateur.nom, str(reservation))
        self.assertIn(self.offre.nom, str(reservation))

    def test_generate_qr_code_creates_image_file(self):
        reservation = Reservation.objects.create(
            utilisateur=self.utilisateur,
            offre=self.offre,
            cle_billet="unique_key_qr",
        )

        with TemporaryDirectory() as tmpdir, override_settings(MEDIA_ROOT=tmpdir):
            reservation.generate_qr_code()
            reservation.save()

            self.assertTrue(reservation.qr_code.name.endswith(".png"))
            stored_file = Path(tmpdir) / reservation.qr_code.name

            self.assertTrue(stored_file.exists())
            self.assertGreater(stored_file.stat().st_size, 0)
