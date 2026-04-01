import psutil
import time
import os
from datetime import datetime
import csv

filename = "metrics.csv"
file_exists = os.path.isfile(filename)

def getMetrics():
    return {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "cpu": psutil.cpu_percent(interval=None),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent
    }

def printMetrics(metrics):
    print(f"Time: {metrics['time']}")
    print(f"CPU: {metrics['cpu']:.1f}%")
    print(f"Memory: {metrics['memory']:.1f}%")
    print(f"Disk: {metrics['disk']:.1f}%")

def writeMetrics(writer, metrics):
        writer.writerow([
        metrics["time"],
        metrics["cpu"],
        metrics["memory"],
        metrics["disk"]
    ])

try:
    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Time", "CPU %", "Memory", "Disk %"])
        
        while True:
            metrics = getMetrics()
            printMetrics(metrics)
            writeMetrics(writer, metrics)
            f.flush()
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping script... Data saved to metrics.csv.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")