import csv
import os
from datetime import date

# Get today's date
today = date.today().strftime("%m-%d-%Y")

# Define the file paths
addigy_directory = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/Addigy Devices/")
endpoint_directory = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/365 Endpoint/")
autopilot_directory = os.path.expanduser("~/Desktop/PAAL/PAAL in Progress/365 AutoPilot/")
compliance_directory = os.path.expanduser(f"~/Desktop/PAAL/PAAL in Progress/{today} - Audit/")
os.makedirs(compliance_directory, exist_ok=True)
addigy_file = os.path.join(addigy_directory, f"Addigy - Modified - {today}.csv")
endpoint_file = os.path.join(endpoint_directory, f"365 Endpoint - Modified - {today}.csv")
autopilot_file = os.path.join(autopilot_directory, f"365 AutoPilot - Modified - {today}.csv")
audit_file = os.path.join(compliance_directory, "Audit.csv")
compliance_file = os.path.join(compliance_directory, "ComplianceAudit.csv")

# Read the Audit.csv file and clone the "Endpoint Name" column
with open(audit_file, 'r') as file:
    reader = csv.DictReader(file)
    endpoint_names = [row.get("Endpoint Name".strip()) for row in reader]

# Create the ComplianceAudit.csv file with initial data
with open(compliance_file, 'w', newline='') as file:
    fieldnames = ["Endpoint Name", "Compliance Audit", "Encryption Status", "Compliance Status", "AD Join Type", "AutoPilot Status"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    # Fill "Endpoint Name" and "Compliance Audit" columns
    for endpoint_name in endpoint_names:
        writer.writerow({
            "Endpoint Name": endpoint_name,
            "Compliance Audit": "████",
            "Encryption Status": "",
            "Compliance Status": "",
            "AD Join Type": "",
            "AutoPilot Status": ""
        })

# Read the Addigy file and create a list of dictionaries if it exists
if os.path.isfile(addigy_file):
    with open(addigy_file, 'r') as file:
        reader = csv.DictReader(file)
        filevault_data = [row for row in reader]
else:
    filevault_data = []

# Read the 365 Endpoint file and create a list of dictionaries
with open(endpoint_file, 'r') as file:
    reader = csv.DictReader(file)
    endpoint_data = [row for row in reader]

# Check if the autopilot_file exists before trying to open it
if os.path.isfile(autopilot_file):
    # Read the 365 AutoPilot file and get the "Serial number" column
    with open(autopilot_file, 'r') as file:
        reader = csv.DictReader(file)
        autopilot_serials = {row.get("Serial number".strip()) for row in reader}
else:
    autopilot_serials = set()

# Read the ComplianceAudit.csv file, update the "Encryption Status", "Compliance Status", "AD Join Type", and "AutoPilot Status" based on the "Endpoint Name"
with open(compliance_file, 'r') as file:
    reader = csv.DictReader(file)
    compliance_rows = list(reader)

for row in compliance_rows:
    endpoint_name = row.get("Endpoint Name".strip())
    for filevault_entry in filevault_data:
        if filevault_entry.get("Endpoint Name".strip()) == endpoint_name and not row.get("Encryption Status".strip()):
            row["Encryption Status"] = filevault_entry.get("Filevault Status".strip())
    for endpoint_entry in endpoint_data:
        if endpoint_entry.get("Endpoint Name".strip()) == endpoint_name:
            if not row.get("Encryption Status".strip()):
                row["Encryption Status"] = endpoint_entry.get("Encryption Status".strip())
            if not row.get("Compliance Status".strip()):
                row["Compliance Status"] = endpoint_entry.get("Compliance Status".strip())
            if not row.get("AD Join Type".strip()):
                row["AD Join Type"] = endpoint_entry.get("AD JoinType".strip())
            if endpoint_entry.get("Serial number".strip()) not in autopilot_serials:
                row["AutoPilot Status"] = "Not Enrolled"

# Write updated rows back to the ComplianceAudit.csv file
with open(compliance_file, 'w', newline='') as file:
    fieldnames = ["Endpoint Name", "Compliance Audit", "Encryption Status", "Compliance Status", "AD Join Type", "AutoPilot Status"]
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(compliance_rows)

print("ComplianceAudit.csv file has been updated successfully!")
