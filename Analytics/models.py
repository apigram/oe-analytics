from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import gettext_lazy as _
import pandas as pd
from sklearn.linear_model import LinearRegression
import threading


class StatisticType(models.Model):
    title = models.CharField(max_length=100)
    x_axis_label = models.CharField(max_length=100)
    y_axis_label = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    def get_patient_statistic(self, pas_key):
        return Statistic.objects.get(stat_type_id=self.id, pas_key=pas_key)


class Statistic(models.Model):
    class Eye(models.TextChoices):
        LEFT = 'L', _('Left')
        RIGHT = 'R', _('Right')

    pas_key = models.CharField(max_length=100)
    stat_type = models.ForeignKey(StatisticType, on_delete=models.CASCADE, related_name='statistics', related_query_name='statistic')
    eye = models.CharField(null=True, max_length=1, choices=Eye.choices, default=None)
    gradient = models.FloatField(null=True)
    y_intercept = models.FloatField(null=True)

    def __str__(self):
        return self.pas_key + ' - ' + str(self.stat_type) + ('(' + self.eye + ')' if self.eye else '')

    def predict_y(self, x):
        return self.gradient * x + self.y_intercept

    def run_linear_regression(self):
        t = threading.Thread(target=do_linear_regression, args=[self])
        t.daemon = True
        t.start()


def do_linear_regression(stat):
    d = stat.datapoints.all().values('x_value', 'y_value')
    df = pd.DataFrame.from_records(d)
    x_train = df[["x_value"]]
    y_train = df[["y_value"]]
    model = LinearRegression()
    model.fit(x_train, y_train)
    stat.gradient = model.coef_[0][0]
    stat.y_intercept = model.intercept_[0]
    stat.save()


class StatisticDatapoint(models.Model):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE, related_name='datapoints', related_query_name='datapoint')
    x_value = models.FloatField()
    y_value = models.FloatField()
    event_id = models.IntegerField(null=True)
    event_type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.statistic.pas_key + ' (' + str(self.x_value) + ', ' + str(self.y_value) + ')'


def on_datapoints_altered(sender, instance, **kwargs):
    instance.statistic.run_linear_regression()


post_save.connect(on_datapoints_altered, sender=StatisticDatapoint)
post_delete.connect(on_datapoints_altered, sender=StatisticDatapoint)
