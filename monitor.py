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
MEMORY_ALERT_THRESHOLD = 85
DISK_ALERT_THRESHOLD = 90

def get_Metrics(previous_net, interval):
    current_net = psutil.net_io_counters()
    sent_per_sec = 0.0
    recv_per_sec = 0.0

    if previous_net is not None:
        sent_per_sec = (current_net.bytes_sent - previous_net.bytes_sent) / interval
        recv_per_sec = (current_net.bytes_recv - previous_net.bytes_recv) / interval

    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage(DISK_PATH).percent,
        "bytes_sent": current_net.bytes_sent,
        "bytes_recv": current_net.bytes_recv,
        "sent_per_sec": sent_per_sec,
        "recv_per_sec": recv_per_sec
    }, current_net

def make_bar(percent, width=20):
    filled = int((percent / 100) * width)
    empty = width - filled
    return "[" + "#" * filled + "-" * empty + "]"


def print_Metrics(metrics, alerts):
    print("=" * 50)
    print("             SYSTEM MONITOR DASHBOARD")
    print("=" * 50)
    print(f"Time: {metrics['time']}")
    print()

    print("[USAGE]")
    print(f"CPU:        {metrics['cpu']:.1f}% {make_bar(metrics['cpu'])}")
    print(f"Memory:     {metrics['memory']:.1f}% {make_bar(metrics['memory'])}")
    print(f"Disk:       {metrics['disk']:.1f}% {make_bar(metrics['disk'])}")
    print()

    print("[NETWORK]")
    print(f"Bytes Sent:      {metrics['bytes_sent']}")
    print(f"Bytes Received:  {metrics['bytes_recv']}")
    print(f"Upload Rate:     {format_bytes_per_sec(metrics['sent_per_sec'])}")
    print(f"Download Rate:   {format_bytes_per_sec(metrics['recv_per_sec'])}")
    print()

    print("[STATUS]")
    if alerts:
        print("Health: WARNING")
        print("Alerts: " + "; ".join(alerts))
    else:
        print("Health: NORMAL")
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
        "Time",
        "CPU %",
        "Memory %",
        "Disk %",
        "Bytes Sent",
        "Bytes Received",
        "Upload Rate (B/s)",
        "Download Rate (B/s)",
        "Alerts"
    ])

def write_Metrics(writer, metrics, alerts):
        alert_text = "; ".join(alerts)

        writer.writerow([
        metrics["time"],
        metrics["cpu"],
        metrics["memory"],
        metrics["disk"],
        metrics["bytes_sent"],
        metrics["bytes_recv"],
        metrics["sent_per_sec"],
        metrics["recv_per_sec"],
        alert_text
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