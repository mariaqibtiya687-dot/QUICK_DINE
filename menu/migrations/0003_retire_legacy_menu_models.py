"""Retire legacy model state without deleting the existing database tables."""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('menu', '0002_menuitem'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.DeleteModel(name='FoodItem'),
                migrations.DeleteModel(name='Category'),
            ],
        ),
    ]
