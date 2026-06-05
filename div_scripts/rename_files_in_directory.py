import os

def rename_files_in_directory(directory: str, files_containing: str, split_on_before_bpname: str = "", split_on_after_bpname: str = "", prefix_new_name: str = "", suffix_new_name: str = ""):
    """Renames all files in a directory with the old name to the new name."""
    for file in os.listdir(directory):
        if files_containing in file:
            # Check if we need to split the file name
            if split_on_before_bpname and split_on_after_bpname:
                base_name = file.split(split_on_before_bpname)[1].split(split_on_after_bpname)[0]
            elif split_on_before_bpname:
                base_name = file.split(split_on_before_bpname)[1]
            elif split_on_after_bpname:
                base_name = file.split(split_on_after_bpname)[0]
            else:
                base_name = file

            # Extract the file extension
            _, file_extension = os.path.splitext(file)
            
            # Combine the new name with the file extension
            new_name = prefix_new_name + base_name + suffix_new_name + file_extension
            
            os.rename(os.path.join(directory, file), os.path.join(directory, new_name))

