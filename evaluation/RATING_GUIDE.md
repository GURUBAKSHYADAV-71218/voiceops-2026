# Baseline vs RAG — Manual Rating Guide

Rate each answer independently on a 1–5 scale.

## 1. Groundedness
1 — Unsupported or contradicts the supplied knowledge.
2 — Mostly unsupported; major claims lack evidence.
3 — Partially supported; some claims are unverified.
4 — Well supported, with minor gaps.
5 — Claims are supported by the supplied knowledge.

## 2. Correctness
1 — Major factual or procedural errors.
2 — Several important errors.
3 — Partly correct; some important details missing or wrong.
4 — Correct overall, with minor issues.
5 — Factually and procedurally correct.

## 3. Helpfulness
1 — Does not address the customer's need.
2 — Barely useful or confusing.
3 — Partly useful but incomplete.
4 — Clear and useful, with minor omissions.
5 — Clear, relevant, complete, and actionable.

## Rating procedure
- Rate baseline and RAG answers independently.
- Use the same rubric for both systems.
- Use the question and supplied knowledge documents to verify claims.
- Leave ratings blank if an answer has not been reviewed.
- Do not treat retrieval rate as answer accuracy.
- Report the number of answers actually rated and compare mean scores
  only across answers with completed ratings.
- Record API failures separately; do not count failed answers as zero.

