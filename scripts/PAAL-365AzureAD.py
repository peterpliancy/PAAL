import os
import shutil
import datetime
import pandas as pd
import requests
from io import StringIO

def copy_file(source_file, destination_folder, new_filename):
    shutil.copy2(source_file, os.path.join(destination_folder, new_filename))

def modify_csv_file(file_path, remote_data):
    df = pd.read_csv(file_path)

    columns_to_remove = [
        'accountEnabled',
        'registeredOwners',
        'userNames',
        'mdmDisplayName',
        'registrationTime',
        'approximateLastSignInDateTime',
        'deviceId',
        'objectId',
        'profileType',
        'systemLabels',
        'model'
    ]

    df.drop(columns=columns_to_remove, inplace=True)

    df.loc[df['isCompliant'] == True, 'isCompliant'] = ''
    df.loc[df['isManaged'] == True, 'isManaged'] = ''

    df.loc[df['isCompliant'] == False, 'isCompliant'] = 'Not Compliant'

    # Rename entries from "MacMDM" to "macOS" in the "operatingSystem" column
    df.loc[df['operatingSystem'] == 'MacMDM', 'operatingSystem'] = 'macOS'

    # Rename columns
    df.rename(columns={'isCompliant': 'Compliance Status', 'joinType (trustType)': 'AD Join Type', 'isManaged': 'Managed Status'}, inplace=True)

    # Rename the "operatingSystem" column to "OS"
    df.rename(columns={'operatingSystem': 'OS'}, inplace=True)

    # Create a new column "OS Version OOD" and clone the values from "operatingSystemVersion"
    df.insert(df.columns.get_loc('operatingSystemVersion') + 1, 'OS Version OOD', df['operatingSystemVersion'])

    # Clear "OS Version OOD" if it starts with a value from the OSCombined column
    df['OS Version OOD'] = df['OS Version OOD'].astype(str)
    remote_data['OSCombined'] = remote_data['OSCombined'].astype(str)

    df['OS Version OOD'] = df.apply(
        lambda row: '' if any(row['OS Version OOD'].startswith(version) for version in remote_data['OSCombined']) else row['OS Version OOD'],
        axis=1
    )

    # Sort the displayName column alphabetically, ignoring case
    df['displayName'] = df['displayName'].astype(str)
    df.sort_values(by='displayName', key=lambda x: x.str.lower(), inplace=True)

    return df

def save_csv_file(df, output_path):
    df.to_csv(output_path, index=False)

def fetch_remote_csv_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        df = pd.read_csv(StringIO(content))
        return df
    else:
        raise Exception("Failed to fetch remote CSV data.")

def main():
    # Get today's date
    date_today = datetime.datetime.now().strftime("%m-%d-%Y")

    # Define base directory
    base_dir = os.path.expanduser("~/Desktop")

    # Define file paths
    source_file = os.path.join(base_dir, "PAAL", "PAAL in Progress", "365 AzureAD", "365 AzureAD - Original - " + date_today + ".csv")
    modified_file_name = "365 AzureAD - Modified - " + date_today + ".csv"

    # Check if the source file exists
    if os.path.isfile(source_file):
        # Define the path for the modified file
        modified_file_path = os.path.join(base_dir, "PAAL", "PAAL in Progress", "365 AzureAD", modified_file_name)

        # Copy the file and rename it
        copy_file(source_file, os.path.dirname(modified_file_path), modified_file_name)

        # Fetch remote CSV data from Gist
        gist_url = "https://gist.githubusercontent.com/peterpliancy/09d569bc5657afa40272d5d687c5366e/raw/latestversion.csv"
        remote_data = fetch_remote_csv_data(gist_url)

        # Modify the modified file
        modified_df = modify_csv_file(modified_file_path, remote_data)

        # Rename columns
        modified_df.rename(columns={'isCompliant': 'Compliance Status', 'joinType (trustType)': 'AD Join Type', 'isManaged': 'Managed Status'}, inplace=True)
        modified_df.rename(columns={'operatingSystem': 'OS', 'operatingSystemVersion': 'OS Version'}, inplace=True)

        # Save the modified file
        save_csv_file(modified_df, modified_file_path)

        print("365 AzureAD CSV Created Successfully!")
    else:
        print(f"Source file does not exist: {source_file}")

if __name__ == "__main__":
    main()
