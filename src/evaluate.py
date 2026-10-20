
import csv
import re
from pathlib import Path
from src.rag import retrieve_policy

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "practice" / "questions.csv"
KB_DIR = ROOT / "kb"

# Read all practice questions.
with DATA_FILE.open(encoding="utf-8-sig", newline="") as f:
    questions = list(csv.DictReader(f))

# Index section IDs that actually exist in the knowledge base.
kb_ids = set()

for path in KB_DIR.glob("*.md"):
    text = path.read_text(encoding="utf-8")
    kb_ids.update(re.findall(r"(?m)^##\s+\[([A-Z]+-\d+)\]", text))

passed = 0
failed = 0
skipped = 0
results = []

for row in questions:
    qid = row["id"]
    question = row["question"]
    evidence = row.get("gold_evidence", "").strip()

    if not evidence:
        skipped += 1
        results.append((qid, "SKIP", "No gold evidence"))
        continue

    # Extract policy section IDs, e.g. RET-6 or WAR-2.
    expected_ids = re.findall(
        r"(?<![A-Z0-9-])([A-Z]{2,}-\d+)(?![A-Z0-9-])",
        evidence.upper()
    )

    # Keep only IDs that exist in the indexed KB.
    expected_kb_ids = [item for item in expected_ids if item in kb_ids]

    chunks = retrieve_policy(question, top_k=10)
    retrieved = "\n".join(chunks)

    # Only count a section as retrieved if its exact ID appears.
    found_ids = set(
        re.findall(r"\[([A-Z]+-\d+)\]", retrieved.upper())
    )

    if expected_kb_ids:
        matched = sorted(set(expected_kb_ids) & found_ids)
        ok = bool(matched)
        detail = (
            f"KB IDs found: {', '.join(matched)}"
            if ok
            else f"Expected KB IDs: {', '.join(expected_kb_ids)}"
        )
    else:
        # Product/CSV-only evidence is not verified by this KB-only test.
        skipped += 1
        results.append((qid, "SKIP", "No verifiable KB section ID"))
        continue

    if ok:
        passed += 1
        results.append((qid, "PASS", detail))
    else:
        failed += 1
        results.append((qid, "FAIL", detail))

tested = passed + failed

print("\nKB evidence-ID retrieval check")
print(f"PASS: {passed}")
print(f"FAIL: {failed}")
print(f"SKIP: {skipped}")
if tested:
    print(f"KB section retrieval rate: {passed}/{tested} ({passed / tested:.1%})")

for qid, status, detail in results:
    print(f"{status:4} {qid}: {detail}")
