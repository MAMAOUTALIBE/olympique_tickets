from unicodedata import decimal
from django.contrib.auth.hashers import make_password, check_password
from django.db import models

class Utilisateur(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    mot_de_pass= models.CharField(max_length=255)
    cle_utilisateur = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.nom} {self.prenom}'
#Model offres
class Offre(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.IntegerField()
    nombre_de_places = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

#Model Rservation
class Reservation(models.Model):
     utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
     offre = models.ForeignKey(Offre, on_delete=models.CASCADE)
     cle_billet = models.CharField(max_length=255)
     qr_code = models.ImageField(upload_to='qr_codes/') #fichier qr code associé

     def __str__(self):
         return f'{self.utilisateur} {self.offre}'
#configuration de l'authentification

class UtilisateurProfile(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    cle_utilisateur = models.CharField(max_length=255,unique=True)

    def set_password(self, raw_password):
        self.mot_de_passe = make_password(raw_password, self.mot_de_passe)

    def check_password(self, raw_password):
        return check_password(raw_password, self.mot_de_passe)
    def __str__(self):
        return f'{self.nom} {self.prenom}'

