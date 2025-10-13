from unicodedata import decimal
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.utils import timezone
from django.utils.timezone import now 
from io import BytesIO
from math import frexp
import qrcode
from django.core.files.base import ContentFile

ROLES = (
    ("super-admin", "super-admin"),
    ("user", "user"),
)

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
        extra_fields.setdefault('default_role', "super-admin")
        return self.create_user(email, password, **extra_fields)

# Modèle utilisateur personnalisé
class Utilisateur(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)  # Identifiant principal
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=255, null=True)
    default_role = models.CharField(choices=ROLES, max_length=30, default="user", null=True)
    cle_utilisateur = models.CharField(max_length=100, unique=True, null=True)
    is_superuser = models.BooleanField(default=False, null=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=64, null=True, blank=True)
    totp_secret = models.CharField(max_length=32, null=True, blank=True)
    is_totp_enabled = models.BooleanField(default=False)

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
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.nom

#Model Rservation
class Reservation(models.Model):
    utilisateur = models.ForeignKey('Utilisateur', on_delete=models.CASCADE)
    offre = models.ForeignKey('Offre', on_delete=models.CASCADE)
    cle_billet = models.CharField(max_length=100, unique=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f"Reservation pour {self.utilisateur.nom} - {self.offre.nom}"

    def generate_qr_code(self):
        """ Génère un QR code et l'enregistre dans le champ qr_code """
        qr_data = f"{self.utilisateur.cle_utilisateur} - {self.cle_billet}"
        qr = qrcode.make(qr_data)
        buffer = BytesIO()
        qr.save(buffer, format='PNG')

        # Sauvegarder l'image dans le champ qr_code
        self.qr_code.save(f"qrcode_{self.id}.png", ContentFile(buffer.getvalue()), save=False)

#configuration de l'authentification
class UtilisateurProfile(models.Model):
    nom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    cle_utilisateur = models.CharField(max_length=255,unique=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

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
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return f'{self.utilisateur.nom} {self.offre.nom}'
    
class UtilisateurPayment(models.Model):
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)
    offre = models.ForeignKey(Offre, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.PositiveIntegerField()
    currency = models.CharField(max_length=3)
    has_paid = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    # Champs Stripe
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_payment_method_id = models.CharField(max_length=255, blank=True, null=True)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)

    def __str__(self):
        return f"{self.utilisateur.nom} {self.utilisateur.prenom} - {self.offre.nom} - Paid: {self.has_paid}"


class SportEvent(models.Model):
    nom = models.CharField(max_length=150)
    discipline = models.CharField(max_length=150, blank=True)
    lieu = models.CharField(max_length=150, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="sports", blank=True, null=True)
    createdAt = models.DateTimeField(auto_now_add=True, null=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ["-createdAt"]

    def __str__(self):
        return self.nom


class LoginVerificationToken(models.Model):
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name="login_tokens",
    )
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def is_expired(self):
        expiration_minutes = getattr(
            settings,
            "LOGIN_EMAIL_TOKEN_EXPIRATION_MINUTES",
            10,
        )
        return timezone.now() > self.created_at + timedelta(minutes=expiration_minutes)
