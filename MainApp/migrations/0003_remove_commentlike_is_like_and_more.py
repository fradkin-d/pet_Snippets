# Generated by Django 4.1 on 2022-08-24 18:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MainApp', '0002_comment_snippetlike_commentlike'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='commentlike',
            name='is_like',
        ),
        migrations.RemoveField(
            model_name='snippetlike',
            name='is_like',
        ),
    ]
