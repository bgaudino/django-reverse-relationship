# Generated by Django 5.0.3 on 2024-03-11 19:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tests", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Nutrition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "topping",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tests.topping"
                    ),
                ),
            ],
        ),
    ]
