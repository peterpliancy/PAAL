import os
import csv
from datetime import date

# Define the paths
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
today = date.today().strftime("%m-%d-%Y")
csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", f"{today} - Audit", "Audit.csv")
new_csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", f"{today} - Audit", "AuditTime.csv")
sentinel_csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", "SentinelOne Sentinels (Full)", f"SentinelOne Sentinels (Full) - Modified - {today}.csv")
sentinel_apps_csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", "SentinelOne Applications", f"SentinelOne Applications - Modified - {today}.csv")
screenconnect_csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", "ScreenConnect", f"ScreenConnect - Modified - {today}.csv")
addigy_csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", "Addigy Devices", f"Addigy - Modified - {today}.csv")
endpoint365_csv_path = os.path.join(desktop_path, "PAAL", "PAAL in Progress", "365 Endpoint", f"365 Endpoint - Modified - {today}.csv")

# Read the existing CSV file and extract the "Endpoint Name" column
data = []
with open(csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        endpoint_name = row.get("Endpoint Name".strip())  # Strip whitespaces from column name
        if endpoint_name is not None:
            data.append({"Endpoint Name": endpoint_name, "Time Audit": "████"})

sentinel_data = {}
sentinel_reboot_data = {}
screenconnect_data = {}
screenconnect_reboot_data = {}
sentinel_apps_data = {}
addigy_data = {}
endpoint365_data = {}

# Check if sentinel csv file exists
if os.path.isfile(sentinel_csv_path):
    with open(sentinel_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
            endpoint_name = row.get("Endpoint Name".strip())  # Strip whitespaces from column name
            last_checkin = row.get("Last Check-in")  # Use get() to avoid KeyError if the column doesn't exist
            days_since_reboot = row.get("Days Since Last Reboot")  # Use get() to avoid KeyError if the column doesn't exist
            if endpoint_name is not None and last_checkin is not None:
                sentinel_data[endpoint_name] = last_checkin
            if endpoint_name is not None and days_since_reboot is not None and days_since_reboot != '':
                sentinel_reboot_data[endpoint_name] = int(days_since_reboot)

# Check if sentinel apps csv file exists
if os.path.isfile(sentinel_apps_csv_path):
    with open(sentinel_apps_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
            endpoint_name = row.get("Endpoint Name".strip())  # Strip whitespaces from column name
            last_successful_scan = row.get("Days Since Last Successful S1 Scan")  # Use get() to avoid KeyError if the column doesn't exist
            if endpoint_name is not None and last_successful_scan is not None:
                sentinel_apps_data[endpoint_name] = last_successful_scan

# Check if screenconnect csv file exists
if os.path.isfile(screenconnect_csv_path):
    with open(screenconnect_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
            endpoint_name = row.get("Endpoint Name".strip())  # Strip whitespaces from column name
            last_checkin = row.get("Last Check-in")  # Use get() to avoid KeyError if the column doesn't exist
            days_since_reboot = row.get("Days Since Last Reboot")  # Use get() to avoid KeyError if the column doesn't exist
            if endpoint_name is not None and last_checkin is not None:
                screenconnect_data[endpoint_name] = last_checkin
            if endpoint_name is not None and days_since_reboot is not None and days_since_reboot != '':
                screenconnect_reboot_data[endpoint_name] = int(days_since_reboot)

# Check if addigy csv file exists
if os.path.isfile(addigy_csv_path):
    with open(addigy_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
            endpoint_name = row.get("Endpoint Name".strip())  # Strip whitespaces from column name
            last_checkin = row.get("Last Check-in")  # Use get() to avoid KeyError if the column doesn't exist
            if endpoint_name is not None and last_checkin is not None:
                addigy_data[endpoint_name] = last_checkin

# Check if endpoint365 csv file exists
if os.path.isfile(endpoint365_csv_path):
    with open(endpoint365_csv_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
            endpoint_name = row.get("Endpoint Name".strip())  # Strip whitespaces from column name
            last_checkin = row.get("Last check-in")  # Use get() to avoid KeyError if the column doesn't exist
            if endpoint_name is not None and last_checkin is not None:
                endpoint365_data[endpoint_name] = last_checkin

# Write the extracted data to the new CSV file with the additional columns
fieldnames = [
    "Endpoint Name",
    "Time Audit",
    "ScreenConnect: Days Since Last Check-in",
    "MDM: Days Since Last Check-in",
    "SentinelOne: Days Since Last Check-in",
    "SentinelOne: Days Since Last Scan",
    "Days Since Last Reboot"
]

with open(new_csv_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        endpoint_name = row.get("Endpoint Name")
        if endpoint_name is not None:
            if endpoint_name in sentinel_data:
                row["SentinelOne: Days Since Last Check-in"] = sentinel_data[endpoint_name]
                row["SentinelOne: Days Since Last Scan"] = sentinel_apps_data.get(endpoint_name, '')
            if endpoint_name in screenconnect_data:
                row["ScreenConnect: Days Since Last Check-in"] = screenconnect_data[endpoint_name]
            if endpoint_name in addigy_data:
                row["MDM: Days Since Last Check-in"] = addigy_data[endpoint_name]
            if endpoint_name in endpoint365_data:
                row["MDM: Days Since Last Check-in"] = endpoint365_data[endpoint_name]
            
            sentinel_reboot = sentinel_reboot_data.get(endpoint_name, None)
            screenconnect_reboot = screenconnect_reboot_data.get(endpoint_name, None)
            if sentinel_reboot is not None and screenconnect_reboot is not None:
                row["Days Since Last Reboot"] = min(sentinel_reboot, screenconnect_reboot)
            elif sentinel_reboot is not None:
                row["Days Since Last Reboot"] = sentinel_reboot
            elif screenconnect_reboot is not None:
                row["Days Since Last Reboot"] = screenconnect_reboot
            else:
                row["Days Since Last Reboot"] = ''
            writer.writerow(row)
