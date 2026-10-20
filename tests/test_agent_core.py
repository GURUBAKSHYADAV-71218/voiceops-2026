import unittest
from unittest.mock import patch

from src.agent_core import respond_to_text


class AgentCoreTests(unittest.TestCase):

    def test_order_requires_verification(self):
        history = None

        answer, history = respond_to_text("Track my order", history)
        self.assertIn("order ID", answer)

        answer, history = respond_to_text("123456", history)
        self.assertIn("verify", answer.lower())

        with patch(
            "src.agent_core.lookup_order",
            return_value={
                "verified": True,
                "order_id": "123456",
                "status": "Shipped",
                "estimated_delivery": "2026-10-23",
                "items": [],
            },
        ) as lookup:
            answer, history = respond_to_text("1234", history)

        lookup.assert_called_once_with("123456", "1234")
        self.assertIn("Order verified", answer)
        self.assertIn("Shipped", answer)

    def test_failed_verification_allows_only_one_retry(self):
        history = None
        _, history = respond_to_text("Track my order", history)
        _, history = respond_to_text("123456", history)

        with patch(
            "src.agent_core.lookup_order",
            return_value={"verified": False},
        ):
            answer, history = respond_to_text("0000", history)
            self.assertIn("once more", answer)

            answer, history = respond_to_text("0000", history)
            self.assertIn("failed again", answer.lower())

    def test_ticket_confirmation_requires_tool_success(self):
        with patch(
            "src.agent_core.create_ticket",
            return_value={"created": False},
        ):
            answer, _ = respond_to_text("I want a human support agent")
            self.assertNotIn("I've created a support ticket", answer)

        with patch(
            "src.agent_core.create_ticket",
            return_value={"created": True, "ticket_id": "TKT-TEST"},
        ):
            answer, _ = respond_to_text("I want a human support agent")
            self.assertIn("TKT-TEST", answer)

    def test_policy_question_uses_rag(self):
        with patch(
            "src.agent_core.retrieve_policy",
            return_value=["[RET-1] Return policy evidence"],
        ) as retrieval, patch(
            "src.agent_core.ask_gemini",
            return_value="The policy allows eligible returns.",
        ):
            answer, _ = respond_to_text("What is the return policy?")

        retrieval.assert_called_once()
        self.assertIn("eligible returns", answer)


if __name__ == "__main__":
    unittest.main(verbosity=2)
