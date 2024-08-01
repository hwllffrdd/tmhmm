import biolib
import argparse
import tempfile
import os
import platform
import logging
import stat
from pathlib import PureWindowsPath

logging.basicConfig(level=logging.DEBUG)


def setup_temp_dir(temp_dir):
    if 'microsoft-standard' in platform.uname().release.lower():
        temp_dir = '/tmp/tmhmm_temp'

    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    tempfile.tempdir = temp_dir
    os.environ['TEMP'] = temp_dir
    os.environ['TMP'] = temp_dir
    logging.debug(f'TEMP directory set to: {tempfile.gettempdir()}')
    logging.debug(f'OS environment TEMP: {os.environ["TEMP"]}')
    logging.debug(f'OS environment TMP: {os.environ["TMP"]}')
    if 'microsoft-standard' not in platform.uname().release.lower():
        os.chmod(temp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        logging.debug(f'Set full permissions for the temp directory')


def convert_path_to_wsl(path):
    if path.startswith('/mnt/'):
        return path
    try:
        windows_path = PureWindowsPath(path)
        drive = windows_path.drive.lower().rstrip(':')
        path_without_drive = str(windows_path.relative_to(windows_path.anchor))
        return f"/mnt/{drive}/{path_without_drive}"
    except ValueError:
        return path


def run_deeptmhmm(fasta_file, output_dir):
    print(f"Loading DeepTMHMM...")
    deeptmhmm = biolib.load('DTU/DeepTMHMM:1.0.24')

    wsl_fasta_file = convert_path_to_wsl(fasta_file)
    wsl_output_dir = convert_path_to_wsl(output_dir)

    print(f"Running DeepTMHMM on file: {wsl_fasta_file}")
    print(f"Output will be saved to: {wsl_output_dir}")

    try:
        job = deeptmhmm.cli(args=['--fasta', wsl_fasta_file], machine='local')
    except Exception as e:
        print(f"Failed to start DeepTMHMM: {e}")
        return

    print("Waiting for job to complete...")
    job.wait()

    print("Job status:", job.get_status())

    # Save all output files
    print(f"Saving output files to {wsl_output_dir}")
    job.save_files(output_dir=wsl_output_dir)

    # Optionally, save specific file types if needed
    # job.save_files(output_dir=wsl_output_dir, path_filter='*.gff3')
    # job.save_files(output_dir=wsl_output_dir, path_filter='*.txt')
    # job.save_files(output_dir=wsl_output_dir, path_filter='*.json')

    print("Contents of the output directory:")
    for item in os.listdir(wsl_output_dir):
        print(f" - {item}")

    print("Job completed successfully.")


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
