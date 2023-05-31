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

# Convert the list to a DataFrame, remove duplicates and sort
audit_df = pd.DataFrame(audit_data)
audit_df.drop_duplicates(inplace=True)
audit_df.sort_values(by=['Endpoint Name'], inplace=True)

# Pivot the DataFrame to have a column for each service, with check marks for the endpoint names that appear in each service
pivot_df = audit_df.pivot_table(index='Endpoint Name', columns='Service', aggfunc=len, fill_value='✖')
pivot_df.replace(1, '✔', inplace=True)

# Check for endpoints that appear in 365 Endpoint or 365 AzureAD
if '365 Endpoint' in pivot_df.columns:
    endpoint_endpoints = pivot_df[pivot_df['365 Endpoint'] == '✔'].index
if '365 AzureAD' in pivot_df.columns:
    azuread_endpoints = pivot_df[pivot_df['365 AzureAD'] == '✔'].index

# Rename the specified columns
pivot_df.rename(columns={"SentinelOne Sentinels (Full)": "SentinelOne"}, inplace=True)

# Create a blank Addigy column
pivot_df.insert(2, 'Addigy', '')

# Load Addigy Devices csv
addigy_file = os.path.join(paal_in_progress_folder, 'Addigy Devices', f'Addigy - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv')
addigy_df = pd.read_csv(addigy_file)

# If 'Endpoint Name' in Addigy Devices csv, mark Addigy column in pivot_df as '✔'
addigy_endpoints = addigy_df['Endpoint Name']
for endpoint in addigy_endpoints:
    if endpoint in pivot_df.index:
        pivot_df.loc[endpoint, 'Addigy'] = '✔'

# Load SentinelOne Sentinels csv
sentinel_file = os.path.join(paal_in_progress_folder, 'SentinelOne Sentinels (Full)', f'SentinelOne Sentinels (Full) - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv')
sentinel_df = pd.read_csv(sentinel_file)

# If 'OS' column contains 'macOS' and there's not a '✔' in Addigy column, mark it as '✖'
mac_endpoints = sentinel_df[sentinel_df['OS'].str.contains('macOS', na=False)]['Endpoint Name']
for endpoint in mac_endpoints:
    if endpoint in pivot_df.index and pivot_df.loc[endpoint, 'Addigy'] != '✔':
        pivot_df.loc[endpoint, 'Addigy'] = '✖'

# Load ScreenConnect csv
screenconnect_file = os.path.join(paal_in_progress_folder, 'ScreenConnect', f'ScreenConnect - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv')
screenconnect_df = pd.read_csv(screenconnect_file)

# If 'OS Name' is 'Mac OS X' and Addigy column is blank, mark it as '✖'
mac_endpoints = screenconnect_df[screenconnect_df['OS Name'] == 'Mac OS X']['Endpoint Name']
for endpoint in mac_endpoints:
    if endpoint in pivot_df.index and pivot_df.loc[endpoint, 'Addigy'] == '':
        pivot_df.loc[endpoint, 'Addigy'] = '✖'

# Write the audit data to the audit file
pivot_df.to_csv(audit_file_path)
