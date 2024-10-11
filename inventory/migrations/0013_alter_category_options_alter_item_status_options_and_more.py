# Generated by Django 4.2.9 on 2024-10-02 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0012_alter_item_status'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='item_status',
            options={'verbose_name': 'Item Status', 'verbose_name_plural': 'Item Statuses'},
        ),
        migrations.AlterModelOptions(
            name='payment_sources',
            options={'verbose_name': 'Payment Source', 'verbose_name_plural': 'Payment Sources'},
        ),
        migrations.AlterModelOptions(
            name='purchase_group',
            options={'verbose_name': 'Purchase Group', 'verbose_name_plural': 'Purchase Groups'},
        ),
        migrations.AlterModelOptions(
            name='purchase_status',
            options={'verbose_name': 'Purchase Status', 'verbose_name_plural': 'Purchase Statuses'},
        ),
        migrations.AlterModelOptions(
            name='stock',
            options={'verbose_name': 'Stock', 'verbose_name_plural': 'Stock'},
        ),
        migrations.AlterModelOptions(
            name='stock_type',
            options={'verbose_name': 'Stock Type', 'verbose_name_plural': 'Stock Types'},
        ),
        migrations.AlterModelOptions(
            name='sub_category',
            options={'verbose_name': 'Sub-category', 'verbose_name_plural': 'Sub-categories'},
        ),
        migrations.AlterField(
            model_name='item',
            name='code',
            field=models.CharField(max_length=150, blank=False, null=False),
            preserve_default=False,
        ),
    ]
