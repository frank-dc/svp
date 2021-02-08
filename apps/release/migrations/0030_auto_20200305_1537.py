# Generated by Django 2.2.3 on 2020-03-05 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0029_auto_20191214_1221'),
    ]

    operations = [
        migrations.AddField(
            model_name='git',
            name='test_branch',
            field=models.CharField(default='test', max_length=32, verbose_name='测试环境分支名称'),
        ),
        migrations.AlterField(
            model_name='git',
            name='branch',
            field=models.CharField(default='master', max_length=32, verbose_name='线上环境分支名称'),
        ),
    ]
