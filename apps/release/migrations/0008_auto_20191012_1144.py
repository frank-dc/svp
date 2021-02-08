# Generated by Django 2.2.3 on 2019-10-12 11:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0007_auto_20191011_1721'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='record',
            name='if_approve',
        ),
        migrations.AddField(
            model_name='record',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '待审核'), (1, '已审核'), (2, '待发布'), (3, '已发布')], default=0, verbose_name='记录状态'),
        ),
    ]
