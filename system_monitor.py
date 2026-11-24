import psutil
import config

def check_system_health():
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent

    # Find top 3 CPU-consuming processes
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            processes.append(proc.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    top_procs = sorted(processes, key=lambda p: p['cpu_percent'] or 0, reverse=True)[:3]

    alerts = []
    if cpu_usage > config.CPU_THRESHOLD:
        alerts.append(f"High CPU usage: {cpu_usage}% (Threshold: {config.CPU_THRESHOLD}%)")
    if ram_usage > config.RAM_THRESHOLD:
        alerts.append(f"High RAM usage: {ram_usage}% (Threshold: {config.RAM_THRESHOLD}%)")
    if disk_usage > config.DISK_THRESHOLD:
        alerts.append(f"High Disk usage: {disk_usage}% (Threshold: {config.DISK_THRESHOLD}%)")

    return {
        "cpu": cpu_usage,
        "ram": ram_usage,
        "disk": disk_usage,
        "top_processes": top_procs,
        "alerts": alerts
    }
