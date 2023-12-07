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


def index(request):
    plot_div = '<div></div>'
    if request.method == 'POST':
        form = PlotForm(request.POST)
        if form.is_valid():
            statistic_type = form.cleaned_data['statistic_type']
            x_data = []
            y_data = []
            dx_data = []
            dy_data = []
            customdata = []
            if form.cleaned_data['eye']:
                stats = statistic_type.statistics.filter(eye=form.cleaned_data['eye'])
                plot_color = 'green' if form.cleaned_data['eye'] == 'R' else 'red'
            else:
                stats = statistic_type.statistics.all()
                plot_color = 'green'
            for stat in stats:
                if form.cleaned_data['eye']:
                    dx_data.append(0)
                    dx_data.append(100)
                    dy_data.append(stat.predict_y(dx_data[0]))
                    dy_data.append(stat.predict_y(dx_data[1]))
                for datapoint in stat.datapoints.all():
                    x_data.append(datapoint.x_value)
                    y_data.append(datapoint.y_value)
                    customdata.append((datapoint.event_id, datapoint.event_type))

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=x_data,
                y=y_data,
                customdata=customdata,
                mode='markers',
                name=statistic_type.title,
                opacity=0.8,
                marker=dict(
                    color=plot_color
                ),
            ))
            if dx_data:
                fig.add_trace(go.Scatter(
                    x=dx_data,
                    y=dy_data,
                    mode='lines',
                    name=statistic_type.title + ' (Avg)',
                    opacity=0.8,
                    marker=dict(
                        color=plot_color
                    ),
                ))
            fig.update_layout(
                title=statistic_type.title,
                xaxis_title=statistic_type.x_axis_label,
                yaxis_title=statistic_type.y_axis_label
            )
            plot_div = plot(fig, output_type='div', include_plotlyjs=False, show_link=False, link_text="")
    else:
        form = PlotForm()
    return render(request, "plot.html", context={'plot_div': plot_div, 'form': form})

