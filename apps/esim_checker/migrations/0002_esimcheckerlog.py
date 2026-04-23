import apps.esim_checker.models
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('esim_checker', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ESIMCheckerLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(
                    db_index=True,
                    help_text='IMEI number that was checked.',
                    max_length=20,
                    unique=True,
                )),
                ('url', models.CharField(
                    help_text='VCare API URL that returned the successful response.',
                    max_length=512,
                )),
                ('created_date', models.DateTimeField(
                    default=django.utils.timezone.now,
                    help_text='UTC timestamp when this IMEI was first successfully checked.',
                )),
                ('hit_count', models.PositiveIntegerField(
                    default=1,
                    help_text='How many times this cached result has been served (starts at 1 on first insert).',
                )),
                ('cached_response', models.JSONField(
                    help_text='Full JSON response payload from the VCare API.',
                )),
            ],
            options={
                'verbose_name': 'eSIM Checker Log',
                'verbose_name_plural': 'eSIM Checker Logs',
                'ordering': ['-created_date'],
            },
        ),
    ]
