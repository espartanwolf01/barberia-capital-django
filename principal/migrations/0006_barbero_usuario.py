from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("principal", "0005_pedido_clave_confirmacion"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.AddField(
            model_name="barbero", name="usuario",
            field=models.OneToOneField(
                to=settings.AUTH_USER_MODEL, null=True, blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="barbero",
            ),
        ),
    ]
