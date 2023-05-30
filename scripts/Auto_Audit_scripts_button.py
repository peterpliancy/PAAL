import subprocess
import time
import os

# Get the directory path of the current script (PAAL.py)
current_dir = os.path.dirname(os.path.abspath(__file__))

# List of scripts to run in order
scripts = [
    "PAAL-365AutoPilot.py",
    "PAAL-365AzureAD.py",
    "PAAL-365Endpoint.py",
    "PAAL-Addigy.py",
    "PAAL-Screenconnect.py",
    "PAAL-SentinelOneApps.py",
    "PAAL-SentinelOneSentinelsFull.py",
    "PAAL-AutoAudit.py",
    "PAAL-AuditTime.py",
    "PAAL-AuditCompliance.py",
    "PAAL-AuditSoftware.py",
    "PAAL-AuditVulnerability.py",
    "PAAL-AuditMerge.py",
    "PAAL-FocusPoints.py",
    "PAAL-HTMLReport.py"
]

# Run each script with a delay
for script in scripts:
    script_path = os.path.join(current_dir, script)
    print(f"Running script: {script_path}")
    result = subprocess.run(["python3", script_path], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"Error while running script: {script_path}")
        print(result.stderr)
    else:
        print("Script executed successfully.")

    time.sleep(2)
