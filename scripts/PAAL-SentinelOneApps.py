import os
import csv
import shutil
from datetime import date, datetime

# Define base directory
base_dir = os.path.expanduser("~")

# Get today's date
today = date.today().strftime("%m-%d-%Y")

# Define the file path
file_path = os.path.join(base_dir, "Desktop", "PAAL", "PAAL in Progress", "SentinelOne Applications", f"SentinelOne Applications - Original - {today}.csv")

# Verify if the file exists
if not os.path.exists(file_path):
    print("The file does not exist. Exiting...")
    exit()

# Construct the new filename with today's date
new_filename = f"SentinelOne Applications - Modified - {today}.csv"
destination_path = os.path.join(os.path.dirname(file_path), new_filename)

# Copy the selected file to the destination folder with the new filename
shutil.copy2(file_path, destination_path)
print(f"\nFile copied to: {destination_path}\n")

computer_column = "Endpoint Name"
application_column = "Application"
vulnerable_column = "Vulnerable Applications"
days_column = "Days From CVE Detection"
new_days_column = "Days Since Application Vulnerability Detection"
last_scan_column = "Last Successful Scan"
new_last_scan_column = "Days Since Last Successful S1 Scan"
amount_column = "Amount of Vulnerable Applications"
columns_to_remove = [
    "CVE ID",
    "Vendor",
    "Base Score",
    "Severity",
    "CVE Detection Date",
    "CVE Publish Date",
    "Last Scan Result",
    "Application",
    "Days From CVE Detection",
    "Last Successful Scan"
]

with open(destination_path, "r", newline="") as file:
    reader = csv.DictReader(file)
    header = reader.fieldnames

    computer_applications = {}
    all_rows = {}

    for row in reader:
        computer = row[computer_column]
        application = row[application_column]
        if computer in computer_applications:
            if application not in computer_applications[computer]:
                computer_applications[computer].append(application)
            all_rows[computer].append(row)
        else:
            computer_applications[computer] = [application]
            all_rows[computer] = [row]

sorted_computers = sorted(computer_applications.keys(), key=lambda x: x.lower())

header.insert(0, header.pop(header.index(computer_column)))

header.insert(1, amount_column)
header.append(vulnerable_column)
header = [new_last_scan_column if col == last_scan_column else col for col in header]
header = [new_days_column if col == days_column else col for col in header]

modified_rows = []

for computer in sorted_computers:
    rows = all_rows[computer]
    row = rows[0]

    applications = sorted(set(computer_applications[computer]))
    merged_applications = ", ".join(applications)
    row[vulnerable_column] = merged_applications

    row[amount_column] = len(applications)

    modified_row = {k: v for k, v in row.items() if k not in columns_to_remove}

    days_from_detection = row.get(days_column)
    if days_from_detection:
        modified_row[new_days_column] = int(days_from_detection.split()[0])

    last_scan = row.get(last_scan_column)
    if last_scan:
        last_scan_date = datetime.strptime(last_scan, "%b %d, %Y, %H:%M:%S")
        days_since_last_scan = (date.today() - last_scan_date.date()).days
        modified_row[new_last_scan_column] = days_since_last_scan

    modified_rows.append(modified_row)

header = [column for column in header if column not in columns_to_remove]

with open(destination_path, "w", newline="") as file:
    writer = csv.DictWriter(file, fieldnames=header)

    writer.writeheader()
    writer.writerows(modified_rows)

print("Changes applied successfully!")