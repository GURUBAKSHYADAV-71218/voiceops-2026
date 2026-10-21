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

## 4. Evaluation and Testing

### Dataset Validation
The dataset validation script passed checks across all 9 supplied CSV files and the knowledge-base documents. Checks covered data integrity, key relationships, order calculations, verification gates, and company naming.

### Retrieval Evaluation
The current retrieval evaluation passed 43 of 47 evaluated questions (91.5%). This measures retrieval success only; it should not be interpreted as overall answer accuracy or factual correctness.

### Automated Tests
All 5 automated tests passed. These cover agent-core behaviour and a mocked multi-audio pipeline, including conversation-history handling and expected output artifacts. The mocked pipeline test does not establish that the complete live speech-to-answer-to-speech flow works end-to-end.

### Baseline vs. RAG Comparison
A comparison script and manual rating rubric are provided in `evaluation/comparison.py` and `evaluation/RATING_GUIDE.md`. Each answer can be rated from 1–5 for groundedness, correctness, and helpfulness. Comparative results remain pending until answers have been generated and reviewed. No comparative performance claim is made at this stage.

### Limitations
Live end-to-end validation and the baseline-versus-RAG experiment remain pending because of limited LLM API quota. These results will be reported only after the relevant tests have actually completed.

## 5. Limitations and Next Steps
1. Complete a live end-to-end voice test using one audio file.
2. Run and document the prompt-only versus RAG comparison.
3. Review failures and skipped cases against the supplied evaluation criteria.
4. Verify setup and execution from a clean environment with the provided dataset.
5. Record a short demo and finalize the report within the competition's page limit.

## 6. Reproducibility and Security
Configure API keys locally using `.env`; never commit secrets. Install dependencies from `requirements.txt`. Keep the supplied dataset in the expected local folders and validate it with `python validate_dataset.py` before running the application. Follow the README for the exact setup and execution commands.