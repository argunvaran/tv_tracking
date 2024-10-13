from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import TV, TVLog
from .forms import TVForm
from background_task import background
from django.utils import timezone
from django.db.models import Sum
import subprocess
import logging
from datetime import timedelta

logger = logging.getLogger('tv_logger')

last_status = {}

def ping_device(ip, attempts=3):
    successful_pings = 0
    try:
        for _ in range(attempts):
            output = subprocess.check_output(['ping', '-n', '1', ip], universal_newlines=True)
            if "TTL=" in output:
                successful_pings += 1

        if successful_pings >= attempts // 2:
            logger.info(f"Ping Success: {ip} Connected to Internet.")
            return True
        else:
            logger.warning(f"Ping Fail: {ip} Not Connected to Internet.")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Ping Error: {ip} - Error: {e}")
        return False

@background(schedule=10)
def check_tv_status():
    global last_status
    all_tvs = TV.objects.all()
    for tv in all_tvs:
        is_online = ping_device(tv.ip_address, attempts=3)
        current_status = 'ON' if is_online else 'OFF'

        if tv.ip_address not in last_status:
            last_status[tv.ip_address] = current_status
            logger.info(f"{tv.name} Initial Status: {current_status}")
            TVLog.objects.create(tv=tv, status=current_status, timestamp=timezone.now())
            tv.is_online = is_online
            tv.save()
        elif last_status[tv.ip_address] != current_status:
            logger.info(f"{tv.name} Status Changed: {current_status}")

            if current_status == 'OFF':
                last_on_log = TVLog.objects.filter(tv=tv, status='ON').last()
                if last_on_log:
                    last_on_log.duration = timezone.now() - last_on_log.timestamp
                    last_on_log.save()
                    logger.info(f"{tv.name} Offline Duration: {last_on_log.duration}")

            TVLog.objects.create(tv=tv, status=current_status, timestamp=timezone.now())
            tv.is_online = is_online
            tv.save()
            last_status[tv.ip_address] = current_status

def start_check(request):
    check_tv_status(repeat=10)  
    return redirect('tv_status')


def add_tv(request):
    if request.method == 'POST':
        form = TVForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tv_status')  
    else:
        form = TVForm()
    
    return render(request, 'add_tv.html', {'form': form})

def delete_tv(request, tv_id):
    tv = get_object_or_404(TV, id=tv_id)
    if request.method == 'POST':
        tv.delete()
        return redirect('tv_status')
    return render(request, 'confirm_delete.html', {'tv': tv})

def tv_status_view(request):
    tvs = TV.objects.all()
    return render(request, 'tv_status.html', {'tvs': tvs})

def tv_report_view(request):
    tvs = TV.objects.all()
    selected_tv_id = request.GET.get('tv_id')

    if selected_tv_id:
        selected_tv = TV.objects.get(id=selected_tv_id)
        logs = TVLog.objects.filter(tv=selected_tv).order_by('timestamp')
        
        filtered_logs = []
        total_duration = timedelta()

        for log in logs:
            if log.status == 'ON':

                next_off_log = TVLog.objects.filter(tv=selected_tv, status='OFF', timestamp__gt=log.timestamp).first()
                if next_off_log:
                   
                    log.duration = next_off_log.timestamp - log.timestamp
                    total_duration += log.duration
                    filtered_logs.append(log)  
            elif log.status == 'OFF' and log.duration:
                
                filtered_logs.append(log)

        logs = filtered_logs  
    else:
        selected_tv = None
        logs = None
        total_duration = None

    return render(request, 'tv_report.html', {
        'tvs': tvs,
        'selected_tv': selected_tv,
        'logs': logs,
        'total_duration': total_duration
    })

