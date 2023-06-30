import os
import shutil

root_dir = r'C:\Users\kamra\DataspellProjects\images\2022'  # path of the root directory
destination_dir = r"C:\Users\kamra\DataspellProjects\images\dest\labels\val"  # path of the destination directory

# Iterate over all the directories in the root directory
for dir_name in os.listdir(root_dir):
    specific_dir_path = os.path.join(root_dir, dir_name, 'YOLODataset', 'labels', 'val')
    if os.path.isdir(specific_dir_path):
        # Copy all files in this directory
        for file in os.listdir(specific_dir_path):
            source_file_path = os.path.join(specific_dir_path, file)
            destination_file_path = os.path.join(destination_dir, file)

            # If a file with the same name already exists in the destination directory
            if os.path.exists(destination_file_path):
                # Append a number to the filename
                base, extension = os.path.splitext(file)
                i = 1
                while os.path.exists(os.path.join(destination_dir, f"{base}_{i}{extension}")):
                    i += 1
                destination_file_path = os.path.join(destination_dir, f"{base}_{i}{extension}")

            # Copy the file
            shutil.copy(source_file_path, destination_file_path)
