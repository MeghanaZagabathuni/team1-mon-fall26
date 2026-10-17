from django.db import migrations

# Services shown in the UI design. Admins can add more in /admin/.
DEFAULT_SERVICE_TYPES = [
    ("Dog walking", "A walk around the neighborhood."),
    ("Pet sitting", "Care for your pet at your home."),
    ("Drop-in visit", "A short visit to feed and check on your pet."),
]


def add_service_types(apps, schema_editor):
    """Give every database the same starting services so owners can book."""
    ServiceType = apps.get_model("caregivers", "ServiceType")
    for name, description in DEFAULT_SERVICE_TYPES:
        ServiceType.objects.get_or_create(
            name=name, defaults={"description": description}
        )


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(add_service_types, migrations.RunPython.noop),
    ]
