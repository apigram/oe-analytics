from django.contrib.auth.models import Group, User
from rest_framework import serializers

from Analytics.models import Statistic, StatisticDatapoint, StatisticType


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class StatisticTypeSerializer(serializers.HyperlinkedModelSerializer):
    statistics = serializers.HyperlinkedRelatedField(many=True, view_name='statistic-detail', read_only=True)

    class Meta:
        model = StatisticType
        fields = ['url', 'title', 'x_axis_label', 'y_axis_label', 'statistics']


class StatisticSerializer(serializers.HyperlinkedModelSerializer):
    datapoints = serializers.HyperlinkedRelatedField(many=True, view_name='statisticdatapoint-detail', read_only=True)

    class Meta:
        model = Statistic
        fields = ['url', 'pas_key', 'stat_type', 'eye', 'datapoints']


class StatisticDatapointSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StatisticDatapoint
        fields = ['url', 'statistic', 'x_value', 'y_value', 'event_id', 'event_type']
