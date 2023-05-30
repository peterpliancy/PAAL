import os
import pandas as pd
from datetime import datetime, timezone
import requests
from io import StringIO

# Define base directory and file path
base_dir = os.path.expanduser("~")
current_date = datetime.now().strftime("%m-%d-%Y")
file_path = os.path.join(base_dir, "Desktop", "PAAL", "PAAL in Progress", "Addigy Devices", f"Addigy Devices - Original - {current_date}.csv")

# Read CSV file
df = pd.read_csv(file_path)

# Create a duplicate of the original file with only the necessary columns
necessary_columns = [
    "Device Name",
    "Serial Number",
    "FileVault Enabled",
    "Device Model Name",
    "Free Disk Space (GB)",
    "Has MDM Profile Approved",
    "MDM Last Connected",
    "OS Version"
]
df = df[necessary_columns]

# Convert "Free Disk Space (GB)" to int and calculate "Free Disk Space (<20GB)"
df["Free Disk Space (GB)"] = df["Free Disk Space (GB)"].fillna(0).apply(lambda x: int(round(x, 0)))
df.rename(columns={"Free Disk Space (GB)": "Free Disk Space (<20GB)"}, inplace=True)
df['Free Disk Space (<20GB)'] = df['Free Disk Space (<20GB)'].apply(lambda x: '' if x > 20 else x)

# Rename columns and update values
df.rename(columns={"Device Model Name": "Device Type"}, inplace=True)
df['Device Type'] = df['Device Type'].apply(lambda x: 'Mobile' if 'iPad' in x or 'iPhone' in x else 'Workstation')

df.rename(columns={"FileVault Enabled": "Filevault Status"}, inplace=True)
df.loc[(df['Device Type'] == 'Workstation') & (df['Filevault Status'] == False), 'Filevault Status'] = 'Disabled'
df.loc[df['Filevault Status'] == True, 'Filevault Status'] = ''

df.rename(columns={"Has MDM Profile Approved": "MDM Profile Approval Status"}, inplace=True)
df.loc[df['MDM Profile Approval Status'] != 'FALSE', 'MDM Profile Approval Status'] = ''
df.loc[df['MDM Profile Approval Status'] == 'FALSE', 'MDM Profile Approval Status'] = 'Not Approved'

df.rename(columns={"MDM Last Connected": "Days Since Last MDM Connection"}, inplace=True)
df['Days Since Last MDM Connection'] = pd.to_datetime(df['Days Since Last MDM Connection'], format='%b %d, %Y %H:%M %Z')
df['Days Since Last MDM Connection'] = (datetime.now(timezone.utc) - df['Days Since Last MDM Connection']).dt.days
df.loc[df['Days Since Last MDM Connection'] <= 14, 'Days Since Last MDM Connection'] = None
df['Days Since Last MDM Connection'] = df['Days Since Last MDM Connection'].astype('Int64')

df.rename(columns={"OS Version": "OS Version OOD"}, inplace=True)

# Fetch latest versions
response = requests.get('https://gist.githubusercontent.com/peterpliancy/09d569bc5657afa40272d5d687c5366e/raw/latestversion.csv')
latest_versions_df = pd.read_csv(StringIO(response.text))

# Apply the function to 'OS Version OOD'
df.loc[(df['Device Type'] == 'Workstation') & (df['OS Version OOD'].isin(latest_versions_df['macOS'])), 'OS Version OOD'] = ''
df.loc[(df['Device Type'] == 'Mobile') & (df['OS Version OOD'].isin(latest_versions_df['Mobile'])), 'OS Version OOD'] = ''

# For those entries not in the gist, leave the OS version as is
df.loc[(df['Device Type'] == 'Workstation') & (~df['OS Version OOD'].isin(latest_versions_df['macOS'])), 'OS Version OOD'] = df['OS Version OOD']
df.loc[(df['Device Type'] == 'Mobile') & (~df['OS Version OOD'].isin(latest_versions_df['Mobile'])), 'OS Version OOD'] = df['OS Version OOD']

# Remove rows where "Filevault Status" is 'True'
df = df[df['Filevault Status'] != 'True']
df = df[df['Filevault Status'] != True]  # Include boolean True as well

# Rename columns as the last step
df.rename(columns={"Device Name": "Endpoint Name", "Days Since Last MDM Connection": "Last Check-in"}, inplace=True)

# Fetch original "OS Version" column from the original file
original_df = pd.read_csv(file_path)
df['OS Version'] = original_df['OS Version']

# Save the modified dataframe to a new CSV file
dir_name = os.path.dirname(file_path)
new_file_name = f'Addigy - Modified - {datetime.now().strftime("%m-%d-%Y")}.csv'
new_file_path = os.path.join(dir_name, new_file_name)
df.to_csv(new_file_path, index=False)
