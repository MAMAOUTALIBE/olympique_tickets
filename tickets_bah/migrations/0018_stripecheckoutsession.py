from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tickets_bah", "0017_loginverificationtoken"),
    ]

    operations = [
        migrations.CreateModel(
            name="StripeCheckoutSession",
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
                ("stripe_session_id", models.CharField(max_length=255, unique=True)),
                (
                    "stripe_payment_intent_id",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("is_completed", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "offre",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checkout_sessions",
                        to="tickets_bah.offre",
                    ),
                ),
                (
                    "reservation",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="checkout_session",
                        to="tickets_bah.reservation",
                    ),
                ),
                (
                    "utilisateur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="checkout_sessions",
                        to="tickets_bah.utilisateur",
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
                "indexes": [
                    models.Index(fields=["stripe_session_id"], name="tickets_bah_stripe_session_idx"),
                    models.Index(fields=["utilisateur", "offre", "is_completed"], name="tickets_bah_session_status_idx"),
                ],
            },
        ),
    ]
