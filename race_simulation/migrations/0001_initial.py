# Generated by Django 4.1.4 on 2022-12-26 04:46

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RaceData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('race_id', models.CharField(max_length=20)),
                ('total_time1', models.FloatField()),
                ('up_time1', models.FloatField()),
                ('total_time2', models.FloatField()),
                ('up_time2', models.FloatField()),
                ('total_time3', models.FloatField()),
                ('up_time3', models.FloatField()),
                ('total_time4', models.FloatField()),
                ('up_time4', models.FloatField()),
                ('total_time5', models.FloatField()),
                ('up_time5', models.FloatField()),
                ('total_time6', models.FloatField()),
                ('up_time6', models.FloatField()),
                ('total_time7', models.FloatField()),
                ('up_time7', models.FloatField()),
                ('total_time8', models.FloatField()),
                ('up_time8', models.FloatField()),
                ('total_time9', models.FloatField()),
                ('up_time9', models.FloatField()),
                ('total_time10', models.FloatField()),
                ('up_time10', models.FloatField()),
                ('total_time11', models.FloatField()),
                ('up_time11', models.FloatField()),
                ('total_time12', models.FloatField()),
                ('up_time12', models.FloatField()),
                ('total_time13', models.FloatField()),
                ('up_time13', models.FloatField()),
                ('total_time14', models.FloatField()),
                ('up_time14', models.FloatField()),
                ('total_time15', models.FloatField()),
                ('up_time15', models.FloatField()),
                ('total_time16', models.FloatField()),
                ('up_time16', models.FloatField()),
                ('total_time17', models.FloatField()),
                ('up_time17', models.FloatField()),
                ('total_time18', models.FloatField()),
                ('up_time18', models.FloatField()),
            ],
        ),
    ]
