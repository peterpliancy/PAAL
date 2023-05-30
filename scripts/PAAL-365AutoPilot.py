import os
import shutil
import pandas as pd
from datetime import date

# Define the base directory
base_dir = os.path.expanduser("~/Desktop")

# Construct the file path
file_path = os.path.join(base_dir, "PAAL", "PAAL in Progress", "365 AutoPilot", "365 AutoPilot - Original - {}.csv".format(date.today().strftime("%m-%d-%Y")))

# Check if the file exists
if os.path.isfile(file_path):
    # Construct the duplicate file name
    duplicate_file_path = os.path.join(base_dir, "PAAL", "PAAL in Progress", "365 AutoPilot", "365 AutoPilot - Modified - {}.csv".format(date.today().strftime("%m-%d-%Y")))
    
    # Copy the original file to create a duplicate
    shutil.copy(file_path, duplicate_file_path)
    
    # Load the modified file into a DataFrame
    df = pd.read_csv(duplicate_file_path)
    
    # Remove specified columns from the DataFrame
    columns_to_remove = ['Purchase order', 'Profile status', 'Group tag']
    df.drop(columns_to_remove, axis=1, inplace=True)
    
    # Save the modified DataFrame back to the CSV file
    df.to_csv(duplicate_file_path, index=False)
    
    print("Duplicate file created successfully and columns removed.")
else:
    print("Original file not found.")
