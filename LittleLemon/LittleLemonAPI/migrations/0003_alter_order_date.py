# Generated by Django 4.1.5 on 2023-01-25 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("LittleLemonAPI", "0002_alter_orderitem_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="date",
            field=models.DateTimeField(db_index=True),
        ),
    ]