# Python script to sort shots into folders
import argparse
import os
import shutil
from glob import glob
import re

def get_shot_dir_path(root_dir, file_path, summary_log):
    '''
    Gets the full file path of name.

    :param root_dir: Path to the root directory
    :type root_dir: LiteralString
    :param file_path: File path of file/directory
    :type name: String
    :param summary_log: Dict holding summary information about shots
    :type summary_log: Dict of two lists, "versions" and "subfolders"
    :return: LiteralString of new shot folder name and
            LiteralString of file path of name or None if file/dir named incorrectly 
    '''
    shot_dir = ""       # Final dir name
    shot_dir_path = ""  # File path of final dir name

    match = re.match(r"^(SHOT_\d{3})", os.path.basename(file_path))

    # Check if file/dir named correctly
    if match:
        shot_dir = match.group(1)
        shot_dir_path = os.path.join(root_dir, shot_dir)

        # Initialize shot in summary if not already present
        if shot_dir not in summary_log:
            summary_log[shot_dir] = {
                'versions': [],
                'subfolders': []
            }
    else:
        shot_dir_path = None
        
    return shot_dir, shot_dir_path

def move_files(root_dir, files, summary_log):
    '''
    Move files to their correct shot folder. 

    :param root_dir: File path to the root directory
    :type root_dir: LiteralString
    :param files: Set of the all the files' file paths in root_dir
    :type files: Set
    :param summary_log: Dict holding summary information about shots
    :type summary_log: Dict of two lists, "versions" and "subfolders"
    :return: Nothing
    '''
    for file in files:
        shot_dir, shot_dir_path = get_shot_dir_path(root_dir, file, summary_log)

        # Error check if shot_dir_path is valid
        if shot_dir_path == None:
            # Check that incorrectly named file isn't this python file!
            if not "shot_sorting.py" in file:
                print(f"File {file} is not named correctly.")
            continue

        # Create the shot directory if it doesn't exist
        if not os.path.exists(shot_dir_path):
            os.makedirs(shot_dir_path)

        # Add to summary information
        summary_log[shot_dir]['versions'].append(os.path.basename(file))

        # Move directory into newly named dir
        shutil.move(file, shot_dir_path)

def move_directories(root_dir, directories, summary_log):
    '''
    Move directories to their correct shot folder. Two possible cases.

    Case 1: Since the preview/final folder structure is preserved for a shot number, 
    just rename shot folder (helps to set up some directories for files later)
    Case 2: File with just version number in a folder with the shot name

    :param root_dir: File path to the root directory
    :type root_dir: LiteralString
    :param directories: Set of the all the directories' file paths in root_dir
    :type directories: Set
    :param summary_log: Dict holding summary information about shots
    :type summary_log: Dict of two lists, "versions" and "subfolders"
    :return: Nothing
    '''
    for directory in directories:
        shot_dir, shot_dir_path = get_shot_dir_path(root_dir, directory, summary_log)
        basename = os.path.basename(directory)

        # Error check if shot_dir_path is valid
        if shot_dir_path == None:
            print(f"Directory {directory} is not named correctly.")
            continue

        # Case 1
        shot_dir_preview_path = os.path.join(directory, "preview")
        shot_dir_final_path = os.path.join(directory, "final")

        is_shot_dir_preview_path = os.path.exists(shot_dir_preview_path)
        is_shot_dir_final_path = os.path.exists(shot_dir_final_path)

        # If preview/final folder exists
        if is_shot_dir_preview_path or is_shot_dir_final_path:
            try:
                # Add to summary information
                if is_shot_dir_preview_path:
                    summary_log[shot_dir]['subfolders'].append("preview")
                    version_file_path = basename + "/preview/" + os.listdir(shot_dir_preview_path)[0]
                    summary_log[shot_dir]['versions'].append(version_file_path)
                if is_shot_dir_final_path:
                    summary_log[shot_dir]['subfolders'].append("final")
                    version_file_path = basename + "/final/" + os.listdir(shot_dir_final_path)[0]
                    summary_log[shot_dir]['versions'].append(version_file_path)

                os.rename(directory, shot_dir_path)
                                                 
                break
            except:
                print("Error with renaming directory.") # TODO descriptive error message

        # Case 2
        # Create the shot directory if it doesn't exist
        if not os.path.exists(shot_dir_path):
            os.makedirs(shot_dir_path)

        summary_log[shot_dir]['subfolders'].append(basename)
        version_file_path = basename + "/" + os.listdir(directory)[0]
        summary_log[shot_dir]['versions'].append(version_file_path)

        # Move directory into newly named dir
        shutil.move(directory, shot_dir_path)

def organize_shot_files(root_dir):
    '''
    Organize the shot files and directories in root_dir.

    :param root_dir: File path to the root directory
    :type root_dir: LiteralString
    :return: Nothing
    '''
    # Initialize a list to log the movements
    summary_log = {}

    # Get all the files and directories matching the pattern for shots
    shot_pattern = os.path.join(root_dir, 'SHOT_*')
    shot_file_paths = glob(shot_pattern)

    # Separate directories and files into sets for linear access time (assumes unique file/directory names)
    directories = {item for item in shot_file_paths if os.path.isdir(item)}
    files = {item for item in shot_file_paths if os.path.isfile(item)}

    # Handle directories first
    move_directories(root_dir, directories, summary_log)

    # Handle files second
    move_files(root_dir, files, summary_log)

    # Create a summary file (summary.txt) in the root directory
    create_summary_file(summary_log, root_dir)

def get_latest_version(versions):
    '''
    Gets the file with the latest version from versions. Assumes that the versions increment from 1 and in order.

    :param versions: List of files
    :type versions: List
    :return: String of file name of latest version from versions
    '''
    latest_version = None

    # Assume the versions in order
    version_number = len(versions)

    # Format a version string in the format vxx, where xx is the version number.
    # If the version number is a single digit, fill left side with 0
    version_str = f"v{version_number:02d}"

    # Regex
    pattern = rf"v{version_str[1:]}"

    # Loop through the list and find the matching item
    for version in versions:
        if re.search(pattern, version):
            latest_version = version
            break
    
    return latest_version

def create_summary_file(summary_log, root_dir):
    '''
    Create a summary file with the following information:
    - Total shot number
    - For each shot...
        - Number of versions (summary_log value tuple index 0)
        - Latest version (summary_log value tuple index 1)
        - Subfolders (summary_log value tuple index 2)

    :param summary_log: Dict of summary information. Key for every shot, and two lists
                        "versions" and "subfolders"
    :type summary_log: Dict
    :param root_dir: File path to the root directory
    :type root_dir: LiteralString
    :return: Nothing
    '''
    # Sort dict (time consuming, but makes summary nicer)
    summary_log = dict(sorted(summary_log.items()))

    # Create file text based on summary_log information
    summary_log_text = []
    total_shots = len(summary_log)
    summary_log_text.append(f"Total Shots: {total_shots}\n")    # Total shot number

    # Print shot specific information
    for shot, shot_information in summary_log.items():
        summary_log_text.append(f"{shot}")  # Shot number
        summary_log_text.append(f"- Versions: {len(shot_information['versions'])}")   # Version number

        # Get latest version... assuming the versions are incremented in order (no skipped versions)
        latest_version = get_latest_version(shot_information['versions'])
        summary_log_text.append(f"- Latest Version: {latest_version}")

        # Check for subfolders, and format properly if they exist
        if shot_information['subfolders'] == []:
            summary_log_text.append("- Subfolders: None\n")
        else:
            subfolders = shot_information['subfolders']

            # Join list elements with commas
            subfolder_str = ', '.join(subfolders)

            summary_log_text.append(f"- Subfolders: {subfolder_str}\n")

    # Create summary file and write summary_log_text in line by line
    summary_file = os.path.join(root_dir, 'summary.txt')
    with open(summary_file, 'w') as f:
        for line in summary_log_text:
            f.write(line + '\n')

def parse_args():
    '''
    Parse CLI arguments.
    '''

    parser = argparse.ArgumentParser(description="Sort shot files into from input to output directory.")
    
    parser.add_argument(
        '--input',
        type=str,
        required=False,
        help="Path to the root directory containing the shot files."
    )
    
    parser.add_argument(
        '--output',
        type=str,
        required=False,
        help="Path to the directory where the sorted files and summary will be saved."
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    # Get current working directory file path
    root_directory = os.getcwd()

    # # Parse command-line arguments
    # args = parse_args()

    # # Organize shot files based on input and output paths provided
    # root_directory = args.input   # Use the input directory passed in the CLI
    # output_directory = args.output  # Use the output directory passed in the CLI
    
    organize_shot_files(root_directory)