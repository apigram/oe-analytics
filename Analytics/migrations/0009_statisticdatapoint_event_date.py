# Generated by Django 5.0 on 2023-12-08 01:08

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Analytics', '0008_statistic_gradient_statistic_y_intercept'),
    ]

    operations = [
        migrations.AddField(
            model_name='statisticdatapoint',
            name='event_date',
            field=models.DateTimeField(default=datetime.datetime(2023, 12, 8, 12, 8, 47, 332489)),
        ),
    ]
