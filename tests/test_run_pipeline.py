import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run


class VoicePipelineTests(unittest.TestCase):
    def test_multiple_audio_files_preserve_history_and_save_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_dir = root / "audio"
            output_dir = root / "output"
            input_dir.mkdir()

            (input_dir / "turn1.wav").write_bytes(b"fake audio 1")
            (input_dir / "turn2.wav").write_bytes(b"fake audio 2")

            seen_histories = []

            def fake_respond(text, history=None):
                seen_histories.append(history)
                updated = list(history or [])
                updated.append({"role": "user", "content": text})
                return f"Reply to {text}", updated

            def fake_tts(text, output_path):
                Path(output_path).write_bytes(b"fake wav")
                return output_path

            with patch.object(sys, "argv", [
                "run.py", "--input", str(input_dir),
                "--output", str(output_dir)
            ]), patch.object(
                run, "transcribe_audio",
                side_effect=["Hello", "And my order?"]
            ), patch.object(
                run, "retrieve_policy",
                return_value=["[TEST] policy evidence"]
            ), patch.object(
                run, "respond_to_text", side_effect=fake_respond
            ), patch.object(
                run, "synthesize_reply", side_effect=fake_tts
            ):
                run.main()

            self.assertEqual(len(seen_histories), 2)
            self.assertIsNone(seen_histories[0])
            self.assertIsNotNone(seen_histories[1])

            for name in ("turn1", "turn2"):
                folder = output_dir / name
                self.assertTrue((folder / "transcript.txt").exists())
                self.assertTrue((folder / "reply.txt").exists())
                self.assertTrue((folder / "reply.wav").exists())
                self.assertTrue((folder / "retrieved_sources.txt").exists())

                result = json.loads(
                    (folder / "result.json").read_text(encoding="utf-8")
                )
                self.assertEqual(result["status"], "success")

        print("PASS: Multi-file pipeline, history, and output artifacts verified.")


if __name__ == "__main__":
    unittest.main()
