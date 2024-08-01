# DeepTMHMM Wrapper

This Python script provides a wrapper for running DeepTMHMM, a tool for predicting transmembrane helices in proteins. It's designed to work in a Windows Subsystem for Linux (WSL) environment and uses the Biolib package to interface with DeepTMHMM.

## Features

- Runs DeepTMHMM on a given FASTA file
- Converts Windows paths to WSL-compatible paths
- Saves output files to a specified directory
- Works in WSL environment

## Prerequisites

- Python 3.x
- WSL (Windows Subsystem for Linux)
- Biolib package
- DeepTMHMM (accessible via Biolib)

## Installation

1. Clone this repository:
   git clone https://github.com/hwllffrdd/tmhmm.git
   

2. Install the required Python packages:
   pip install biolib

## Usage

Run the script from the command line with the following arguments:
  python tmhmm.py --fasta <path_to_fasta_file> --output <path_to_output_directory>

For example:
  python tmhmm.py --fasta /mnt/c/Projects/tmhmm/human.fasta --output /mnt/c/Projects/tmhmm/deeptmhmm_results`

## Output

The script will create the specified output directory (if it doesn't exist) and save the DeepTMHMM results there. The output typically includes:
- GFF3 files
- TXT files
- JSON files
- Other DeepTMHMM output files

## Notes

- This script is designed to work in a WSL environment. Make sure you're running it in WSL if you're on a Windows machine.
- Paths should be provided in WSL format (e.g., `/mnt/c/...` instead of `C:\...`).

## Contributing

Contributions, issues, and feature requests are welcome.
