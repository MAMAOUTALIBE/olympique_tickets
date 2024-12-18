# Generated by Django 5.1.4 on 2024-12-14 14:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Offre",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("prix", models.IntegerField()),
                ("nombre_de_places", models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name="Utilisateur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=50)),
                ("prenom", models.CharField(max_length=50)),
                ("email", models.EmailField(max_length=254, unique=True)),
                ("mot_de_pass", models.CharField(max_length=255)),
                ("cle_utilisateur", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="Reservation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cle_billet", models.CharField(max_length=255)),
                ("qr_code", models.ImageField(upload_to="qr_codes/")),
                (
                    "offre",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tickets_bah.offre",
                    ),
                ),
                (
                    "utilisateur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tickets_bah.utilisateur",
                    ),
                ),
            ],
        ),
    ]
