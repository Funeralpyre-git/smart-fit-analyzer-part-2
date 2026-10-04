import csv
from pathlib import Path

def export_results(results: list, rejected_records: list, output_dir: Path):
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # export analysis_summary.csv
    summary_csv = out_path / "analysis_summary.csv"
    with open(summary_csv, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "session_id",
            "participant_id",
            "usable_samples",
            "total_samples",
            "classification",
            "avg_heart_rate",
            "avg_activity",
        ])

        for res in results:
            summaries = res.get("summaries", {})

            avg_hr = summaries.get("avg_heart_rate", "N/A")
            avg_act = summaries.get("avg_activity", "N/A")

            writer.writerow([
                res.get("session_id", "N/A"),
                res.get("participant_id", "N/A"),
                res.get("usable_observations", 0),
                res.get("total_observations", 0),
                res.get("classification", "unknown"),
                avg_hr if avg_hr is not None else "N/A",
                avg_act if avg_act is not None else "N/A",
            ])

    # export analysis_report.txt
    report_txt = out_path / "analysis_report.txt"
    with open(report_txt, mode="w", encoding="utf-8") as f:
        f.write("====================================================\n")
        f.write("        SMART FITNESS SESSION ANALYSIS REPORT        \n")
        f.write("====================================================\n\n")

        for res in results:
            f.write(f"Session ID    : {res.get('session_id')}\n")
            f.write(f"Participant ID: {res.get('participant_id')}\n")
            f.write(f"Usable samples: {res.get('usable_observations')}/{res.get('total_observations')}\n")
            f.write(f"Classification: {res.get('classification')}\n")
            f.write(f"Rationale     : {res.get('rationale')}\n")
            f.write("==================================================\n")

    # export rejected_records.txt
    rejected_txt = out_path / "rejected_records.txt"
    with open(rejected_txt, mode="w", encoding="utf-8") as f:
        f.write("=====================================================\n")
        f.write("              REJECTED CSV RECORDS LOG:              \n")
        f.write("=====================================================\n\n")

        if not rejected_records:
            f.write("No records were rejected.\n")
        else:
            for rec in rejected_records:
                f.write(f"{rec}\n")