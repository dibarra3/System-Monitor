import psutil
import time
import os
from datetime import datetime
import csv

filename = "metrics.csv"
file_exists = os.path.isfile(filename)

def getMetrics():
        cpu = psutil.cpu_percent(interval=None)
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("C:\\").percent
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return cpu, memory, disk, current_time

def printMetrics(cpu, memory, disk, current_time):
        print(f"Recording... [Ctrl+C to Quit]")
        print(f"Time: {current_time}")
        print(f"CPU: {round(cpu)}%")
        print(f"Memory: {round(memory)}%")
        print(f"Disk : {round(disk)}%")

def writeMetrics(writer, current_time, cpu, memory, disk):
     writer.writerow([current_time, cpu, memory, disk])

try:
    with open(filename, "a", newline='') as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow(["Time", "CPU %", "Memory", "Disk %"])

        print("Recording metrics... Press Ctrl+C to stop.")
        
        while True:
            
            f.flush()
            os.system('cls' if os.name == 'nt' else 'clear')
            time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping script... Data saved to metrics.csv.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")