from django.contrib import admin

from Analytics.models import StatisticType


# Register your models here.
@admin.register(StatisticType)
class StatisticTypeAdmin(admin.ModelAdmin):
    pass
