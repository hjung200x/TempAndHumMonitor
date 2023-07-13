from django.shortcuts import render
from django.contrib.auth.decorators import permission_required, login_required
from monitor.models import Monitor, Event

@login_required
def MonitorGraph(request):
    monitor_list = Monitor.objects.all().order_by('date')
    event_list = Event.objects.all().order_by('date')

    context = {
        'monitor_list'          : monitor_list,
        'event_list'            : event_list,
    }
    
    return render(request, 'monitor_graph.html', context=context)

def DeleteAllMonitorData(request):
    Monitor.objects.all().delete()
    Event.objects.all().delete()

    context = {
    }
    
    return render(request, 'monitor_graph.html', context=context)
