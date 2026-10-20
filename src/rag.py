from pathlib import Path
import re

KB_DIR = Path(__file__).resolve().parent.parent / "kb"

# Each topic maps to the relevant knowledge-base documents.
TOPIC_RULES = [
    (
        [
            "return", "send it back", "send back", "doesn't fit",
            "does not fit", "not fit", "too small", "too large",
            "swimsuit", "swimwear", "briefs", "innerwear",
            "bedsheet", "exchange", "change of mind",
            "लौटाने", "वापस", "कितने दिन",
        ],
        ["pol_returns_v4.md"],
    ),
    (
        [
            "refund", "money back", "refund status",
            "refund not received", "rrn",
        ],
        ["pol_refunds.md"],
    ),
    (
        ["cash on delivery", "cod"],
        ["pol_payments_cod.md", "pol_refunds.md"],
    ),
    (
        [
            "damaged", "damage", "crack", "cracked", "broken",
            "wrong item", "missing item", "defective",
            "torn", "सामान", "collection",
        ],
        [
            "pol_damaged_wrong_missing.md",
            "agent_escalation_handoff.md",
            "faq_hindi.md",
        ],
    ),
    (
        [
            "never placed", "unauthorized", "account activity",
            "phone number", "other customer",
        ],
        ["agent_escalation_handoff.md"],
    ),
    (
        [
            "cancel", "cancellation", "already shipped",
            "on its way", "stop it", "shipped",
            "ऑर्डर शिप", "कैंसिल",
        ],
        ["pol_cancellations.md", "help_track_order.md", "faq_hindi.md"],
    ),
    (
        [
            "delivery", "late order", "shipping", "courier",
            "tracking", "track my order", "order status",
            "dubai", "international delivery", "deliver to",
            "express order", "arrived late", "late delivery", "compensation",
        ],
        ["help_track_order.md", "pol_delivery_shipping.md"],
    ),
    (
        [
            "warranty", "warranty claim", "assured",
            "claim kaise", "claim karein", "claim karna",
            "sku", "warranty period", "warranty coverage",
        ],
        ["pol_warranty_assured.md"],
    ),
    (
        [
            "charging", "battery", "troubleshooting",
            "phone won't turn on", "phone will not turn on",
            "bluetooth speaker", "wont turn on",
        ],
        ["help_troubleshooting_electronics.md"],
    ),
    (
        [
            "verification", "verify", "registered phone",
            "pincode", "order id", "order details",
        ],
        ["agent_identity_verification.md"],
    ),
    (
        ["track my order", "where is my order", "order status"],
        ["help_track_order.md"],
    ),
]


def choose_files(question: str) -> list[Path]:
    q = question.lower()
    selected = []

    for keywords, filenames in TOPIC_RULES:
        if any(keyword in q for keyword in keywords):
            selected.extend(filenames)

    # Remove duplicate filenames and ignore missing or superseded files.
    unique_names = list(dict.fromkeys(selected))

    return [
        KB_DIR / name
        for name in unique_names
        if (KB_DIR / name).is_file()
        and "superseded" not in name.lower()
    ]


def retrieve_policy(question: str, top_k: int = 10) -> list[str]:
    files = choose_files(question)

    if not files:
        return []

    q = question.lower()
    query_words = set(re.findall(r"\w+", q))
    chunks = []

    is_swimwear_question = (
        any(term in q for term in [
            "swimsuit", "swimwear", "briefs", "innerwear"
        ])
        and any(term in q for term in [
            "fit", "return", "send it back", "send back"
        ])
    )

    for path in files:
        text = path.read_text(encoding="utf-8")
        sections = re.split(r"(?=^## )", text, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()

            if not section:
                continue

            content = section.lower()
            content_words = set(re.findall(r"\w+", content))
            score = len(query_words & content_words)

            # Prioritize the exact swimwear/innerwear restriction.
            if (
                is_swimwear_question
                and path.name == "pol_returns_v4.md"
            ):
                mentions_category = any(term in content for term in [
                    "swimwear", "innerwear", "lingerie"
                ])
                mentions_restriction = any(term in content for term in [
                    "change of mind", "cannot be returned",
                    "not returnable", "cannot be returned for"
                ])

                if mentions_category and mentions_restriction:
                    score += 100

            # Prioritize explicit return-window sections for day-limit questions.
            if path.name == "pol_returns_v4.md":
                asks_days = any(term in q for term in [
                    "how many days", "return window",
                    "return period", "days to return"
                ])

                if asks_days and (
                    "return window" in content
                    or "days from delivery" in content
                    or "within " in content
                ):
                    score += 10

            if score > 0:
                chunks.append((score, path.name, section))

    # Highest-scoring, most relevant sections first.
    chunks.sort(key=lambda item: item[0], reverse=True)

    return [
        f"\n{section}"
        for _, filename, section in chunks[:top_k]
    ]


if __name__ == "__main__":
    question = input("Question: ").strip()
    results = retrieve_policy(question)

    if not results:
        print("No matching policy found.")
    else:
        for chunk in results:
            print("\n---\n" + chunk)