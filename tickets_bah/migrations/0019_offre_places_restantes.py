from django.db import migrations, models


def init_places_restantes(apps, schema_editor):
    Offre = apps.get_model("tickets_bah", "Offre")
    for offre in Offre.objects.all():
        try:
            total = int(offre.nombre_de_places)
        except (TypeError, ValueError):
            total = 0
        Offre.objects.filter(pk=offre.pk).update(
            places_restantes=total,
            nombre_de_places=total,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("tickets_bah", "0018_stripecheckoutsession"),
    ]

    operations = [
        migrations.AddField(
            model_name="offre",
            name="places_restantes",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.RunPython(init_places_restantes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="offre",
            name="nombre_de_places",
            field=models.PositiveIntegerField(),
        ),
    ]
