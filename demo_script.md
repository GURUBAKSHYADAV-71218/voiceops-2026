# VoiceOps 2026 — 2-Minute Demo Script

## 0:00–0:15 — Introduction
“Hello, this is VoiceOps 2026, an AI-powered customer support agent for ZentroMart. It combines knowledge retrieval, order-support tools, ticket escalation, and voice processing.”

## 0:15–0:35 — Policy Questions
“The agent retrieves relevant information from the supplied knowledge base and uses it to answer customer questions. This helps keep responses grounded in the available company policies.”

**Show:** The relevant source documents and the retrieval/answer flow, or a previously saved result.

## 0:35–0:55 — Secure Order Lookup
“The agent supports order lookup through CSV-backed tools. Customer verification is required before protected order details can be disclosed.”

**Show:** The order lookup code and the verification test. Do not expose real API keys or sensitive customer details.

## 0:55–1:10 — Escalation
“When an issue needs further assistance, the agent can create an escalation ticket and retain the result for follow-up.”

**Show:** The ticket tool or a safe example of its output.

## 1:10–1:30 — Voice Pipeline
“The audio runner accepts supported audio files and saves the transcript, generated reply, retrieved source chunks, and a JSON result for each input.”

**Show:** The pipeline code and existing output artifacts. A mocked test is not proof of a complete live voice interaction.

## 1:30–1:50 — Evaluation
“Dataset validation passed across all nine supplied CSV files and the knowledge-base documents. All five automated tests passed. Retrieval evaluation passed 43 of 47 evaluated questions, or 91.5%. This is a retrieval metric, not overall answer accuracy.”

**Show:** The validation and test results.

## 1:50–2:00 — Honest Status
“The project includes a baseline-versus-RAG comparison script and a manual rating rubric. Live end-to-end voice validation and comparative evaluation remain pending because of the available LLM API quota.”

“Thank you.”
