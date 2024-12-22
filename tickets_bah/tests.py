from django.test import TestCase

from tickets_bah.models import Utilisateur


# Create your tests here.

class UtilisateurTest(TestCase):
    def test_creation_utilisateur(self):
        user = Utilisateur.objects.create(
            nom="bah",
            prenom="mamadou",
            email="bah@gmail.com",
            mot_de_pass="bah",
            cle_utilisateur="CLE-12345"
        )
        self.assertEqual(user.nom, "bah")
        self.assertEqual(user.prenom, "mamadou")
