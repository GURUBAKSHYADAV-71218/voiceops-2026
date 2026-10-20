import argparse
import csv
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "practice" / "questions.csv"
OUT = ROOT / "evaluation" / "baseline_vs_rag.csv"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10,
                        help="Number of practice questions; use 0 for all")
    args = parser.parse_args()

    with QUESTIONS.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if args.limit > 0:
        rows = rows[:args.limit]

    from src.baseline import ask_support
    from src.agent_core import respond_to_text

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0].keys()) + [
        "baseline_answer", "rag_answer", "evaluation_status", "error"
    ] if rows else []

    completed = 0
    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()

        for index, row in enumerate(rows, 1):
            result = dict(row)
            result.update({
                "baseline_answer": "",
                "rag_answer": "",
                "evaluation_status": "failed",
                "error": "",
            })

            try:
                result["baseline_answer"] = ask_support(row["question"])
                answer, _ = respond_to_text(row["question"])
                result["rag_answer"] = answer
                result["evaluation_status"] = "completed"
                completed += 1
                print(f"{index}/{len(rows)} completed: {row.get('id', index)}")

            except Exception as exc:
                result["error"] = f"{type(exc).__name__}: {exc}"
                print(f"Stopped at {row.get('id', index)}: {result['error']}")
                writer.writerow(result)
                f.flush()
                break

            writer.writerow(result)
            f.flush()
            time.sleep(0.2)

    print(f"\nCompleted comparisons: {completed}/{len(rows)}")
    print(f"Saved results: {OUT}")


if __name__ == "__main__":
    main()
