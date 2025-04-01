# Test A Shot Management Automation
A Python script to manage shot files in a VFX pipeline.

## Required Dependencies and Installations
The required dependencies and installations are as follows:
- Python 3.x.x
- os (included with Python)
- argparse (included with Python)
- shutil (included with Python)
- glob (included with Python)
- re (included with Python)

## How To Run
1. Navigate to the directory where compare_directories.py is stored via terminal,
2. Run **python shot_sorting.py**.

## Features
- Organizes Files:
    - Moves all shot files into subdirectories based on shot number (e.g., SHOT_001,
    SHOT_002).
    - Maintains existing subfolder structures (like preview, final) within the shot directory.
    - Handles mixed file types (.mov and .exr) and nested subfolders.
- Generates a Summary File (summary.txt):
    - Contains the total number of shots.
    - Lists the number of versions for each shot.
    - Identifies the latest version for each shot.
    - Lists any subfolders found within each shot.
- Handles malformed filenames
- Handles missing directories

## In the Works
- CLI for specifying input and output directories

## Assumptions
- Only one version in preview/final folders.
- Versions for a shot start at version 1 and increment in order