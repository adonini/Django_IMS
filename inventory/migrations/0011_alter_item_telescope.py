# Generated by Django 4.2.9 on 2024-09-23 10:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0010_alter_telescope_structure_table'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='telescope',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.telescope_structure'),
        ),
    ]
