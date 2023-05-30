import os
import csv
import pandas as pd
from datetime import datetime

# Define paths
desktop = os.path.expanduser("~/Desktop")
paal_folder = os.path.join(desktop, "PAAL")
paal_in_progress_folder = os.path.join(paal_folder, "PAAL in Progress")

# Define audit file path
today_date_folder = datetime.now().strftime("%m-%d-%Y") + " - Audit"
today_date_folder_path = os.path.join(paal_in_progress_folder, today_date_folder)
os.makedirs(today_date_folder_path, exist_ok=True)
audit_file_name = "Audit.csv"
audit_file_path = os.path.join(today_date_folder_path, audit_file_name)

# Create a list to hold the audit data
audit_data = []

# List of csv file paths
csv_files = [
    os.path.join(paal_in_progress_folder, '365 AzureAD', f'365 AzureAD - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv'),
    os.path.join(paal_in_progress_folder, '365 Endpoint', f'365 Endpoint - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv'),
    os.path.join(paal_in_progress_folder, 'Addigy Devices', f'Addigy - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv'),
    os.path.join(paal_in_progress_folder, 'ScreenConnect', f'ScreenConnect - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv'),
    os.path.join(paal_in_progress_folder, 'SentinelOne Sentinels (Full)', f'SentinelOne Sentinels (Full) - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv')
]

# Process each csv file
for file in csv_files:
    # Get the service name from the file name
    service_name = os.path.basename(os.path.dirname(file))

    df = pd.read_csv(file)

    # Check if 'Endpoint Name' is in the csv file
    if 'Endpoint Name' in df.columns:
        for endpoint_name in df['Endpoint Name']:
            audit_data.append({'Endpoint Name': endpoint_name, 'Service': service_name})

# Convert the list to a DataFrame, make entries upper case, remove duplicates and sort
audit_df = pd.DataFrame(audit_data)
audit_df['Endpoint Name'] = audit_df['Endpoint Name'].str.upper()
audit_df.drop_duplicates(inplace=True)
audit_df.sort_values(by=['Endpoint Name'], inplace=True)

# Pivot the DataFrame to have a column for each service, with check marks for the endpoint names that appear in each service
pivot_df = audit_df.pivot_table(index='Endpoint Name', columns='Service', aggfunc=len, fill_value='✖')
pivot_df.replace(1, '✔', inplace=True)

# Check for endpoints that appear in Addigy Devices and mark 365 AzureAD and 365 Endpoint as blank
if 'Addigy Devices' in pivot_df.columns:
    addigy_endpoints = pivot_df[pivot_df['Addigy Devices'] == '✔'].index
    if '365 Endpoint' in pivot_df.columns:
        pivot_df.loc[addigy_endpoints, '365 Endpoint'] = ''
    if '365 AzureAD' in pivot_df.columns:
        pivot_df.loc[addigy_endpoints, '365 AzureAD'] = ''

# Check for endpoints that appear in 365 Endpoint or 365 AzureAD and mark Addigy Devices as blank
if '365 Endpoint' in pivot_df.columns:
    endpoint_endpoints = pivot_df[pivot_df['365 Endpoint'] == '✔'].index
    if 'Addigy Devices' in pivot_df.columns:
        pivot_df.loc[endpoint_endpoints, 'Addigy Devices'] = ''
if '365 AzureAD' in pivot_df.columns:
    azuread_endpoints = pivot_df[pivot_df['365 AzureAD'] == '✔'].index
    if 'Addigy Devices' in pivot_df.columns:
        pivot_df.loc[azuread_endpoints, 'Addigy Devices'] = ''

# Rename the specified columns
pivot_df.rename(columns={"Addigy Devices": "Addigy", "SentinelOne Sentinels (Full)": "SentinelOne"}, inplace=True)

# Load ScreenConnect csv
screenconnect_file = os.path.join(paal_in_progress_folder, 'ScreenConnect', f'ScreenConnect - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv')
screenconnect_df = pd.read_csv(screenconnect_file)

# Load Addigy Devices csv
addigy_file = os.path.join(paal_in_progress_folder, 'Addigy Devices', f'Addigy - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv')
addigy_df = pd.read_csv(addigy_file)

# For each endpoint in ScreenConnect csv where "OS Name" is "Mac OS X"
# if it's not in Addigy Devices csv, mark Addigy column in pivot_df as "✖"
mac_endpoints = screenconnect_df[screenconnect_df['OS Name'] == 'Mac OS X']['Endpoint Name'].str.upper()
missing_endpoints = mac_endpoints[~mac_endpoints.isin(addigy_df['Endpoint Name'].str.upper())]
pivot_df.loc[missing_endpoints, 'Addigy'] = '✖'

# If "OS Name" is not "Mac OS X", leave the corresponding entry blank
non_mac_endpoints = screenconnect_df[screenconnect_df['OS Name'] != 'Mac OS X']['Endpoint Name'].str.upper()
pivot_df.loc[non_mac_endpoints, 'Addigy'] = ''

# Write the audit data to the audit file
pivot_df.to_csv(audit_file_path)
