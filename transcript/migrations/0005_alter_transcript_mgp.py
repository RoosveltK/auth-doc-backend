# Generated by Django 4.0.3 on 2022-04-06 03:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcript', '0004_alter_evaluation_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transcript',
            name='mgp',
            field=models.DecimalField(decimal_places=2, max_digits=3),
        ),
    ]
