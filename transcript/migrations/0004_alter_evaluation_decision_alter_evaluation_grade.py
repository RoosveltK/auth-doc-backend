# Generated by Django 4.0.3 on 2022-05-06 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transcript', '0003_evaluation_examen'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evaluation',
            name='decision',
            field=models.CharField(blank=True, default=None, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='evaluation',
            name='grade',
            field=models.CharField(blank=True, default=None, max_length=5, null=True),
        ),
    ]
