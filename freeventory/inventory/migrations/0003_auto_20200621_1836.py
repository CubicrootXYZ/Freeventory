# Generated by Django 3.0.7 on 2020-06-21 16:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_auto_20200621_1258'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lend',
            name='lend_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lend',
            name='lend_finish',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='lend',
            name='lend_start',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
