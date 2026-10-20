from pathlib import Path
import argparse
import json

from src.agent_core import respond_to_text
from src.rag import retrieve_policy
from src.voice import transcribe_audio, synthesize_reply


def main():
    parser = argparse.ArgumentParser(
        description="Process customer audio files with the ZentroMart support agent."
    )
    parser.add_argument("--input", default="practice/audio")
    parser.add_argument("--output", default="outputs/voice")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not input_dir.is_dir():
        raise SystemExit(f"Input folder not found: {input_dir.resolve()}")

    supported = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}
    audio_files = sorted(
        p for p in input_dir.iterdir()
        if p.is_file() and p.suffix.lower() in supported
    )

    if not audio_files:
        raise SystemExit(f"No supported audio files found in {input_dir.resolve()}")

    successes = 0
    history = None

    for audio_path in audio_files:
        item_dir = output_dir / audio_path.stem
        item_dir.mkdir(parents=True, exist_ok=True)

        result = {
            "audio_file": audio_path.name,
            "transcript": "",
            "reply": "",
            "retrieved_sources": [],
            "status": "failed",
            "error": None,
        }

        print(f"\nProcessing: {audio_path.name}")

        try:
            transcript = transcribe_audio(str(audio_path))
            if not transcript:
                raise ValueError("Speech transcription was empty.")

            result["transcript"] = transcript
            (item_dir / "transcript.txt").write_text(
                transcript, encoding="utf-8"
            )

            chunks = retrieve_policy(transcript, top_k=10)
            result["retrieved_sources"] = chunks
            (item_dir / "retrieved_sources.txt").write_text(
                "\n\n--- SOURCE CHUNK ---\n\n".join(chunks),
                encoding="utf-8",
            )

            # Preserve conversation context across ordered audio turns.
            reply, history = respond_to_text(transcript, history)

            result["reply"] = reply
            (item_dir / "reply.txt").write_text(reply, encoding="utf-8")

            synthesize_reply(reply, str(item_dir / "reply.wav"))

            result["status"] = "success"
            successes += 1
            print(f"SUCCESS: outputs saved to {item_dir}")

        except Exception as exc:
            result["error"] = f"{type(exc).__name__}: {exc}"
            print(f"FAILED: {audio_path.name}: {result['error']}")

        finally:
            (item_dir / "result.json").write_text(
                json.dumps(result, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    print(f"\nFinished: {successes}/{len(audio_files)} audio files completed.")
    print(f"Results: {output_dir.resolve()}")


if __name__ == "__main__":
    main()
