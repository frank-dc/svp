# Generated by Django 2.2.3 on 2019-10-13 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('release', '0011_auto_20191013_0045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '待审核'), (1, '已审核'), (3, '已发布'), (4, '作废')], default=0, verbose_name='记录状态'),
        ),
    ]