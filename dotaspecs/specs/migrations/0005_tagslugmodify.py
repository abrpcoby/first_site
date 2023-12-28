# Generated by Django 4.2.3 on 2023-08-13 04:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('specs', '0004_alter_specs_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagSlugModify',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=30)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]