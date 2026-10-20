import os
from dotenv import load_dotenv
from openai import OpenAI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(ROOT, ".env"))

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

MODEL = "gemini-3.8-flash"


def ask_support(question: str) -> str:
    """Step 1 baseline: prompt-only, without retrieval or policy context."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are ZentroMart customer support. Be polite and concise. "
                    "Answer using only facts explicitly provided in the conversation. "
                    "Do not invent company policies, order details, or timelines. "
                    "If information is unavailable, clearly say you do not know."
                ),
            },
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content or ""


if __name__ == "__main__":
    question = input("Customer: ").strip()
    if question:
        print("\nZentroMart Support:", ask_support(question))
