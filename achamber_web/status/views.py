from django.shortcuts import render
from django.contrib.auth.decorators import permission_required, login_required

from status.models import Status
from config.models import ConfigTbl

@login_required
def index(request):
    if (request.method == 'POST'):
        is_run = request.POST.get('is_run')
        config_run = ConfigTbl.objects.get(pk='Operate chamber(0 - stop, 1 - run)')
        if (is_run == 'on'):
            config_run.value = '1'
        else:
            config_run.value = '0'
        config_run.save()

    status_run = Status.objects.get(pk='run')
    status_start_time = Status.objects.get(pk='start_time')
    status_end_time = Status.objects.get(pk='end_time')
    config_run = ConfigTbl.objects.get(pk='Operate chamber(0 - stop, 1 - run)')
    
    context = {
        'status_run'            : status_run,
        'status_start_time'     : status_start_time,
        'status_end_time'       : status_end_time,
        'config_run'            : config_run,
    }

    return render(request, 'index.html', context=context)