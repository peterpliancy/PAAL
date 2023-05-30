import os
import shutil
import datetime
import pandas as pd
import requests
from io import StringIO

def copy_file(source_file, destination_folder, new_filename):
    shutil.copy2(source_file, os.path.join(destination_folder, new_filename))

def modify_csv_file(file_path):
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
        modified_df = modify_csv_file(modified_file_path)

        # Clear operatingSystemVersion if it starts with a value from the Windows column
        modified_df['operatingSystemVersion'] = modified_df['operatingSystemVersion'].astype(str)
        remote_data['Windows'] = remote_data['Windows'].astype(str)

        modified_df['operatingSystemVersion'] = modified_df.apply(
            lambda row: '' if any(str(row['operatingSystemVersion']).startswith(windows) for windows in remote_data['Windows']) else row['operatingSystemVersion'],
            axis=1
        )

        # Sort the displayName column alphabetically, ignoring case
        modified_df['displayName'] = modified_df['displayName'].astype(str)
        modified_df.sort_values(by='displayName', key=lambda x: x.str.lower(), inplace=True)

        # Change "False" entries in the isCompliant column to "Not Compliant"
        modified_df.loc[modified_df['isCompliant'] == False, 'isCompliant'] = 'Not Compliant'

        # Rename columns
        modified_df.rename(columns={
            'displayName': 'Endpoint Name',
            'operatingSystem': 'OS',
            'operatingSystemVersion': 'OS Version',
            'joinType (trustType)': 'AD JoinType',
            'isCompliant': 'Compliance Status',
            'isManaged': 'Managed Status'
        }, inplace=True)

        # Remove matches to 'Azure AD joined' in the 'AD JoinType' column
        modified_df.loc[modified_df['AD JoinType'] == 'Azure AD joined', 'AD JoinType'] = ''

        # Save the modified file
        save_csv_file(modified_df, modified_file_path)

        print("CSV file processing completed.")
    else:
        print(f"Source file does not exist: {source_file}")

if __name__ == "__main__":
    main()
