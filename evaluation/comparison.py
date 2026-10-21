
import argparse
import csv
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUESTIONS = ROOT / "practice" / "questions.csv"
OUT = ROOT / "evaluation" / "baseline_vs_rag.csv"

RATING_FIELDS = [
    "baseline_groundedness",
    "baseline_correctness",
    "baseline_helpfulness",
    "rag_groundedness",
    "rag_correctness",
    "rag_helpfulness",
]


def main():
    parser = argparse.ArgumentParser(
        description="Compare baseline and RAG support answers."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of practice questions; use 0 for all",
    )
    args = parser.parse_args()

    if args.limit < 0:
        parser.error("--limit must be 0 or greater")

    if not QUESTIONS.is_file():
        raise SystemExit(f"Questions file not found: {QUESTIONS}")

    with QUESTIONS.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise SystemExit("No practice questions found.")

    if args.limit > 0:
        rows = rows[:args.limit]

    from src.baseline import ask_support
    from src.agent_core import respond_to_text

    OUT.parent.mkdir(parents=True, exist_ok=True)

    source_fields = list(rows[0].keys())
    fields = source_fields + [
        "baseline_answer",
        "rag_answer",
        *RATING_FIELDS,
        "evaluation_status",
        "error",
    ]

    completed = 0

    with OUT.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        f.flush()

        for index, row in enumerate(rows, 1):
            result = {key: row.get(key, "") for key in source_fields}
            result.update({
                "baseline_answer": "",
                "rag_answer": "",
                **{key: "" for key in RATING_FIELDS},
                "evaluation_status": "failed",
                "error": "",
            })

            question_id = row.get("id", str(index))
            print(f"\n{index}/{len(rows)} — Question {question_id}")

            try:
                result["baseline_answer"] = ask_support(row["question"])
            except Exception as exc:
                result["error"] = (
                    f"baseline: {type(exc).__name__}: {exc}"
                )

            try:
                answer, _ = respond_to_text(row["question"])
                result["rag_answer"] = answer
            except Exception as exc:
                rag_error = f"RAG: {type(exc).__name__}: {exc}"
                result["error"] = (
                    f"{result['error']} | {rag_error}"
                    if result["error"] else rag_error
                )

            if result["baseline_answer"] and result["rag_answer"]:
                result["evaluation_status"] = "completed"
                completed += 1
            elif result["baseline_answer"] or result["rag_answer"]:
                result["evaluation_status"] = "partial"

            writer.writerow(result)
            f.flush()

            print(f"Status: {result['evaluation_status']}")
            if result["error"]:
                print(f"Error: {result['error']}")

            time.sleep(0.2)

    print(f"\nCompleted comparisons: {completed}/{len(rows)}")
    print(f"Saved results: {OUT}")
    print("\nManual rating guide (score each answer from 1 to 5):")
    print("Groundedness: supported by the provided knowledge sources.")
    print("Correctness: factually and procedurally correct.")
    print("Helpfulness: clear, relevant, and useful to the customer.")
    print("Leave ratings blank until you have reviewed the answers.")


if __name__ == "__main__":
    main()
