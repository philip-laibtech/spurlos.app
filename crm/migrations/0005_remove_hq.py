from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crm", "0004_alter_contact_salutation"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="companylocation",
            name="unique_company_hq",
        ),
        migrations.RemoveIndex(
            model_name="companylocation",
            name="crm_company_is_head_1ee862_idx",
        ),
        migrations.RemoveField(
            model_name="companylocation",
            name="is_headquarters",
        ),
        migrations.RemoveField(
            model_name="company",
            name="hq_location",
        ),
    ]
