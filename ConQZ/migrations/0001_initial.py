# Generated by Django 4.1.4 on 2022-12-31 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('Snumber', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='学号')),
                ('Name', models.CharField(default='', max_length=20, verbose_name='名称')),
                ('PasswordQZ', models.CharField(default='', max_length=50, verbose_name='强智密码')),
                ('Classname', models.CharField(default='', max_length=50, verbose_name='班级名称')),
                ('Majorname', models.CharField(default='', max_length=50, verbose_name='专业名称')),
                ('Collegename', models.CharField(default='', max_length=50, verbose_name='学院名称')),
                ('Enteryear', models.IntegerField(default='', verbose_name='入学年份')),
                ('Gradenumber', models.IntegerField(default='', verbose_name='当前年级')),
            ],
        ),
    ]
