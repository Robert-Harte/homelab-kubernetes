# Script to automate the backup of my postgres databases.
# The process will backup each database in my kubernetes pod and copy it onto my server.

import subprocess
from datetime import datetime

# List of current databases. I currently only use two, if I start using too lots I will think about making this list dynamic.
databases = {"linkding", "mealie"}
backup_dir = "/var/lib/postgresql"
today = datetime.today().strftime('%Y%m%d')

# Loop through databases
for db in databases:
    backup_filename = db + "_backup_" + today + ".dump"
    bg_command = "kubectl exec -n database -it postgres-0 -- pg_dump -U robert -d " + db + " --file="+ backup_dir + "/" + backup_filename
    
    # Run command to backup database.
    result = subprocess.run(bg_command, shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        cp_command = "kubectl cp database/postgres-0:var/lib/postgresql/" + backup_filename + " /media/storage/Backups/Databases/" + backup_filename
        
        # Copy database backup from prod to my home PC.
        copy_file = subprocess.run(cp_command, shell=True, capture_output=True, text=True)
        if copy_file.returncode == 0:
            print(backup_filename + " was successfully backed up!")
        else:
            print("There was an error copying the backup file " + backup_filename)
    else:
        print("There was an error creating the backup!")
    
