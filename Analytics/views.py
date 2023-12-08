from django.contrib.auth.models import Group, User
from rest_framework import permissions, viewsets
from Analytics.models import Statistic, StatisticDatapoint, StatisticType
import Analytics.serializers as serializers
from django.shortcuts import render
from plotly.offline import plot
import plotly.graph_objs as go
from .forms import PlotForm


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class StatisticTypeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = StatisticType.objects.all()
    serializer_class = serializers.StatisticTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class StatisticViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Statistic.objects.all()
    serializer_class = serializers.StatisticSerializer
    permission_classes = [permissions.IsAuthenticated]


class StatisticDatapointViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = StatisticDatapoint.objects.all()
    serializer_class = serializers.StatisticDatapointSerializer
    permission_classes = [permissions.IsAuthenticated]


def get_datapoints(statistic):
    x_data = []
    y_data = []
    min_x = statistic.datapoints.order_by('x_value')[0]
    max_x = statistic.datapoints.order_by('-x_value')[0]
    min_y = statistic.gradient * min_x.x_value + statistic.y_intercept
    max_y = statistic.gradient * max_x.x_value + statistic.y_intercept
    trend_x = [min_x.x_value, max_x.x_value]
    trend_y = [min_y, max_y]
    customdata = []
    for datapoint in statistic.datapoints.all():
        x_data.append(datapoint.x_value)
        y_data.append(datapoint.y_value)
        customdata.append((datapoint.event_id, datapoint.event_type))
    fig = go.Figure()

    plot_color = 'green' if statistic.eye == 'R' else 'red'

    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        customdata=customdata,
        name=statistic.stat_type.title,
        marker=dict(
            color=plot_color
        ),
    ))
    fig.add_trace(go.Scatter(
        x=trend_x,
        y=trend_y,
        mode='lines',
        name=statistic.stat_type.title + ' Rate',
        marker=dict(
            color=plot_color
        ),
    ))
    fig.update_layout(
        title=statistic.stat_type.title + ' (Patient ' + statistic.pas_key + ')',
    )
    return plot(fig, output_type='div', include_plotlyjs=False, show_link=False, link_text="")


def get_scatterlines(rate, statistic_type, eye):
    stats = Statistic.objects.filter(gradient=rate)
    x_data = []
    y_data = []
    customdata = []
    for stat in stats:
        min_x = stat.datapoints.order_by('x_value')[0]
        max_x = stat.datapoints.order_by('-x_value')[0]
        x_data.append(min_x.x_value)
        y_data.append(stat.gradient * min_x.x_value + stat.y_intercept)
        x_data.append(max_x.x_value)
        y_data.append(stat.gradient * max_x.x_value + stat.y_intercept)
        customdata.append(stat.id)
        customdata.append(stat.id)

    fig = go.Figure()

    plot_color = 'green' if eye == 'R' else 'red'

    fig.add_trace(go.Scatter(
        x=x_data,
        y=y_data,
        customdata=customdata,
        name=statistic_type.title,
        marker=dict(
            color=plot_color
        ),
    ))
    fig.update_layout(
        title=statistic_type.title,
    )
    return plot(fig, output_type='div', include_plotlyjs=False, show_link=False, link_text="")


def get_rate_plot(statistic_type, eye):
    x_data = []
    y_data = []
    if eye:
        stats = statistic_type.statistics.filter(eye=eye)
        plot_color = 'green' if eye == 'R' else 'red'
    else:
        stats = statistic_type.statistics.all()
        plot_color = 'green'
    for stat in stats:
        if stat.gradient in x_data:
            x_data.append(stat.gradient)
            y_data[x_data.index(stat.gradient)] += 1
        else:
            x_data.append(stat.gradient)
            y_data.append(1)

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=x_data,
        y=y_data,
        name=statistic_type.title + ' Rate',
        marker=dict(
            color=plot_color
        ),
    ))
    fig.update_layout(
        title=statistic_type.title + ' Rate',
        xaxis_title=statistic_type.x_axis_label,
        yaxis_title=statistic_type.y_axis_label
    )
    return plot(fig, output_type='div', include_plotlyjs=False, show_link=False, link_text="")


def index(request):
    rate_plot_div = ''
    scatterlines_div = ''
    datapoints_div = ''
    if request.method == 'POST':
        form = PlotForm(request.POST)
        if form.is_valid():
            rate_plot_div = get_rate_plot(form.cleaned_data['statistic_type'], form.cleaned_data['eye'])
            if form.cleaned_data['rate']:
                scatterlines_div = get_scatterlines(form.cleaned_data['rate'], form.cleaned_data['statistic_type'], form.cleaned_data['eye'])
            if form.cleaned_data['statistic']:
                datapoints_div = get_datapoints(Statistic.objects.get(id=form.cleaned_data['statistic']))
    else:
        form = PlotForm()
    return render(
        request,
        "plot.html",
        context={'rate_plot_div': rate_plot_div, 'scatterlines_div': scatterlines_div, 'datapoints_div': datapoints_div, 'form': form}
    )

