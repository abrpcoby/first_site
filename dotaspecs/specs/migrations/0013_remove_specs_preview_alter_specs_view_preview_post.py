# Generated by Django 4.2.3 on 2023-08-15 07:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specs', '0012_alter_specs_preview'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='specs',
            name='preview',
        ),
        migrations.AlterField(
            model_name='specs',
            name='view_preview_post',
            field=models.BooleanField(default=False, verbose_name='Показывать превью в конце поста'),
        ),
    ]