#!/bin/bash

# Autonomous Forensic Plantable Container Launcher
# This script ensures dependencies are met and runs the forensic scanner.

echo "--------------------------------------------------"
echo "🧊 FORENSIC PLANTABLE CONTAINER ACTIVATED"
echo "--------------------------------------------------"

# 1. Dependency Check
echo "[*] Checking Python dependencies..."
if ! command -v whisperx &> /dev/null
then
    echo "[!] WhisperX not found. Attempting non-interactive install..."
    # Attempting to install whisperx and its requirements
    pip install whisperx --quiet
else
    echo "[+] WhisperX detected."
fi

# 2. Setup Environment
export PYTHONUNBUFFERED=1

# 3. Execution Loop (Plantable behavior)
echo "[*] Starting processing loop in $(pwd)..."
echo "[*] Reports will be generated in the './reports' directory."

while true; do
    echo "[$(date)] Scanning for new media..."
    python3 forensic_engine.py
    
    echo "[*] Generating summary report..."
    python3 summary_generator.py
    
    echo "[*] Scan complete. Sleeping for 60 seconds (Control+C to stop)..."
    sleep 60
done
