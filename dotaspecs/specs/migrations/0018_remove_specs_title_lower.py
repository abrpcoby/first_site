# Generated by Django 4.2.3 on 2023-08-22 23:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('specs', '0017_alter_specs_title_lower'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specs',
            name='title_lower',
        ),
    ]
