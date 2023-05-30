import os
import pandas as pd
from datetime import datetime

# Get the current date and format it
current_date = datetime.now().strftime('%m-%d-%Y')

# Define the directory path
directory = os.path.expanduser(f'~/Desktop/PAAL/PAAL in Progress/{current_date} - Audit')

# Define the list of files to modify in the desired order
files_to_modify = ['AuditTime.csv', 'ComplianceAudit.csv', 'SoftwareAudit.csv', 'VulnerabilityAudit.csv']

# Define the output file
output_file = os.path.join(directory, 'Audit.csv')

# Load the existing data from the output file
output_df = pd.read_csv(output_file)

# Process each file
for file_name in files_to_modify:
    # Create the full file path
    file_path = os.path.join(directory, file_name)

    # Load the CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Remove the 'Endpoint Name' column if it exists
    if 'Endpoint Name' in df.columns:
        df = df.drop(columns=['Endpoint Name'])

    # Append the data to the output DataFrame
    output_df = pd.concat([output_df, df], axis=1)

# Save the output DataFrame to the output file
output_df.to_csv(output_file, index=False)

# Define the new file name
new_file = os.path.join(directory, 'PAAL.csv')

# Rename the output file
os.rename(output_file, new_file)

# Delete the processed files
for file_name in files_to_modify:
    # Create the full file path
    file_path = os.path.join(directory, file_name)

    # Delete the file
    if os.path.exists(file_path):
        os.remove(file_path)

print("PAAL.csv Created Successfully!")
