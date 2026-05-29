from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("activities", "0001_initial"),
        ("crm", "0004_alter_contact_salutation"),
    ]

    operations = [
        # First delete any rows whose company is NULL (safety net for dev data)
        migrations.RunSQL(
            "DELETE FROM activities_activity WHERE company_id IS NULL;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Make contact nullable
        migrations.AlterField(
            model_name="activity",
            name="contact",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="activities",
                to="crm.contact",
            ),
        ),
        # Make company required (non-nullable, PROTECT)
        migrations.AlterField(
            model_name="activity",
            name="company",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="activities",
                to="crm.company",
            ),
        ),
    ]
