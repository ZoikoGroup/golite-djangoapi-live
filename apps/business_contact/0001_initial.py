from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BusinessContact",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("full_name", models.CharField(max_length=255)),
                ("business_name", models.CharField(max_length=255)),
                ("business_email", models.EmailField(max_length=254)),
                ("business_needs", models.CharField(
                    max_length=50,
                    choices=[
                        ("new_plan", "New Plan"),
                        ("plan_upgrade", "Plan Upgrade"),
                        ("troubleshooting", "Troubleshooting"),
                        ("custom_solution", "Custom Solution"),
                        ("other", "Other"),
                    ],
                )),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Business Contact",
                "verbose_name_plural": "Business Contacts",
                "ordering": ["-created_at"],
            },
        ),
    ]
