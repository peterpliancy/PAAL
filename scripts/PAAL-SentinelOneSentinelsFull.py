import pandas as pd
import os
import shutil
from datetime import datetime, timedelta
import io
import urllib.request
import ssl

def load_csv_from_url(url):
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    with urllib.request.urlopen(url, context=ssl_context) as response:
        data = response.read()
    return pd.read_csv(io.StringIO(data.decode('utf-8')))

# Define base directory and file path
base_dir = os.path.expanduser("~")
original_file_path = os.path.join(base_dir, "Desktop", "PAAL", "PAAL in Progress", "SentinelOne Sentinels (Full)", f"SentinelOne Sentinels (Full) - Original - {datetime.now().strftime('%m-%d-%Y')}.csv")

comparison_data = load_csv_from_url("https://gist.githubusercontent.com/peterpliancy/09d569bc5657afa40272d5d687c5366e/raw/latestversion.csv")

# Load the original file
df = pd.read_csv(original_file_path)

necessary_columns = ["Scan Status", "Subscribed On"]
if all(item in df.columns for item in necessary_columns):
    print("The file has the necessary columns.")

    dest_folder = os.path.join(base_dir, 'Desktop', 'PAAL', 'PAAL in Progress', 'SentinelOne Sentinels (Full)')
    os.makedirs(dest_folder, exist_ok=True)

    date_str = datetime.today().strftime('%m-%d-%Y')
    modified_file_name = f'SentinelOne Sentinels (Full) - Modified - {date_str}.csv'

    modified_file_path = os.path.join(dest_folder, modified_file_name)
    shutil.copy(original_file_path, modified_file_path)
    print(f"Copied the original file to {modified_file_path}")

    df_modified = pd.read_csv(modified_file_path)

    necessary_columns = ["Endpoint Name", "Agent Version", "Serial Number", "OS", 
                         "OS Version", "Memory", "Update Status", "Disk Encryption", 
                         "Last Reboot Date", 
                         "Reboot Required due to Threat", "User Action Required"]

    # Check if 'Last Active' is in df_modified
    if 'Last Active' in df_modified.columns:
        necessary_columns.append('Last Active')

    df_modified = df_modified[necessary_columns]

    df_modified['OS Version'] = df_modified['OS Version'].apply(lambda x: str(x).split(',')[-1].split(' ')[0].strip().lower() if isinstance(x, str) else x)
    df_modified['OS Version'] = df_modified['OS Version'].apply(lambda x: x if pd.isnull(x) else '.'.join(x.split('.')[:3]))

    comparison_data['OSCombined'] = comparison_data['OSCombined'].apply(lambda x: str(x).strip().lower() if isinstance(x, str) else x)

    df_modified.loc[df_modified['OS Version'].isin(comparison_data['OSCombined']), 'OS Version'] = ''

    if 'Last Active' in df_modified.columns:
        df_modified['Last Active'] = pd.to_datetime(df_modified['Last Active'], format='%b %d, %Y %I:%M:%S %p')
        df_modified['Days Since Last Active'] = (datetime.now() - df_modified['Last Active']).dt.days
        df_modified.loc[df_modified['Days Since Last Active'] <= 13, 'Days Since Last Active'] = ""

    df_modified.rename(columns={'Endpoint Name': 'Device Name'}, inplace=True)
    df_modified['Reboot Required due to Threat'] = df_modified['Reboot Required due to Threat'].replace({"No": ""})

    df_modified['User Action Required'] = df_modified['User Action Required'].replace({"['reboot_needed']": "Reboot Required", "['rebootless_without_dynamic_detection']": "Reboot Required"})
    df_modified['User Action Required'] = df_modified['User Action Required'].apply(lambda x: '' if 'No' in str(x) else 'Full Disk Access Required' if 'fda' in str(x).lower() else x)

    df_modified['Disk Encryption'] = df_modified['Disk Encryption'].replace({"On": "", "Off": "Disabled"})
    df_modified.rename(columns={'Disk Encryption': 'Disk Encryption Status'}, inplace=True)

    df_modified.loc[df_modified['Update Status'] == "Up to date", 'Update Status'] = ""

    df_modified['Agent Version'] = df_modified.apply(lambda row: '' if row['Agent Version'] in comparison_data['S1 GA Mac Version'].tolist() or row['Agent Version'] in comparison_data['S1 GA Windows Version'].tolist() else row['Agent Version'], axis=1)

    df_modified['Last Reboot Date'] = pd.to_datetime(df_modified['Last Reboot Date'], format='%b %d, %Y %I:%M:%S %p')
    df_modified['Days Since Last Reboot'] = (datetime.now() - df_modified['Last Reboot Date']).dt.days
    df_modified.loc[df_modified['Days Since Last Reboot'] < 30, 'Days Since Last Reboot'] = ""
    df_modified.drop(['Last Reboot Date'], axis=1, inplace=True)
    
    if 'Last Active' in df_modified.columns:
        df_modified.drop(['Last Active'], axis=1, inplace=True)

    # Copy the 'OS Version' column from the original dataframe df to df_modified and rename it
    df_modified['OS Version OOD'] = df['OS Version']

    # Format 'OS Version OOD' as 'OS Version'
    df_modified['OS Version OOD'] = df_modified['OS Version OOD'].apply(lambda x: str(x).split(',')[-1].split(' ')[0].strip().lower() if isinstance(x, str) else x)
    df_modified['OS Version OOD'] = df_modified['OS Version OOD'].apply(lambda x: x if pd.isnull(x) else '.'.join(x.split('.')[:3]))

    # Swap 'OS Version' and 'OS Version OOD'
    df_modified.rename(columns={'OS Version': 'temp', 'OS Version OOD': 'OS Version'}, inplace=True)
    df_modified.rename(columns={'temp': 'OS Version OOD'}, inplace=True)

    # Rename 'Device Name' to 'Endpoint Name'
    df_modified.rename(columns={'Device Name': 'Endpoint Name'}, inplace=True)

    # Rename 'Disk Encryption Status' to 'Encryption Status'
    df_modified.rename(columns={'Disk Encryption Status': 'Encryption Status'}, inplace=True)

    # Rename 'Days Since Last Active' to 'Last Check-in'
    df_modified.rename(columns={'Days Since Last Active': 'Last Check-in'}, inplace=True)

    df_modified.to_csv(modified_file_path, index=False)
    print(f"Saved the modified file to {modified_file_path}")
else:
    print("The file does not have the necessary columns.")
