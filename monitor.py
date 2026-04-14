import psutil
import time
import os
from datetime import datetime
import csv

FILENAME = "metrics.csv"
INTERVAL = 1
PRINT_TO_SCREEN = True
DISK_PATH = "/"

CPU_ALERT_THRESHOLD = 8
MEMORY_ALERT_THRESHOLD = 8
DISK_ALERT_THRESHOLD = 90

START_TIME = time.time()

def get_Metrics(previous_net, interval):
    current_net = psutil.net_io_counters()
    sent_per_sec = 0.0
    recv_per_sec = 0.0
    cpu = psutil.cpu_percent(interval=None)
    memory = psutil.virtual_memory().percent
    disk = psutil.disk_usage(DISK_PATH).percent

    if previous_net is not None:
        sent_per_sec = (current_net.bytes_sent - previous_net.bytes_sent) / interval
        recv_per_sec = (current_net.bytes_recv - previous_net.bytes_recv) / interval

    metrics = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "bytes_sent": current_net.bytes_sent,
        "bytes_recv": current_net.bytes_recv,
        "sent_per_sec": sent_per_sec,
        "recv_per_sec": recv_per_sec,   
    }

    alerts = check_alerts(metrics)
    health = get_health_status(alerts)

    metrics["health"] = health
    metrics["active_alerts"] = len(alerts)
    metrics["alert_messages"] = "; ".join(alerts) if alerts else "None"

    return metrics, current_net

def make_bar(percent, width=20):
    filled = int((percent / 100) * width)
    empty = width - filled
    return "[" + "#" * filled + "-" * empty + "]"

def get_health_status(alerts):
    if not alerts:
        return "NORMAL"

    if any("[EMERGENCY]" in alert for alert in alerts):
        return "EMERGENCY"

    if any("[CRITICAL]" in alert for alert in alerts):
        return "CRITICAL"

    if any("[WARNING]" in alert for alert in alerts):
        return "WARNING"

    return "NORMAL"

def print_Metrics(metrics, alerts):
    print("=" * 50)
    print("             SYSTEM MONITOR DASHBOARD")
    print("=" * 50)
    print(f"Time: {metrics['time']}")
    print(f"Monitor Runtime: {get_runtime()}")
    print()

    print("[USAGE]")
    print(f"CPU:        {metrics['cpu']:.1f}% {make_bar(metrics['cpu'])}")
    print(f"Memory:     {metrics['memory']:.1f}% {make_bar(metrics['memory'])}")
    print(f"Disk:       {metrics['disk']:.1f}% {make_bar(metrics['disk'])}")
    print()

    print("[NETWORK]")
    print(f"Bytes Sent:      {format_bytes(metrics['bytes_sent'])}")
    print(f"Bytes Received:  {format_bytes(metrics['bytes_recv'])}")
    print(f"Upload Rate:     {format_bytes_per_sec(metrics['sent_per_sec'])}")
    print(f"Download Rate:   {format_bytes_per_sec(metrics['recv_per_sec'])}")
    print()

    symbol = {
        "NORMAL": "[OK]",
        "WARNING": "[!]",
        "CRITICAL": "[!!]",
        "EMERGENCY": "[!!!]"
    }

    health = metrics["health"]

    print("[STATUS]")
    print(f"Active Alerts: {len(alerts)}")
    print(f"Health: {symbol[health]} {health}")
    if alerts:
        print("Alerts:")
        for alert in alerts:
            print(f"  - {alert}")
    else:
        print("Alerts: None")

    print("=" * 50)

def format_bytes_per_sec(bytes_per_sec):
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.1f} B/s"
    elif bytes_per_sec < 1024 ** 2:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 ** 3:
        return f"{bytes_per_sec / (1024 ** 2):.1f} MB/s"
    else:
        return f"{bytes_per_sec / (1024 ** 3):.1f} GB/s"

def write_header(writer):
    writer.writerow([
        "Time", "CPU %", "Memory %", "Disk %",
        "Bytes Sent", "Bytes Received",
        "Upload Rate (B/s)", "Download Rate (B/s)",
        "Health", "Active Alerts", "Alert Messages"
    ])

def write_Metrics(writer, metrics, alerts):
        writer.writerow([
        metrics["time"],
        metrics["cpu"],
        metrics["memory"],
        metrics["disk"],
        metrics["bytes_sent"],
        metrics["bytes_recv"],
        metrics["sent_per_sec"],
        metrics["recv_per_sec"],
        metrics["health"],
        metrics["active_alerts"],
        metrics["alert_messages"]
    ])

def check_alerts(metrics):
    alerts = []

    if metrics['cpu'] > CPU_ALERT_THRESHOLD:
        alerts.append("[WARNING] High CPU usage")
    
    if metrics['memory'] > MEMORY_ALERT_THRESHOLD:
        alerts.append("[CRITICAL] High Memory usage")
    
    if metrics['disk'] > DISK_ALERT_THRESHOLD:
        alerts.append("[EMERGENCY] High Disk usage")
    
    return alerts

def get_runtime():
    elapsed = int(time.time() - START_TIME)
    hours = elapsed // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def format_bytes(num):
    units = ["B", "KB", "MB", "GB", "TB"]
    value = float(num)

    for unit in units:
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}"
        value /= 1024

def main():
    file_exists = os.path.isfile(FILENAME)
    previous_net = None

    try:
        with open(FILENAME, "a", newline='') as f:
            writer = csv.writer(f)

            if not file_exists:
                write_header(writer)
            
            while True:
                metrics, previous_net = get_Metrics(previous_net, INTERVAL)
                my_alerts = check_alerts(metrics)

                if PRINT_TO_SCREEN:
                    os.system('cls' if os.name == 'nt' else 'clear')
                    print_Metrics(metrics,my_alerts)
                
                write_Metrics(writer, metrics,my_alerts)
                f.flush()
                time.sleep(INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping script... Data saved to metrics.csv.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()