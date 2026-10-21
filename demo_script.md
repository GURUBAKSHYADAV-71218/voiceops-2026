# VoiceOps 2026 — 2-Minute Demo Script

## 0:00–0:15 | Introduction
"VoiceOps is a voice-enabled customer support agent for ZentroMart. It combines knowledge-base retrieval, conversation handling, verified order lookup, ticket escalation, and Gnani.ai speech services."

## 0:15–0:35 | Policy question
"First, I ask a customer-support policy question. The agent retrieves relevant knowledge-base content and uses it to formulate a response."

Show: one policy question, the response, and retrieved source chunks.

## 0:35–0:55 | Order security
"Order information is protected by a verification step. The agent must not disclose verified order details when verification fails."

Show: an order lookup request and the verification prompt. Do not display real API keys or sensitive customer data.

## 0:55–1:15 | Escalation
"When a customer needs human assistance, the system can create a support ticket and report the result."

Show: a successful ticket creation and its confirmation, using test data.

## 1:15–1:35 | Voice workflow
"The audio runner transcribes customer audio, processes the request, and saves the transcript, reply, retrieved source chunks, and synthesized audio."

Show: the output folder and one completed live example, if available.

## 1:35–1:50 | Testing
"The current offline checks include five passing unit and pipeline tests, dataset validation, and a retrieval evaluation with 43 passes, 4 failures, and 5 skipped cases."

Clarify that the multi-file pipeline test uses mocks and that the retrieval result is not overall answer accuracy.

## 1:50–2:00 | Conclusion
"Next, I am completing the live end-to-end voice check and the measured prompt-only versus RAG comparison."
