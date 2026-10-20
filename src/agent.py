from pathlib import Path
import re
import os
import time
import random
import sys
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError, APIConnectionError

load_dotenv(".env")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.tools import lookup_order, create_ticket
from src.rag import retrieve_policy

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

MODEL = "gemini-3.8-flash"


def ask_gemini(messages):
    for attempt in range(4):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except APIStatusError as e:
            if e.status_code == 429:
                raise RuntimeError(
                    "Gemini API quota exhausted. Please wait for quota reset; "
                    "no further retries were attempted."
                ) from e

            if e.status_code not in (500, 502, 503, 504) or attempt == 3:
                raise

        except APIConnectionError:
            if attempt == 3:
                raise

        wait = 2 ** attempt + random.random()
        print(f"\nTemporary API error. Retrying in {wait:.1f}s...")
        time.sleep(wait)


def respond_to_text(question, history=None):
    """Get a text response using the existing RAG + Gemini agent."""
    if history is None:
        history = [
            {
                "role": "system",
                "content": (
                    "You are ZentroMart customer support. Be polite and concise. "
                    "Never invent order information or policies. Use provided "
                    "knowledge-base context for policy questions. If the knowledge "
                    "base does not answer a question, say you don't know."
                ),
            }
        ]
    chunks = retrieve_policy(question, top_k=10)
    if chunks:
        history.append({
            "role": "system",
            "content": "Relevant policy context:\n" + "\n\n".join(chunks),
        })
    history.append({"role": "user", "content": question})
    answer = ask_gemini(history)
    history.append({"role": "assistant", "content": answer})
    return answer, history


def run_agent():
    print("ZentroMart Support (type 'exit' to stop)")
    history = [
        {
            "role": "system",
            "content": (
                "You are ZentroMart customer support. Be polite and concise. "
                "Never invent order information or policies. Use provided "
                "knowledge-base context for policy questions. For order lookup, "
                "ask for the order ID and verification value. Never reveal order "
                "details until lookup_order confirms verified=True. Allow at most "
                "one verification retry. Only say a support ticket was created "
                "when create_ticket returns created=True."
            ),
        }
    ]

    verification_attempts = {}

    while True:
        question = input("\nCustomer: ").strip()
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue

        # Retrieve policy context for this turn.
        chunks = retrieve_policy(question, top_k=10)
        if chunks:
            history.append({
                "role": "system",
                "content": "Relevant policy context:\n" + "\n\n".join(chunks),
            })

        # Explicit order lookup flow; do not let the LLM bypass verification.
        if "order" in question.lower() and any(
            word in question.lower()
            for word in ["track", "status", "where", "details", "lookup"]
        ):
            order_id = input("Order ID: ").strip()
            proof = input("Phone last 4 digits OR delivery pincode: ").strip()

            result = lookup_order(order_id, proof)
            if result.get("verified") is True:
                print("\nZentroMart Support: Order verified. Here are the order details:")
                safe_result = {
                    key: value for key, value in result.items()
                    if key not in {"phone", "delivery_pincode"}
                }
                print({
                    key: result.get(key)
                    for key in ["order_id", "status", "placed_at", "estimated_delivery"]
                    if result.get(key) is not None
                })
            else:
                attempts = verification_attempts.get(order_id, 0)
                if attempts < 1:
                    verification_attempts[order_id] = attempts + 1
                    print("\nVerification failed. You may try once more.")
                else:
                    print("\nVerification failed. Please contact support for help.")
            continue

        # Escalation requests create a ticket only if the tool confirms success.
        if any(word in question.lower() for word in ["human", "agent", "complaint", "escalate"]):
            summary = (
                f"Customer issue: {question}. Checks made: knowledge base reviewed. "
                "Escalation reason: customer requested human support."
            )
            result = create_ticket(
                summary=summary,
                reason="Human support requested",
                intent="escalation",
            )
            if result.get("created") is True:
                print(f"\nZentroMart Support: I've created a support ticket ({result['ticket_id']}).")
            else:
                print("\nZentroMart Support: I couldn't create the ticket. I'll need to escalate this manually.")
            continue

        history.append({"role": "user", "content": question})
        answer = ask_gemini(history)
        history.append({"role": "assistant", "content": answer})
        print("\nZentroMart Support:", answer)


if __name__ == "__main__":
    run_agent()