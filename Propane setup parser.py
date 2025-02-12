import re
import os
from datetime import datetime

# Define the directory containing the log files
log_dir = r"c:\temp\prop logs delete me"
time_format = "%H:%M:%S.%f"

# Iterate through all files in the directory
for filename in os.listdir(log_dir):
    if filename.endswith(".log"):
        log_file_path = os.path.join(log_dir, filename)

        # Initialize variables to store timestamps and client number
        start_time = None
        end_time = None
        client_number = None

        # Process the log file
        with open(log_file_path, 'r') as log_file:
            for line in log_file:
                # Match the client number line
                if "Client number:" in line:
                    match = re.search(r'Client number:\s*"?(.*?)"?$', line)
                    if match:
                        client_number = match.group(1)
                # Match the "Fill DUT: RUNNING" line
                elif "Fill DUT: RUNNING" in line:
                    match = re.match(r'^(\d{2}:\d{2}:\d{2}\.\d+)', line)
                    if match:
                        start_time = datetime.strptime(match.group(1), time_format)
                # Match the "Fill DUT: PASS" line
                elif "Fill DUT: PASS" in line:
                    match = re.match(r'^(\d{2}:\d{2}:\d{2}\.\d+)', line)
                    if match:
                        end_time = datetime.strptime(match.group(1), time_format)

        # Calculate and print the time difference
        if start_time and end_time:
            time_difference = end_time - start_time
            print(f"{client_number},{time_difference}")
        # else:
            # print(f"{filename}: Client number: {client_number}, Could not find both timestamps in the log file.")
