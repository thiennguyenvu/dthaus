# Generated by Django 3.0.10 on 2021-03-13 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_taskfiles_date_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='taskfiles',
            name='date_approved',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
