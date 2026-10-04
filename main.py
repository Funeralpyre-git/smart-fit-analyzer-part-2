from analyzer import FitnessAnalyzer
import argparse
from pathlib import Path
from loader import load_participants, load_sessions
from reporter import export_results

def main():
    parser = argparse.ArgumentParser(description="Smart Fitness Session Analyzer")

    # single file path
    parser.add_argument("--profiles", type=str, required=True, help="Path to participants CSV file")

    # list of file paths
    parser.add_argument("--sessions", type=str, nargs="+", required=True, help="Paths to session CSV files")

    # single output directory
    parser.add_argument("--output", type=str, default="output", help="Output directory path")

    args = parser.parse_args()

    profiles_path = Path(args.profiles)
    session_paths = [Path(p) for p in args.sessions]
    output_dir = Path(args.output)

    rejected_records = []

    print("Loading profiles...")
    participants = load_participants(profiles_path, rejected_records)

    print("Loading sessions...")
    sessions = load_sessions(session_paths, participants, rejected_records)

    print("Analyzing sessions...")
    analyzer = FitnessAnalyzer.create_default()
    results = [analyzer.analyze(sess) for sess in sessions.values()]

    print("Generating report...")
    export_results(results, rejected_records, output_dir)

    print("\n" + "=" * 50)
    print("           PROCESSING COMPLETE")
    print("=" * 50)
    print(f"Accepted Sessions Processed: {len(results)}")
    print(f"Rejected Records Logged    : {len(rejected_records)}")
    print(f"Report Directory           : {output_dir.resolve()}")
    print("=" * 50)

if __name__ == '__main__':
    main()
