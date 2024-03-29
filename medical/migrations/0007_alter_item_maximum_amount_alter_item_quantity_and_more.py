# Generated by Django 4.2.9 on 2024-02-07 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medical', '0006_auto_20230718_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='maximum_amount',
            field=models.DecimalField(blank=True, db_column='MaximumAmount', decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='item',
            name='quantity',
            field=models.DecimalField(blank=True, db_column='Quantity', decimal_places=2, max_digits=18, null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='maximum_amount',
            field=models.DecimalField(blank=True, db_column='MaximumAmount', decimal_places=2, max_digits=18, null=True),
        ),
    ]
