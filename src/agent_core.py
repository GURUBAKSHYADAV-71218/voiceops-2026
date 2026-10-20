import re
import json

from src.agent import ask_gemini
from src.rag import retrieve_policy
from tools.tools import lookup_order, create_ticket

STATE_PREFIX = "__AGENT_STATE__:"


def _get_state(history):
    for item in reversed(history):
        content = item.get("content", "")
        if item.get("role") == "system" and content.startswith(STATE_PREFIX):
            try:
                return json.loads(content[len(STATE_PREFIX):])
            except json.JSONDecodeError:
                break
    return {}


def _save_state(history, state):
    history[:] = [
        item for item in history
        if not (
            item.get("role") == "system"
            and item.get("content", "").startswith(STATE_PREFIX)
        )
    ]
    history.append({
        "role": "system",
        "content": STATE_PREFIX + json.dumps(state),
    })


def _order_id(text):
    # Order IDs in this synthetic dataset are numeric.
    matches = re.findall(r"(?<!\d)\d{6,}(?!\d)", text)
    return matches[-1] if matches else None


def respond_to_text(question, history=None):
    if history is None:
        history = [{
            "role": "system",
            "content": (
                "You are ZentroMart customer support. Be concise and polite. "
                "Use only supplied policy evidence. Never invent order details, "
                "refunds, timelines, or ticket confirmations. Say you do not know "
                "when the available evidence is insufficient."
            ),
        }]

    question = question.strip()
    if not question:
        return "Sorry, I didn't catch that. Could you repeat it?", history

    state = _get_state(history)
    history.append({"role": "user", "content": question})
    lower = question.lower()

    if state.get("stage") == "awaiting_order_id":
        oid = _order_id(question)
        if not oid:
            answer = "Please provide your numeric order ID so I can help track it."
        else:
            _save_state(history, {
                "stage": "awaiting_verification",
                "order_id": oid,
                "attempts": 0,
            })
            answer = (
                f"Please verify order {oid} using the registered phone's last "
                "4 digits or the delivery pincode."
            )
        history.append({"role": "assistant", "content": answer})
        return answer, history

    if state.get("stage") == "awaiting_verification":
        oid = state["order_id"]
        result = lookup_order(oid, question)

        if result.get("verified") is True:
            fields = [
                ("order ID", result.get("order_id")),
                ("status", result.get("status")),
                ("placed at", result.get("placed_at")),
                ("estimated delivery", result.get("estimated_delivery")),
            ]
            details = [f"{label}: {value}" for label, value in fields if value is not None]
            items = result.get("items", [])
            if items:
                names = [
                    str(item.get("product_name") or item.get("sku"))
                    for item in items
                    if item.get("product_name") or item.get("sku")
                ]
                if names:
                    details.append("items: " + ", ".join(names))
            answer = "Order verified. " + "; ".join(details)
            _save_state(history, {})
        elif state.get("attempts", 0) < 1:
            _save_state(history, {
                "stage": "awaiting_verification",
                "order_id": oid,
                "attempts": 1,
            })
            answer = (
                "I couldn't verify those details. Please try once more with "
                "the registered phone's last 4 digits or the delivery pincode."
            )
        else:
            _save_state(history, {})
            answer = (
                "Verification failed again, so I can't disclose the order details. "
                "Please ask for a human support agent if you need further help."
            )

        history.append({"role": "assistant", "content": answer})
        return answer, history

    if any(word in lower for word in (
        "human", "live agent", "speak to an agent", "complaint",
        "escalate", "supervisor"
    )):
        result = create_ticket(
            summary=(
                f"Customer issue: {question}. Checks made: customer requested "
                "human support. Escalation reason: handover requested."
            ),
            reason="Human support requested",
            intent="escalation",
        )
        if result.get("created") is True:
            answer = f"I've created a support ticket ({result['ticket_id']}). A human support team member can follow up."
        else:
            answer = "I couldn't create the support ticket automatically. Please try contacting support again."
        history.append({"role": "assistant", "content": answer})
        return answer, history

    if any(word in lower for word in (
        "track my order", "order status", "where is my order",
        "track order", "order details", "check my order"
    )):
        oid = _order_id(question)
        if oid:
            _save_state(history, {
                "stage": "awaiting_verification",
                "order_id": oid,
                "attempts": 0,
            })
            answer = (
                f"I can help check order {oid}. Please verify it using the "
                "registered phone's last 4 digits or the delivery pincode."
            )
        else:
            _save_state(history, {"stage": "awaiting_order_id"})
            answer = "I can help track that. What is your numeric order ID?"
        history.append({"role": "assistant", "content": answer})
        return answer, history

    chunks = retrieve_policy(question, top_k=10)
    if chunks:
        history.append({
            "role": "system",
            "content": "Relevant policy evidence:\n" + "\n\n".join(chunks),
        })

    # Hide internal state markers from the language model.
    messages = [
        item for item in history
        if not (
            item.get("role") == "system"
            and item.get("content", "").startswith(STATE_PREFIX)
        )
    ]
    answer = ask_gemini(messages)
    history.append({"role": "assistant", "content": answer})
    return answer, history
