# Generated by Django 2.2.3 on 2020-03-05 18:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0031_auto_20200305_1705'),
    ]

    operations = [
        migrations.AddField(
            model_name='git',
            name='git_pid',
            field=models.IntegerField(blank=True, null=True, verbose_name='GitLab项目ID'),
        ),
    ]