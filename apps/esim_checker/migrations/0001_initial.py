from django.db import migrations, models
import apps.esim_checker.models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ESIMCheckerEndpoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('site_url', models.URLField(
                    unique=True,
                    help_text='Origin URL of the registered site (e.g. https://react.driverxmobile.com)'
                )),
                ('secret_key', models.CharField(
                    max_length=16,
                    unique=True,
                    default=apps.esim_checker.models.generate_secret_key,
                    editable=False,
                    help_text='Auto-generated 16-character secret key for this endpoint.'
                )),
                ('is_active', models.BooleanField(
                    default=True,
                    help_text='Deactivate to block API calls from this site without deleting the record.'
                )),
                ('hits_count', models.PositiveIntegerField(
                    default=0,
                    editable=False,
                    help_text='Total number of successful API calls made from this site.'
                )),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('last_hit_at', models.DateTimeField(
                    null=True,
                    blank=True,
                    help_text='Timestamp of the last successful API call.'
                )),
            ],
            options={
                'verbose_name': 'eSIM Checker Endpoint',
                'verbose_name_plural': 'eSIM Checker Endpoints',
                'ordering': ['-created_at'],
            },
        ),
    ]
