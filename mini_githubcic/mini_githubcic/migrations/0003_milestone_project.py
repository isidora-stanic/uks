# Generated by Django 3.2.16 on 2023-01-10 16:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('mini_githubcic', '0002_issue_is_open_issue_project_pullrequest_state_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='milestone',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='mini_githubcic.project'),
        ),
    ]
