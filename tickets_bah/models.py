from unicodedata import decimal
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Hashage automatique du mot de passe
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

# Modèle utilisateur personnalisé
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Identifiant principal
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'  # Champ utilisé pour l'authentification
    REQUIRED_FIELDS = ['nom', 'prenom']

    def __str__(self):
        return self.email

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
     utilisateur = models.ForeignKey('tickets_bah.Utilisateur', on_delete=models.CASCADE)
     offre = models.ForeignKey('tickets_bah.Offre', on_delete=models.CASCADE)
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

#CREATION DU PANIER
class Panier(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='paniers')
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE,)
    date_ajout = models.DateField(auto_now_add=True)

    def __str__(self):
        return f'{self.utilisateur.nom} {self.offre.nom}'


