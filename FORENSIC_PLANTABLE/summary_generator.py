import json
from pathlib import Path

def generate_summary(reports_dir="reports", output_file="FORENSIC_SUMMARY.md"):
    reports_path = Path(reports_dir)
    manifest_path = reports_path / "manifest.json"
    
    if not manifest_path.exists():
        print("No manifest found. Skip summary generation.")
        return

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    summary_lines = [
        "# 🧊 Forensic Processing Summary",
        f"Generated on: {Path('.').absolute()}",
        f"Total Files Processed: {len(manifest)}",
        "",
        "| Filename | Hash (SHA-256) | Status | Report |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for file_hash, data in manifest.items():
        report_file = Path(data['report_file'])
        if report_file.exists():
            with open(report_file, 'r') as f:
                report_data = json.load(f)
                status = report_data.get('status', 'unknown')
        else:
            status = "report_missing"
            
        filename = Path(data['path']).name
        summary_lines.append(f"| {filename} | `{file_hash[:16]}...` | {status} | [View Report]({data['report_file']}) |")

    with open(output_file, 'w') as f:
        f.write("\n".join(summary_lines))
    print(f"Summary generated: {output_file}")

if __name__ == "__main__":
    generate_summary()