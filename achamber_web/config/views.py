from multiprocessing import context
from django.shortcuts import render
from django.contrib.auth.decorators import permission_required, login_required
from config.models import ConfigTbl
from monitor.models import Monitor

@login_required
def ConfigRequest(request):
    context = {
    }
    config_list = ConfigTbl.objects.all()
    if (request.method == 'POST'):
        for config in config_list:
            value = request.POST.get(config.key)
            config.value = value
            config.save()
        context['result'] = 'Successfully configurations stored'
        
    config_list = ConfigTbl.objects.all().order_by('key')        
    context['config_list'] = config_list
    
    monitor_list = Monitor.objects.all().order_by('date')
    context['monitor_list'] = monitor_list
    
    return render(request, 'config_request.html', context=context)

@login_required
def WateringRequest(request):
    context = {
    }

    if (request.method == 'POST'):
        watering = request.POST.get('watering')
        enforce_watering = ConfigTbl.objects.get(pk='enforce watering')
        if (watering == 'on'):
            enforce_watering.value = '1'
        else:
            enforce_watering.value = '0'
        enforce_watering.save()

    enforce_watering = ConfigTbl.objects.get(pk='enforce watering')
    context['enforce_watering'] = enforce_watering

    return render(request, 'watering.html', context=context)
