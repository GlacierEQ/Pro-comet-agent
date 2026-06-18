# 🧊 Forensic Plantable Container

This folder is a self-contained autonomous forensic processor.

## 🚀 How to use
1. **Copy** this entire `FORENSIC_PLANTABLE` folder into any directory you want to process (e.g., your Dropbox mount, Google Drive folder, or a local evidence folder).
2. **Open Termux** and navigate into the folder:
   ```bash
   cd path/to/FORENSIC_PLANTABLE
   ```
3. **Execute** the plant script:
   ```bash
   ./plant.sh
   ```

## 🛠️ What it does
- **Recursive Scan:** It finds every audio and video file in its current directory and all subdirectories.
- **Forensic Hashing:** Generates a SHA-256 hash for every file to ensure evidentiary integrity.
- **Metadata Extraction:** Captures file timestamps, sizes, and paths.
- **WhisperX Transcription:** Performs high-quality transcription with timestamps and speaker diarization (Speaker 0, Speaker 1, etc.).
- **Deduplication:** Uses the `manifest.json` to avoid re-processing files it has already seen, even if they are moved.
- **Persistent Reports:** Saves all findings in the `reports/` folder as structured JSON and transcript files.

## 📁 Output Structure
- `reports/manifest.json`: The master index of all processed files and their hashes.
- `reports/[hash].json`: Detailed forensic report for a specific file.
- `reports/transcripts/[filename]/`: Contains .json, .txt, .srt, and .vtt transcriptions.

## ⚠️ Requirements
- Python 3.10+
- FFmpeg
- WhisperX (the script attempts to install this automatically)
