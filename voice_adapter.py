"""Optional local voice adapter for J.A.R.V.I.S. Portfolio OS v0."""

from __future__ import annotations


def speak(text: str) -> None:
    """Speak concise text with pyttsx3 if available, otherwise print it."""
    message = _concise_butler_text(text)
    try:
        import pyttsx3  # type: ignore
    except ImportError:
        print(f"J.A.R.V.I.S.: {message}")
        return

    engine = pyttsx3.init()
    engine.say(message)
    engine.runAndWait()


def _concise_butler_text(text: str) -> str:
    first_line = next((line.strip().rstrip(".") for line in text.splitlines() if line.strip()), "")
    if not first_line:
        return "Weekly allocation review is ready. Manual approval required."
    return f"{first_line}. Manual approval required. No trades executed."
