"""J.A.R.V.I.S. v143.0 safe voice daily briefing shell."""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V143_0_VOICE_DAILY_BRIEFING_SHELL_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V143_0_VOICE_DAILY_BRIEFING_SHELL_REVIEW_REQUIRED_SAFE"

FORBIDDEN_VOICE_PHRASES: tuple[str, ...] = (
    "buy now",
    "sell now",
    "place order",
    "execute trade",
    "liquidate",
    "connect broker",
    "log in",
    "auto rebalance",
)


@dataclass(frozen=True)
class VoiceBriefingResult:
    status: str
    current_date: str
    voice_briefing_ready: bool
    text: str
    audio_requested: bool
    audio_rendered: bool
    tts_available: bool
    tts_backend: str
    tts_warning: str | None
    no_speech_commands_added: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    broker_connection_enabled: bool
    credentials_required: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LocalTTSPlaybackResult:
    audio_requested: bool
    audio_rendered: bool
    tts_available: bool
    tts_backend: str
    warning: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _eur_words(value: Any) -> str:
    try:
        amount = float(value or 0.0)
    except Exception:
        amount = 0.0
    if amount.is_integer():
        return f"{int(amount)} euros"
    return f"{amount:.2f} euros"


def _safe_status(value: Any) -> bool:
    return bool(value)


def _build_text(product: Mapping[str, Any]) -> str:
    week = product.get("week_plan") or {}
    data = product.get("data_readiness") or {}
    live_news = product.get("live_news_context") or {}
    ready = bool(product.get("dashboard_ready"))
    ready_text = "ready for manual use" if ready else "needs review before manual use"
    market_ready = "ready" if data.get("data_readiness_ready") else "needs review"
    news_text = "News is optional context."
    if live_news.get("usable_count"):
        news_text = f"News has {int(live_news.get('usable_count') or 0)} optional headline items."
    return (
        f"Good evening, Diogo. J.A.R.V.I.S. is {ready_text}. "
        f"Today's manual plan is emergency {_eur_words(week.get('emergency_top_up_eur'))}, "
        f"crypto {_eur_words(week.get('crypto_eur'))}, "
        f"ETF/fund {_eur_words(week.get('etf_fund_eur'))}, "
        f"and stock {_eur_words(week.get('individual_stock_eur'))}. "
        f"Market data is {market_ready}. {news_text} "
        "Manual-only safety is active: no broker, no credentials, no orders, no trades, and no auto-approval. "
        "Ready when you are."
    )


def _forbidden_phrases_absent(text: str) -> tuple[bool, list[str]]:
    lowered = text.lower()
    found = [phrase for phrase in FORBIDDEN_VOICE_PHRASES if phrase in lowered]
    return not found, found


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def speak_text_locally(text: str, *, timeout_seconds: int = 30) -> LocalTTSPlaybackResult:
    """Play generated briefing text through a local OS TTS backend when available."""

    if os.environ.get("JARVIS_DISABLE_TTS") == "1":
        return LocalTTSPlaybackResult(
            audio_requested=True,
            audio_rendered=False,
            tts_available=False,
            tts_backend="disabled",
            warning="local TTS is disabled by JARVIS_DISABLE_TTS; showing text only",
        )

    if platform.system().lower() != "windows":
        return LocalTTSPlaybackResult(
            audio_requested=True,
            audio_rendered=False,
            tts_available=False,
            tts_backend="text_only",
            warning="local Windows TTS is unavailable on this platform; showing text only",
        )

    script = """
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $text = [Console]::In.ReadToEnd()
    if ([string]::IsNullOrWhiteSpace($text)) { exit 2 }
    $synth.Speak($text)
} finally {
    $synth.Dispose()
}
""".strip()

    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            input=text,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
    except (FileNotFoundError, subprocess.SubprocessError, OSError) as exc:
        return LocalTTSPlaybackResult(
            audio_requested=True,
            audio_rendered=False,
            tts_available=False,
            tts_backend="windows_sapi",
            warning=f"local TTS playback was unavailable: {exc}",
        )

    if completed.returncode == 0:
        return LocalTTSPlaybackResult(
            audio_requested=True,
            audio_rendered=True,
            tts_available=True,
            tts_backend="windows_sapi",
            warning=None,
        )

    detail = (completed.stderr or completed.stdout or f"exit code {completed.returncode}").strip()
    return LocalTTSPlaybackResult(
        audio_requested=True,
        audio_rendered=False,
        tts_available=False,
        tts_backend="windows_sapi",
        warning=f"local TTS playback failed safely: {detail}",
    )


def build_voice_briefing_result(
    *,
    current_date: str = "2026-06-20",
    audio_requested: bool = False,
    play_audio: bool = False,
    product_api_result: Any | None = None,
) -> VoiceBriefingResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "voice briefing is text-first and read-only",
        "audio rendering is disabled by default; missing local TTS is a warning, not a blocker",
        "speech-to-text commands are not added by this shell",
    ]
    product = _plain(product_api_result or build_product_api_result(current_date=current_date))
    text = _build_text(product)
    safe_text, forbidden_found = _forbidden_phrases_absent(text)
    safety_ready = _safety_check_ready()

    if not safe_text:
        blockers.append("voice_briefing_contains_forbidden_execution_phrase")
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")
    if product.get("blockers"):
        warnings.append("product API has review notes; briefing remains manual-use text only")

    tts_available = False
    audio_rendered = False
    tts_backend = "text_only"
    tts_warning: str | None = None
    if audio_requested and play_audio:
        playback = speak_text_locally(text)
        tts_available = playback.tts_available
        audio_rendered = playback.audio_rendered
        tts_backend = playback.tts_backend
        tts_warning = playback.warning
        if playback.warning:
            warnings.append(playback.warning)
    elif audio_requested:
        warnings.append("audio was requested, but playback was not enabled; use --voice-briefing-speak for local TTS")

    blockers = _dedupe(blockers)
    ready = not blockers
    return VoiceBriefingResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        voice_briefing_ready=ready,
        text=text,
        audio_requested=audio_requested,
        audio_rendered=audio_rendered,
        tts_available=tts_available,
        tts_backend=tts_backend,
        tts_warning=tts_warning,
        no_speech_commands_added=True,
        safety_check_blocks_execution=safety_ready,
        manual_only=True,
        broker_connection_enabled=False,
        credentials_required=False,
        order_created=False,
        trade_created=False,
        auto_approval_enabled=False,
        blockers=blockers,
        warnings=_dedupe(warnings),
        proof={
            "forbidden_phrases_found": forbidden_found,
            "dashboard_ready": product.get("dashboard_ready"),
            "data_ready": (product.get("data_readiness") or {}).get("data_readiness_ready"),
            "headline_count": (product.get("live_news_context") or {}).get("usable_count"),
            "safety_blocked": safety_ready,
            "tts_backend": tts_backend,
            "tts_warning": tts_warning,
        },
    )


def format_voice_briefing(result: VoiceBriefingResult, *, text_only: bool = False) -> str:
    if text_only:
        return result.text
    lines = [
        "J.A.R.V.I.S. VOICE DAILY BRIEFING SHELL",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"voice briefing ready: {result.voice_briefing_ready}",
        f"audio requested: {result.audio_requested}",
        f"audio rendered: {result.audio_rendered}",
        f"tts available: {result.tts_available}",
        f"tts backend: {result.tts_backend}",
        f"tts warning: {result.tts_warning or 'none'}",
        "",
        "BRIEFING TEXT:",
        result.text,
        "",
        "SAFETY ASSERTIONS:",
        f"- no speech commands added: {result.no_speech_commands_added}",
        f"- safety check blocks execution: {result.safety_check_blocks_execution}",
        f"- manual_only: {result.manual_only}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- order_created: {result.order_created}",
        f"- trade_created: {result.trade_created}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. safe voice briefing shell.")
    parser.add_argument("--voice-briefing", action="store_true")
    parser.add_argument("--voice-briefing-text", action="store_true")
    parser.add_argument("--voice-briefing-speak", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    args = parser.parse_args(argv)

    result = build_voice_briefing_result(
        current_date=args.current_date,
        audio_requested=bool((args.voice_briefing or args.voice_briefing_speak) and not args.voice_briefing_text),
        play_audio=bool(args.voice_briefing_speak and not args.voice_briefing_text),
    )
    print(format_voice_briefing(result, text_only=bool(args.voice_briefing_text)))
    return 0 if result.voice_briefing_ready else 1


__all__ = [
    "FORBIDDEN_VOICE_PHRASES",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "LocalTTSPlaybackResult",
    "VoiceBriefingResult",
    "build_voice_briefing_result",
    "format_voice_briefing",
    "speak_text_locally",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
