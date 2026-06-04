"""Optional local voice adapter for J.A.R.V.I.S. Portfolio OS."""

from __future__ import annotations

import os


def speak(text: str) -> None:
    """Speak concise text with pyttsx3 if available, otherwise print it."""
    message = _concise_butler_text(text)
    if os.environ.get("JARVIS_VOICE_FORCE_FALLBACK") == "1":
        print(f"J.A.R.V.I.S. voice fallback: {message}")
        return

    try:
        import pyttsx3  # type: ignore
    except ImportError:
        print(f"J.A.R.V.I.S. voice fallback: {message}")
        return

    try:
        engine = pyttsx3.init()
        engine.say(message)
        engine.runAndWait()
    except Exception:
        print(f"J.A.R.V.I.S. voice fallback: {message}")


def _concise_butler_text(text: str) -> str:
    first_line = next((line.strip().rstrip(".") for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return "Weekly allocation review is ready. Manual approval required."
    if "No trades executed." in text:
        return text.strip()
    return f"{first_line}. Manual approval required. No trades executed."
