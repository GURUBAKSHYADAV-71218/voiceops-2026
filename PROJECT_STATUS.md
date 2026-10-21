# VoiceOps 2026 — Project Status

## Goal
Submit a voice-enabled ZentroMart customer support agent for the FTTT 2026 capstone.

## Verified
- Dataset validation passed.
- Agent and mocked pipeline tests: 5/5 passed.
- Incorrect order verification does not reveal protected order details.
- Gnani.ai STT tested separately.
- Gnani.ai TTS tested separately.
- Retrieval evaluation: 43 PASS, 4 FAIL, 5 SKIP (91.5% of 47 retrieval checks passed).

## Not Yet Verified / Pending
- Full live audio → Gemini → TTS pipeline.
- Measured prompt-only vs RAG comparison and results CSV.
- Final report within 4 pages.
- Final demo recording within 2 minutes.
- Public GitHub repository and clean setup verification.

## Important Constraints
- Gemini free-tier quota was recently exhausted; avoid repeated retries.
- Never commit .env, API keys, .venv, or supplied dataset files.
- Preserve emergency_submission.zip and emergency_submission/ until a replacement submission is verified.
- Retrieval pass rate is not overall answer accuracy.
- Deadline: 25 October 2026, 11:59 PM IST.

## Next Priorities
1. Confirm report.md and demo_script.md are committed.
2. Complete baseline submission files and inspect the ZIP.
3. Run one real end-to-end audio test when Gemini quota permits.
4. Run prompt-only vs RAG comparison when quota permits.
5. Publish the repository, finalize report and demo, then run a final audit.

## Working Style
Use concise Hinglish and exact PowerShell commands. One step at a time. Avoid repeated audits and unnecessary README loops. Keep building; do not stop at status updates.
