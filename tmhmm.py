import biolib
import argparse
import tempfile
import os
import platform
import shutil
import logging
import stat
import glob
import time
from pathlib import Path, PureWindowsPath
import subprocess

logging.basicConfig(level=logging.DEBUG)


def setup_temp_dir(temp_dir):
    # Check if we're running in WSL
    if 'microsoft-standard' in platform.uname().release.lower():
        # Use a WSL-compatible temp directory
        temp_dir = '/tmp/tmhmm_temp'

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    tempfile.tempdir = temp_dir
    os.environ['TEMP'] = temp_dir
    os.environ['TMP'] = temp_dir
    logging.debug(f'TEMP directory set to: {tempfile.gettempdir()}')
    logging.debug(f'OS environment TEMP: {os.environ["TEMP"]}')
    logging.debug(f'OS environment TMP: {os.environ["TMP"]}')
    # We don't need to change permissions in WSL
    if 'microsoft-standard' not in platform.uname().release.lower():
        os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        logging.debug(f'Set full permissions for the temp directory')


def convert_path_to_wsl(path):
    # Check if the path is already a WSL path
    if path.startswith('/mnt/'):
        return path

    # Convert Windows path to WSL path
    try:
        # Try to convert as a Windows path
        windows_path = PureWindowsPath(path)
        drive = windows_path.drive.lower().rstrip(':')
        path_without_drive = str(windows_path.relative_to(windows_path.anchor))
        return f"/mnt/{drive}/{path_without_drive}"
    except ValueError:
        # If it's not a valid Windows path, assume it's already a valid path
        return path


def run_deeptmhmm(fasta_file, output_dir):
    print(f"Loading DeepTMHMM...")
    deeptmhmm = biolib.load('DTU/DeepTMHMM:1.0.24')

    wsl_fasta_file = convert_path_to_wsl(fasta_file)
    wsl_output_dir = convert_path_to_wsl(output_dir)

    print(f"Original fasta file path: {fasta_file}")
    print(f"Converted WSL fasta file path: {wsl_fasta_file}")
    print(f"Desired output directory: {wsl_output_dir}")

    print(f"Running DeepTMHMM on file: {wsl_fasta_file}")

    try:
        job = deeptmhmm.cli(args=['--fasta', wsl_fasta_file], machine='local')
    except Exception as e:
        print(f"Failed to start DeepTMHMM: {e}")
        return
    print("Waiting for job to complete...")
    job.wait()  # Wait for the job to finish

    print("Job status:", job.get_status())
    print("Stdout:")
    print(job.get_stdout().decode())
    print("Stderr:")
    print(job.get_stderr().decode())

    # Add a delay to ensure all files are written
    time.sleep(5)

    # Create the output directory if it doesn't exist
    os.makedirs(wsl_output_dir, exist_ok=True)

    # Biolib output directory
    biolib_output = os.path.expanduser('~/.biolib/output')

    if not os.path.exists(biolib_output):
        print(f"Biolib output directory does not exist: {biolib_output}")
        return

    files_moved = False

    # List of file extensions to look for
    extensions = ['.gff3', '.txt', '.json']

    for ext in extensions:
        print(f"Searching for *{ext} files in {biolib_output}...")
        for file in glob.glob(f"{biolib_output}/**/*{ext}", recursive=True):
            if 'deeptmhmm' in file.lower() or 'tmhmm' in file.lower():
                print(f"Found result file: {file}")
                dest_file = os.path.join(wsl_output_dir, os.path.basename(file))
                if os.path.abspath(file) != os.path.abspath(dest_file):
                    shutil.copy2(file, dest_file)
                    print(f"Copied to output directory: {dest_file}")
                    files_moved = True
                else:
                    print(f"File already in output directory: {file}")

    if files_moved:
        print(f"Files moved to '{wsl_output_dir}' directory")
    else:
        print("No new output files found.")

    print("Contents of the output directory:")
    for item in os.listdir(wsl_output_dir):
        print(f" - {item}")

    print("Current working directory:", os.getcwd())
    print("Contents of current working directory:")
    for item in os.listdir():
        print(f" - {item}")

    # Search for any files created or modified in the last 5 minutes
    print("Searching for recently created or modified files...")
    current_time = time.time()
    for root, dirs, files in os.walk('.'):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.getmtime(file_path) > current_time - 300:  # 300 seconds = 5 minutes
                print(f"Recent file: {file_path}")

    # Check biolib's default output location
    biolib_output = os.path.expanduser('~/.biolib/output')
    if os.path.exists(biolib_output):
        print(f"Contents of biolib output directory ({biolib_output}):")
        for item in os.listdir(biolib_output):
            print(f" - {item}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run DeepTMHMM on a FASTA file')
    parser.add_argument('--fasta', type=str, required=True, help='Path to the input FASTA file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output directory')
    args = parser.parse_args()

    if 'microsoft-standard' in platform.uname().release.lower():
        new_temp_dir = '/tmp/tmhmm_temp'
    else:
        new_temp_dir = "C:/Projects/tmhmm/Temp"

    setup_temp_dir(new_temp_dir)
    run_deeptmhmm(args.fasta, args.output)

    print("Final check:")
    print("Current working directory:", os.getcwd())
    print("Contents of current working directory:")
    for item in os.listdir():
        print(f" - {item}")
