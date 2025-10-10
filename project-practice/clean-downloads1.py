import os
import shutil
import time

downloads_dir = os.path.expanduser('~/Downloads')
to_delete_dir = os.path.expanduser('~/Downloads/to_delete')

if not os.path.exists(to_delete_dir):
    os.makedirs(to_delete_dir)

for filename in os.listdir(downloads_dir):
    file_path = os.path.join(downloads_dir, filename)
    if os.path.isfile(file_path):
        file_time = os.path.getmtime(file_path)
        if file_time < time.time() - 30 * 86400:  # 30 days old
            shutil.move(file_path, to_delete_dir)
