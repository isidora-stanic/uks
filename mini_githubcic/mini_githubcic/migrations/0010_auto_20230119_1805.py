# Generated by Django 3.2.16 on 2023-01-19 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mini_githubcic', '0009_auto_20230119_1800'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='forked_project',
        ),
        migrations.AddField(
            model_name='project',
            name='forked_project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='forked_projects', to='mini_githubcic.project'),
        ),
    ]
