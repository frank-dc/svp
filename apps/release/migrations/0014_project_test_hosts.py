# Generated by Django 2.2.3 on 2019-10-21 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0013_auto_20191014_1110'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='test_hosts',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='测试机器'),
        ),
    ]