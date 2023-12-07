from django.db import models
from django.utils.translation import gettext_lazy as _


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

    def __str__(self):
        return self.pas_key + ' - ' + str(self.stat_type) + ('(' + self.eye + ')' if self.eye else '')


class StatisticDatapoint(models.Model):
    statistic = models.ForeignKey(Statistic, on_delete=models.CASCADE, related_name='datapoints', related_query_name='datapoint')
    x_value = models.FloatField()
    y_value = models.FloatField()
    event_id = models.IntegerField(null=True)
    event_type = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.statistic.pas_key + ' (' + str(self.x_value) + ', ' + str(self.y_value) + ')'
