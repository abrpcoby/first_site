# Generated by Django 4.2.3 on 2023-08-22 23:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specs', '0016_specs_title_lower'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specs',
            name='title_lower',
            field=models.CharField(editable=False, max_length=255, verbose_name='Заголовок'),
        ),
    ]
