import csv
import os
from datetime import date

# Get today's date
today = date.today().strftime("%m-%d-%Y")

# Define the file paths
addigy_directory = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/Addigy Devices/")
endpoint_directory = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/365 Endpoint/")
audit_directory = os.path.expanduser(f"~/Desktop/PAAL/PAAL in Progress/{today} - Audit/")
os.makedirs(audit_directory, exist_ok=True)
addigy_file = os.path.join(addigy_directory, f"Addigy - Modified - {today}.csv")
endpoint_file = os.path.join(endpoint_directory, f"365 Endpoint - Modified - {today}.csv")
audit_file = os.path.join(audit_directory, "Audit.csv")
software_audit_file = os.path.join(audit_directory, "SoftwareAudit.csv")
sentinel_directory = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/SentinelOne Sentinels (Full)/")
sentinel_file = os.path.join(sentinel_directory, f"SentinelOne Sentinels (Full) - Modified - {today}.csv")

# Read the Audit.csv file and clone the "Endpoint Name" column
with open(audit_file, 'r') as file:
    reader = csv.DictReader(file)
    endpoint_names = [row["Endpoint Name"] for row in reader]

# Create the SoftwareAudit.csv file with initial data
with open(software_audit_file, 'w', newline='') as file:
    fieldnames = ["Endpoint Name", "Software Audit", "Operating System", "Sentinel Agent Version", "Free Disk Space (<20GB)"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # Fill "Endpoint Name" and "Software Audit" columns
    for endpoint_name in endpoint_names:
        writer.writerow({
            "Endpoint Name": endpoint_name,
            "Software Audit": "████",
            "Operating System": "",
            "Sentinel Agent Version": "",
            "Free Disk Space (<20GB)": ""
        })

# Read the Addigy and 365 Endpoint files and create lists of dictionaries
with open(addigy_file, 'r') as file:
    reader = csv.DictReader(file)
    addigy_data = [row for row in reader]
with open(endpoint_file, 'r') as file:
    reader = csv.DictReader(file)
    endpoint_data = [row for row in reader]

# Read the SoftwareAudit.csv file, update the "Operating System" and "Free Disk Space (<20GB)" based on the "Endpoint Name"
with open(software_audit_file, 'r') as file:
    reader = csv.DictReader(file)
    software_audit_rows = list(reader)

for row in software_audit_rows:
    endpoint_name = row["Endpoint Name"].lower()
    for addigy_entry in addigy_data:
        if addigy_entry["Endpoint Name"].lower() == endpoint_name:
            if addigy_entry["Device Type"].lower() != "mobile" or addigy_entry["Device Type"] == "Mobile":
                if not row["Operating System"]:
                    row["Operating System"] = addigy_entry["OS Version OOD"]
                if not row["Free Disk Space (<20GB)"]:
                    row["Free Disk Space (<20GB)"] = addigy_entry["Free Disk Space (<20GB)"]
    for endpoint_entry in endpoint_data:
        if endpoint_entry["Endpoint Name"].lower() == endpoint_name:
            if not row["Operating System"]:
                row["Operating System"] = endpoint_entry["OS Version OOD"]
            if not row["Free Disk Space (<20GB)"]:
                row["Free Disk Space (<20GB)"] = endpoint_entry["Free Disk Space (<20GB)"]

# Read the SentinelOne Sentinels file and create a dictionary of "Endpoint Name" to "Agent Version"
sentinel_data = {}
with open(sentinel_file, 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        endpoint_name = row["Endpoint Name"]
        agent_version = row["Agent Version"]
        sentinel_data[endpoint_name] = agent_version

# Update the "Sentinel Agent Version" based on the "Endpoint Name"
for row in software_audit_rows:
    endpoint_name = row["Endpoint Name"]
    if endpoint_name in sentinel_data:
        row["Sentinel Agent Version"] = sentinel_data[endpoint_name]

# Write the updated data back to the SoftwareAudit.csv file
with open(software_audit_file, 'w', newline='') as file:
    fieldnames = ["Endpoint Name", "Software Audit", "Operating System", "Sentinel Agent Version", "Free Disk Space (<20GB)"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(software_audit_rows)

print("SoftwareAudit.csv file has been updated successfully!")
