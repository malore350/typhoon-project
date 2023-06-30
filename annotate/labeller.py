import os

root_dir = r'C:\Users\kamra\DataspellProjects\images\2022'  # path of the root directory

mapping = {
    "2": "0",
    "3": "1",
    "4": "2",
    "5": "3"
}

# Iterate over all the directories in the root directory
for dir_name in os.listdir(root_dir):
    specific_dir_path = os.path.join(root_dir, dir_name, 'YOLODataset', 'labels', 'train')
    if os.path.isdir(specific_dir_path):
        # Get the last number from the dir_name
        last_number = dir_name.split('_')[-1]

        # Get the new first number from the mapping
        new_first_number = mapping.get(last_number)

        # For every txt file
        for file_name in os.listdir(specific_dir_path):
            if file_name.endswith('.txt'):
                file_path = os.path.join(specific_dir_path, file_name)

                # Read the file
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                # Edit the first number of each line
                for i, line in enumerate(lines):
                    parts = line.split()
                    parts[0] = new_first_number
                    lines[i] = ' '.join(parts) + '\n'

                # Write the file
                with open(file_path, 'w') as file:
                    file.writelines(lines)
