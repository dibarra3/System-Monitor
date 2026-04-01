import psutil
import time
import os
from datetime import datetime
import csv

try:
    with open("metrics.csv", "a", newline='') as f:
        writer = csv.writer(f)

        if f.tell() == 0:
            writer.writerow(["Time", "CPU %", "Memory"])

        print("Recording metrics... Press Ctrl+C to stop.")
        
        while True:
            now = datetime.now()
            formatted_time_24hr = now.strftime("%Y-%m-%d %H:%M:%S")

            cpu = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory().percent

            writer.writerow([formatted_time_24hr, cpu, memory])
            f.flush()

            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"Recording... [Ctrl+C to Quit]")
            print(f"Time: {formatted_time_24hr}")
            print(f"CPU: {round(cpu)}%")
            print(f"Memory: {round(memory)}%")
            time.sleep(1)

except KeyboardInterrupt:
    print("\nStopping script... Data saved to metrics.csv.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")