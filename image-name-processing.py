import os
import shutil

# Set the path to the folder containing the subfolders
folder_path = "dataset"

# Traverse the subfolders
for root, dirs, files in os.walk(folder_path):
    # Loop through the files in each subfolder
    for file_name in files:
        # Check if the file is a JPG image
        if file_name.endswith(".JPG"):
            # Check if the file name contains a space
            if " " in file_name:
                # Replace the space with an underscore
                new_file_name = file_name.replace(" ", "_")
                # Get the full path to the file
                old_file_path = os.path.join(root, file_name)
                new_file_path = os.path.join(root, new_file_name)
                # Rename the file
                shutil.move(old_file_path, new_file_path)
                print(f"Renamed file: {old_file_path} to {new_file_path}")
