import os
import pandas as pd
import ssl
from urllib.request import urlopen
from datetime import datetime

def main():
    # Define base directory and file path
    base_dir = os.path.expanduser("~")
    current_date = datetime.now().strftime("%m-%d-%Y")
    file_path = os.path.join(base_dir, "Desktop", "PAAL", "PAAL in Progress", "365 Endpoint", f"365 Endpoint - Original - {current_date}.csv")

    df = pd.read_csv(file_path)

    # Create duplicate file
    today_date = datetime.now().strftime("%m-%d-%Y")
    directory = os.path.dirname(file_path)
    new_filename = f"365 Endpoint - Modified - {today_date}.csv"
    new_file_path = os.path.join(directory, new_filename)
    df.to_csv(new_file_path, index=False)

    # Edit the new file, keep only the specified columns
    keep_columns = ["Device name", "Last check-in", "OS version", "Serial number",
                    "Free storage", "Compliance", "Encrypted", "JoinType"]

    df = pd.read_csv(new_file_path)
    df = df[keep_columns]

    # Rename columns
    df.rename(columns={
        'Device name': 'Endpoint Name',  # Renamed column
        'OS version': 'OS Version',
        'Free storage': 'Free Disk Space (<20GB)',
        'Compliance': 'Compliance Status',
        'Encrypted': 'Encryption Status',
        'JoinType': 'AD JoinType'
    }, inplace=True)

    # Convert "Last check-in" to days prior to today's date
    df['Last check-in'] = pd.to_datetime(df['Last check-in'])
    df['Last check-in'] = (datetime.now() - df['Last check-in']).dt.days

    # Clear all entries in the "Last check-in" column that are 13 or less
    df.loc[df['Last check-in'] <= 13, 'Last check-in'] = ''

    # Convert "Free Disk Space (<20GB)" from MB to GB with no decimal
    df['Free Disk Space (<20GB)'] = (df['Free Disk Space (<20GB)'] / 1024).astype(int)

    # Clear all entries in the "Free Disk Space (<20GB)" that are more than 20
    df.loc[df['Free Disk Space (<20GB)'] > 20, 'Free Disk Space (<20GB)'] = ''

    # Remove all entries in "Compliance Status" that match "Compliant"
    df.loc[df['Compliance Status'] == "Compliant", 'Compliance Status'] = ''

    # If "Noncompliant" appears in the "Compliance Status" column, rename it to "Non Compliant"
    df.loc[df['Compliance Status'] == "Noncompliant", 'Compliance Status'] = 'Non Compliant'

    # Remove all items in "Encryption Status" that are TRUE, rename "FALSE" as "Disabled"
    df.loc[df['Encryption Status'] == True, 'Encryption Status'] = ''
    df.loc[df['Encryption Status'] == False, 'Encryption Status'] = 'Disabled'

    # Remove all entries in "AD JoinType" that match "Azure AD joined"
    df.loc[df['AD JoinType'] == "Azure AD joined", 'AD JoinType'] = ''

    # Clone "OS Version" to a new column "OS Version OOD"
    df.insert(df.columns.get_loc('OS Version') + 1, 'OS Version OOD', df['OS Version'])

    # Create unverified ssl context
    ssl._create_default_https_context = ssl._create_unverified_context

    # Read latest version data from gist
    with urlopen('https://gist.githubusercontent.com/peterpliancy/09d569bc5657afa40272d5d687c5366e/raw/latestversion.csv') as response:
        latest_versions = pd.read_csv(response)

    # Replace NaN values with an empty string in 'OS Version OOD'
    df['OS Version OOD'].fillna('', inplace=True)

    # Remove all entries in "OS Version OOD" that start with what is found in the gist in the "Windows" column.
    for version in latest_versions['Windows']:
        df.loc[df['OS Version OOD'].str.startswith(str(version)), 'OS Version OOD'] = ''

    df.to_csv(new_file_path, index=False)

if __name__ == "__main__":
    main()
