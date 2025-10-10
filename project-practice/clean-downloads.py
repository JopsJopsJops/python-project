import os
import shutil
import time

# Get current time
current_time = time.time()

# Define directories
download_dir = os.path.expanduser("~/Downloads/")
to_delete_dir = os.path.expanduser("~/Downloads/to_delete/")

# Create to_delete folder if it doesn't exist
os.makedirs(to_delete_dir, exist_ok=True)

# Loop through files
for filename in os.listdir(download_dir):
    file_path = os.path.join(download_dir, filename)
    
    # Skip if it's a folder
    if os.path.isdir(file_path):
        print(f"Skipping folder: {filename}")
        continue

    try:
        last_access_time = os.path.getatime(file_path)
        days_unused = (current_time - last_access_time) / (24 * 3600)

        if days_unused >= 30:
            dest_path = os.path.join(to_delete_dir, filename)
            shutil.move(file_path, dest_path)
            print(f"Moved: {filename}")
        else:
            print(f"Recent file, skipped: {filename}")
    except Exception as e:
        print(f"Error processing {filename}: {e}")