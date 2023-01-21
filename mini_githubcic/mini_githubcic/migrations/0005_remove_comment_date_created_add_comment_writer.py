
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('mini_githubcic', '0004_alter_commit_parents'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='date_created',
        ),
        migrations.AddField(
            model_name='comment',
            name='writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='writer', to='mini_githubcic.user'),
        ),
    ]
