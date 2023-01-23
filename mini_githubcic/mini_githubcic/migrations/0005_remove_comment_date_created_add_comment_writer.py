
from django.db import migrations, models
import django.utils.timezone
import ckeditor.fields
import colorfield.fields


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
        migrations.AlterField(
            model_name='comment',
            name='content',
            field=ckeditor.fields.RichTextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='label',
            name='color',
            field=colorfield.fields.ColorField(default='#00000', image_field=None, max_length=18, samples=None),
        ),
    ]
