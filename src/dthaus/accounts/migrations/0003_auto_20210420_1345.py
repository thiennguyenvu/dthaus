# Generated by Django 3.0.10 on 2021-04-20 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20210420_1338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermanagement',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatar/user-'),
        ),
    ]
