import os
import hashlib
import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("forensic_engine.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ForensicEngine")

class ForensicEngine:
    """
    High-power forensic media processing engine.
    Handles hashing, metadata extraction, and transcription.
    """
    
    SUPPORTED_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.mp4', '.mov', '.avi', '.mkv', '.flac'}

    def __init__(self, output_dir: str = "reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.manifest_path = self.output_dir / "manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        if self.manifest_path.exists():
            try:
                with open(self.manifest_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load manifest: {e}")
        return {}

    def _save_manifest(self):
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=4)

    def get_file_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        path = Path(file_path)
        stat = path.stat()
        return {
            "filename": path.name,
            "path": str(path.absolute()),
            "size_bytes": stat.st_size,
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "extension": path.suffix.lower()
        }

    def transcribe_whisperx(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Attempts to transcribe using WhisperX for high-quality timestamps and diarization.
        """
        logger.info(f"Starting WhisperX transcription for: {file_path}")
        try:
            # Command pattern for WhisperX
            # whisperx <file> --model large-v2 --diarize --highlight_words True --output_dir <dir>
            output_subdir = self.output_dir / "transcripts" / Path(file_path).stem
            output_subdir.mkdir(parents=True, exist_ok=True)
            
            cmd = [
                "whisperx",
                file_path,
                "--model", "base",  # Using base for speed in Termux, can be upgraded to large-v3
                "--diarize",
                "--output_dir", str(output_subdir),
                "--output_format", "all"
            ]
            
            # Note: In Termux/Android, we might need specific LD_LIBRARY_PATH or device considerations
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"WhisperX success for {file_path}")
                # Find the generated json file
                json_files = list(output_subdir.glob("*.json"))
                if json_files:
                    with open(json_files[0], 'r') as f:
                        return json.load(f)
            else:
                logger.error(f"WhisperX failed: {result.stderr}")
                return None
        except Exception as e:
            logger.exception(f"Error in WhisperX transcription: {e}")
            return None

    def transcribe_fallback(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Fallback to standard openai-whisper if whisperx is not available."""
        logger.info(f"Falling back to standard Whisper for: {file_path}")
        try:
            import whisper
            model = whisper.load_model("base")
            result = model.transcribe(file_path)
            return result
        except Exception as e:
            logger.error(f"Fallback transcription failed: {e}")
            return None

    def process_file(self, file_path: str, force: bool = False):
        file_hash = self.get_file_hash(file_path)
        
        if file_hash in self.manifest and not force:
            logger.info(f"Skipping already processed file: {file_path}")
            return

        logger.info(f"Processing: {file_path}")
        metapayload = self.extract_metadata(file_path)
        metadata["sha256"] = file_hash
        
        # Transcription
        transcript_payload = self.transcribe_whisperx(file_path)
        if not transcript_data:
            transcript_payload = self.transcribe_fallback(file_path)
        
        report = {
            "metadata": metadata,
            "processed_at": datetime.now().isoformat(),
            "status": "completed" if transcript_data else "metadata_only",
            "transcript": transcript_data
        }
        
        # Save individual report
        report_file = self.output_dir / f"{file_hash}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=4)
            
        # Update manifest
        self.manifest[file_hash] = {
            "path": str(file_path),
            "processed_at": report["processed_at"],
            "report_file": str(report_file)
        }
        self._save_manifest()
        logger.info(f"Completed processing: {file_path}")

    def scan_and_process(self, root_dir: str):
        """Recursively scan and process all media files."""
        root_path = Path(root_dir)
        for ext in self.SUPPORTED_EXTENSIONS:
            for file_path in root_path.rglob(f"*{ext}"):
                if "reports" in str(file_path): continue # Skip our own output
                try:
                    self.process_file(str(file_path))
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")

if __name__ == "__main__":
    engine = ForensicEngine()
    # By default, process the current directory
    engine.scan_and_process(".")
