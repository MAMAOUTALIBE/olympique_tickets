from django.db import migrations, models
import django.utils.timezone


def set_default_quantity(apps, schema_editor):
    Session = apps.get_model("tickets_bah", "StripeCheckoutSession")
    Session.objects.filter(quantity__isnull=True).update(quantity=1)


class Migration(migrations.Migration):

    dependencies = [
        ("tickets_bah", "0019_offre_places_restantes"),
    ]

    operations = [
        migrations.AddField(
            model_name="stripecheckoutsession",
            name="hold_expires_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="stripecheckoutsession",
            name="quantity",
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AddIndex(
            model_name="stripecheckoutsession",
            index=models.Index(
                fields=["offre", "is_completed", "hold_expires_at"],
                name="tickets_bah_session_hold_idx",
            ),
        ),
        migrations.RunPython(set_default_quantity, migrations.RunPython.noop),
    ]
