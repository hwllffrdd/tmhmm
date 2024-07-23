import biolib
import argparse
import tempfile
import os
import platform
import shutil
import logging
import stat
from pathlib import Path, PureWindowsPath

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

    print(f"Running DeepTMHMM on file: {wsl_fasta_file}")

    print(f"Checking if file exists: {os.path.exists(wsl_fasta_file)}")
    print(f"File contents:")
    try:
        with open(wsl_fasta_file, 'r') as f:
            print(f.read()[:100])  # Print first 100 characters
    except Exception as e:
        print(f"Error reading file: {e}")

    try:
        # Use the converted paths directly in the command
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

    default_output_dir = 'deeptmhmm_results'

    if os.path.exists(default_output_dir):
        if not os.path.exists(wsl_output_dir):
            os.makedirs(wsl_output_dir)
        for item in os.listdir(default_output_dir):
            s = os.path.join(default_output_dir, item)
            d = os.path.join(wsl_output_dir, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, dirs_exist_ok=True)
            else:
                shutil.copy2(s, d)
        print(f"Files saved in '{wsl_output_dir}' directory")
        shutil.rmtree(default_output_dir)
    else:
        print(f"Warning: Expected output directory '{default_output_dir}' not found")

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
