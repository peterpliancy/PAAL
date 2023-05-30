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
        endpoint_name = row["Endpoint Name"]
        data.append({"Endpoint Name": endpoint_name})

# Read the SentinelOne Sentinels CSV file and create a dictionary mapping endpoint names to last check-in dates
sentinel_data = {}
with open(sentinel_csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
        endpoint_name = row["Endpoint Name"]
        last_checkin = row.get("Last Check-in")  # Use get() to avoid KeyError if the column doesn't exist
        if last_checkin is not None:
            sentinel_data[endpoint_name] = last_checkin

# Read the SentinelOne Applications CSV file and create a dictionary mapping endpoint names to last successful scan dates
sentinel_apps_data = {}
with open(sentinel_apps_csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
        endpoint_name = row["Endpoint Name"]
        last_successful_scan = row.get("Days Since Last Successful S1 Scan")  # Use get() to avoid KeyError if the column doesn't exist
        if last_successful_scan is not None:
            sentinel_apps_data[endpoint_name] = last_successful_scan

# Read the ScreenConnect CSV file and create a dictionary mapping endpoint names to last check-in dates
screenconnect_data = {}
with open(screenconnect_csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        endpoint_name = row["Endpoint Name"]
        last_checkin = row.get("Last Check-in")  # Use get() to avoid KeyError if the column doesn't exist
        if last_checkin is not None:
            screenconnect_data[endpoint_name] = last_checkin

# Read the SentinelOne Sentinels CSV file and create a dictionary mapping endpoint names to days since last reboot
sentinel_reboot_data = {}
with open(sentinel_csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row = {k.strip(): v for k, v in row.items()}  # Strip spaces from column names
        endpoint_name = row["Endpoint Name"]
        days_since_reboot = row.get("Days Since Last Reboot")  # Use get() to avoid KeyError if the column doesn't exist
        if days_since_reboot is not None:
            sentinel_reboot_data[endpoint_name] = days_since_reboot

# Read the Addigy Devices CSV file and create a dictionary mapping endpoint names to last check-in dates
addigy_data = {}
with open(addigy_csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        endpoint_name = row["Endpoint Name"]
        last_checkin = row.get("Last Check-in")  # Use get() to avoid KeyError if the column doesn't exist
        if last_checkin is not None:
            addigy_data[endpoint_name] = last_checkin

# Read the 365 Endpoint CSV file and create a dictionary mapping endpoint names to last check-in dates
endpoint365_data = {}
with open(endpoint365_csv_path, 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        endpoint_name = row["Endpoint Name"]
        last_checkin = row.get("Last check-in")  # Use get() to avoid KeyError if the column doesn't exist
        if last_checkin is not None:
            endpoint365_data[endpoint_name] = last_checkin

# Write the extracted data to the new CSV file with the additional columns
fieldnames = ["Endpoint Name", "Time Audit", "ScreenConnect: Days Since Last Check-in", "MDM: Days Since Last Check-in",
              "SentinelOne: Days Since Last Check-in", "SentinelOne: Days Since Last Scan", "Days Since Last Reboot"]
with open(new_csv_path, 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        row["Time Audit"] = "████"
        endpoint_name = row["Endpoint Name"]
        if endpoint_name in sentinel_data:
            row["SentinelOne: Days Since Last Check-in"] = sentinel_data[endpoint_name]
        if endpoint_name in sentinel_apps_data:
            row["SentinelOne: Days Since Last Scan"] = sentinel_apps_data[endpoint_name]
        if endpoint_name in screenconnect_data:
            row["ScreenConnect: Days Since Last Check-in"] = screenconnect_data[endpoint_name]
        if endpoint_name in sentinel_reboot_data:
            row["Days Since Last Reboot"] = sentinel_reboot_data[endpoint_name]
        if endpoint_name in addigy_data:
            row["MDM: Days Since Last Check-in"] = addigy_data[endpoint_name]
        if endpoint_name in endpoint365_data:
            row["MDM: Days Since Last Check-in"] = endpoint365_data[endpoint_name]
        writer.writerow(row)

print("AuditTime.csv file created successfully.")
