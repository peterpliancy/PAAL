import pandas as pd
import os
import ssl
import requests
from datetime import datetime
from io import StringIO

def main():
    # Get today's date
    date_today = datetime.now()

    # Define base directory
    base_dir = os.path.expanduser("~/Desktop")

    # Define the file path
    file_path = os.path.join(base_dir, "PAAL", "PAAL in Progress", "ScreenConnect", f"ScreenConnect - Original - {date_today.strftime('%m-%d-%Y')}.csv")

    # Check if the file exists
    if not os.path.exists(file_path):
        print("The file does not exist.")
        return

    df = pd.read_csv(file_path)
    if not {"GuestOperatingSystemName", "GuestMachineName", "GuestInfoUpdateTime"}.issubset(df.columns):
        print("The file does not contain the necessary columns.")
        return

    # Construct the new file path
    new_file_path = os.path.join(base_dir, "PAAL", "PAAL in Progress", "ScreenConnect", f"ScreenConnect - Modified - {date_today.strftime('%m-%d-%Y')}.csv")

    # Keep only the necessary columns
    df = df[["Name", "GuestOperatingSystemName", "GuestOperatingSystemManufacturerName", "GuestMachineModel", "GuestOperatingSystemVersion", "GuestLastBootTime", "GuestMachineSerialNumber", "GuestInfoUpdateTime"]]

    # Convert 'GuestLastBootTime' and 'GuestInfoUpdateTime' from string to datetime
    df['GuestLastBootTime'] = pd.to_datetime(df['GuestLastBootTime'], format='%m/%d/%Y %I:%M:%S %p')
    df['GuestInfoUpdateTime'] = pd.to_datetime(df['GuestInfoUpdateTime'], format='%m/%d/%Y %I:%M:%S %p')

    # Calculate the number of days from the last reboot and last check-in to today
    df['GuestLastBootTime'] = (date_today - df['GuestLastBootTime']).dt.days
    df['GuestInfoUpdateTime'] = (date_today - df['GuestInfoUpdateTime']).dt.days

    # Clear the entries where the last boot time is less than 30 days
    df.loc[df['GuestLastBootTime'] < 30, 'GuestLastBootTime'] = ''

    # Clear the entries where the last check-in is less than 14 days
    df.loc[df['GuestInfoUpdateTime'] < 14, 'GuestInfoUpdateTime'] = ''

    # Rename 'Microsoft Corporation' to 'Microsoft' in 'OS Manufacturer' column
    df['GuestOperatingSystemManufacturerName'] = df['GuestOperatingSystemManufacturerName'].apply(
        lambda x: 'Microsoft' if x == 'Microsoft Corporation' else x
    )

    # Create 'OS Version OOD' column by copying data from 'OS Version' column
    df.insert(df.columns.get_loc("GuestOperatingSystemVersion") + 1, 'OS Version OOD', df['GuestOperatingSystemVersion'])

    # Fetch the CSV file content using requests library
    response = requests.get(
        'https://gist.githubusercontent.com/peterpliancy/09d569bc5657afa40272d5d687c5366e/raw/latestversion.csv',
        verify=False
    )

    if response.status_code == 200:
        # Load the CSV content as a string
        csv_content = StringIO(response.text)

        # Load the string data into a DataFrame using pd.read_csv
        gist_df = pd.read_csv(csv_content)

        # Clear the 'OS Version OOD' values that exist in the 'OSCombined' column of the gist DataFrame
        df['OS Version OOD'] = df['OS Version OOD'].apply(lambda x: '' if x in gist_df['OSCombined'].values else x)

        # Rename the columns
        df.rename(
            columns={
                'Name': 'Endpoint Name',
                'GuestOperatingSystemName': 'OS Name',
                'GuestOperatingSystemManufacturerName': 'OS Manufacturer',
                'GuestMachineModel': 'Machine Model',
                'GuestOperatingSystemVersion': 'OS Version',
                'OS Version OOD': 'OS Version OOD',
                'GuestLastBootTime': 'Days Since Last Reboot',
                'GuestMachineSerialNumber': 'Serial Number',
                'GuestInfoUpdateTime': 'Last Check-in'
            },
            inplace=True
        )

        # Sort the DataFrame by the 'Endpoint Name' column, ignore case
        df.sort_values(by='Endpoint Name', key=lambda col: col.str.lower(), inplace=True)

        # Save the new CSV file
        df.to_csv(new_file_path, index=False)
        print(f"Modified file has been saved as: {new_file_path}")
    else:
        print("Failed to fetch the CSV file.")

if __name__ == "__main__":
    main()
