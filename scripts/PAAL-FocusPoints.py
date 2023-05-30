import os
import csv
from datetime import datetime

# Define the base folder and current date
base_folder = os.path.expanduser('~/Desktop/PAAL/PAAL in Progress')
current_date = datetime.now().strftime('%m-%d-%Y')

# Define the audit folder path
audit_folder = os.path.join(base_folder, current_date + ' - Audit')

# Create the "Focus Points" folder
focus_points_folder = os.path.join(audit_folder, 'Focus Points')
os.makedirs(focus_points_folder, exist_ok=True)

# Define the paths for the input and output CSV files
input_csv_path = os.path.join(audit_folder, 'PAAL.csv')
output_csv_azuread_path = os.path.join(focus_points_folder, '365 AzureAD.csv')

output_csv_paths = [
    os.path.join(focus_points_folder, 'SentinelOne Not Installed.csv'),
    os.path.join(focus_points_folder, 'SentinelOne Late Check-in.csv'),
    os.path.join(focus_points_folder, 'SentinelOne Late Last Scan.csv'),
    os.path.join(focus_points_folder, 'SentinelOne Agent Out of Date.csv'),
    os.path.join(focus_points_folder, 'ScreenConnect Not Installed.csv'),
    os.path.join(focus_points_folder, '365 Endpoint.csv'),
]

output_csv_headers = [
    'Endpoints missing SentinelOne',
    'SentinelOne Last Check-in more than 14 days ago',
    'SentinelOne Last Scan more than 14 days ago',
    'SentinelOne Sentinels with Agent that is Out of Date',
    'Endpoints Missing ScreenConnect',
    'Endpoint not found in 365 Endpoint'
]

def process_azuread_endpoints(input_csv_path, output_csv_path):
    with open(output_csv_path, 'w', newline='') as output_csv_file:
        writer = csv.writer(output_csv_file)
        writer.writerow(['Endpoints only in AzureAD'])

        with open(input_csv_path, 'r') as input_csv_file:
            reader = csv.DictReader(input_csv_file)
            for row in reader:
                endpoint_name = row['Endpoint Name']
                azuread = row['365 AzureAD']
                endpoint = row['365 Endpoint']
                screenconnect = row['ScreenConnect']
                sentinelone = row['SentinelOne']

                if azuread == '✔' and endpoint == '✖' and screenconnect == '✖' and sentinelone == '✖':
                    writer.writerow([endpoint_name])

output_csv_files = []
csv_writers = []

for i in range(len(output_csv_paths)):
    output_csv_files.append(open(output_csv_paths[i], 'w', newline='', encoding='utf-8'))
    csv_writers.append(csv.writer(output_csv_files[i]))
    csv_writers[i].writerow([output_csv_headers[i]])

try:
    with open(input_csv_path, 'r', encoding='utf-8') as input_csv_file:
        reader = csv.DictReader(input_csv_file)
        for row in reader:
            endpoint_name = row.get('Endpoint Name', '').strip()
            sentinelone = row.get('SentinelOne', '').strip()
            sentinelone_checkin = row.get('SentinelOne: Days Since Last Check-in', '').strip()
            sentinelone_scan = row.get('SentinelOne: Days Since Last Scan', '').strip()
            encryption_status = row.get('Encryption Status', '').strip()
            screenconnect = row.get('ScreenConnect', '').strip()
            endpoint365 = row.get('365 Endpoint', '').strip()

            if sentinelone == '✖':
                csv_writers[0].writerow([endpoint_name])
            if sentinelone_checkin:
                csv_writers[1].writerow([endpoint_name])
            if sentinelone_scan:
                csv_writers[2].writerow([endpoint_name])
            if encryption_status:
                csv_writers[3].writerow([endpoint_name])
            if screenconnect == '✖':
                csv_writers[4].writerow([endpoint_name])
            if endpoint365 == '✖':
                csv_writers[5].writerow([endpoint_name])
            
            for file in output_csv_files:
                file.flush()

    process_azuread_endpoints(input_csv_path, output_csv_azuread_path)

    print('Script executed successfully.')

except FileNotFoundError as fnf_error:
    print(f"File not found: {fnf_error}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    for file in output_csv_files:
        if not file.closed:
            file.close()
