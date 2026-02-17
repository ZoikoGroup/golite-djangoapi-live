from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE auth_user ADD COLUMN vc_enrollment_id VARCHAR(100);",
            reverse_sql="ALTER TABLE auth_user DROP COLUMN vc_enrollment_id;",
        ),
    ]
