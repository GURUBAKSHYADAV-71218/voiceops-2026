# VoiceOps 2026 — ZentroMart Customer Support Agent

## 1. Problem Statement
Build a customer-support agent for ZentroMart that answers policy questions using the supplied knowledge base, maintains conversation context, supports verified order lookup, and creates escalation tickets.

## 2. System Architecture
- **Knowledge retrieval:** Markdown knowledge documents are retrieved for policy-grounded responses.
- **Language model:** Gemini generates conversational answers using the retrieved context.
- **Order lookup:** CSV-backed tools perform order lookup and require verification before revealing order details.
- **Ticketing:** The support tool records escalation tickets.
- **Voice:** Gnani.ai provides speech-to-text (STT) and text-to-speech (TTS).
- **Pipeline:** Customer audio → transcription → retrieval and response → saved text/audio outputs and source chunks.

## 3. Implementation
The project separates agent logic, retrieval, voice processing, business tools, and evaluation scripts. The audio runner supports WAV, MP3, M4A, OGG, and FLAC inputs and stores per-file transcripts, replies, retrieved source chunks, and JSON status records.

## 4. Testing and Current Results
- Dataset validation: passed for the supplied dataset.
- Unit tests: 4 agent-core tests passed.
- Mocked audio-pipeline test: passed for multi-file processing, conversation history, and expected output artifacts.
- Order verification security check: passed for incorrect verification.
- Knowledge-base retrieval evaluation: 43 PASS, 4 FAIL, 5 SKIP; reported retrieval rate 43/47 (91.5%).
- Gnani.ai STT and TTS were tested separately.
- **Limitation:** The full live audio → Gemini response → TTS pipeline has not yet been verified end-to-end. The mocked pipeline test does not establish live-service success.

The retrieval figure above measures the project's current retrieval checks; it is not an overall answer-accuracy score.

## 5. Baseline vs. RAG Experiment
The project includes a prompt-only baseline and a retrieval-augmented generation (RAG) comparison script. The experiment has not yet produced a completed results CSV. No measured baseline-versus-RAG performance claim is made in this draft. Run the comparison when API quota is available, inspect answers against the supplied evaluation questions, and record the method and results here.

## 6. Limitations and Next Steps
1. Complete a live end-to-end voice test using one audio file.
2. Run and document the prompt-only versus RAG comparison.
3. Review failures and skipped cases against the supplied evaluation criteria.
4. Verify setup and execution from a clean environment with the provided dataset.
5. Record a short demo and finalize the report within the competition's page limit.

## 7. Reproducibility and Security
Configure API keys locally using `.env`; never commit secrets. Install dependencies from `requirements.txt`. Keep the supplied dataset in the expected local folders and validate it with `python validate_dataset.py` before running the application. Follow the README for the exact setup and execution commands.
