# Generated by Django 5.1.4 on 2024-12-16 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tickets_bah", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UtilisateurProfile",
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
                ("cle_utilisateur", models.CharField(max_length=255, unique=True)),
            ],
        ),
    ]