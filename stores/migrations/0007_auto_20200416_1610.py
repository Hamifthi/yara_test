# Generated by Django 3.0.5 on 2020-04-16 11:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stores', '0006_auto_20200416_1125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='store',
            name='products',
        ),
        migrations.AddField(
            model_name='product',
            name='store',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='stores.Store'),
        ),
    ]