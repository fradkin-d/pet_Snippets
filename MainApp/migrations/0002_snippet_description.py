# Generated by Django 4.1 on 2022-09-15 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='snippet',
            name='description',
            field=models.CharField(default='', max_length=250),
        ),
    ]
