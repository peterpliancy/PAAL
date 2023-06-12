# PAAL1.0

If you are here you will only really need one more thing!

The command to run this in terminal assuming it has ran successfully in the past is:

python3 /Applications/PAAL/PAAL.py


Current Version 1.0.4
- removed the or feature for last reboot and just reverted it back to the smalllest number of the two entries found

Version 1.0.3
- removed the newly added type column from the outputted modified file sentinelone apps csv
- changed the success message at the end to start the process of cleaning those up
- changed the endpoint script to compare the gist to the OSCombined column instead of the Windows one to better support mixed platform
- changed output of the endpoint script to be in line with the S1 Apps scripts.
- modified the AzureAD script to have the new success message
- modified the AzureAD script to include the original OS column
- renamed macOS devices in the OS column in the AzureAD script

Version 1.0.2
- modified the scripts so that they no longer required an addigy file to be present. It was not built in mind with clients who used 365 to MDM both platofrms

Version 1.0.1
- reworked autoaudit.py to better handle mac devices
- crushed some bugs if the autopilot is not given it can now handle the errors
- removed case reformatting in the autoaudit.py
