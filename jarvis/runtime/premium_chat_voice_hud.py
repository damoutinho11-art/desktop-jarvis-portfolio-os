"""J.A.R.V.I.S. v165.0 premium chat and voice HUD polish."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass

from jarvis.runtime.premium_orbital_design_system import render_shell, render_status_badge

STATUS_READY = "JARVIS_V165_0_CHAT_VOICE_HUD_POLISH_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V165_0_CHAT_VOICE_HUD_POLISH_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_CHAT_VOICE_HUD"


@dataclass(frozen=True)
class ChatVoiceHudPolishResult:
    status: str
    final_verdict: str
    chat_voice_hud_ready: bool
    premium_design_system_present: bool
    jarvis_orb_present: bool
    voice_controls_present: bool
    quick_commands_present: bool
    manual_only_language_present: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection_enabled: bool
    credentials_required: bool
    account_login_enabled: bool
    private_account_ingestion_enabled: bool
    buy_sell_request_created: bool
    order_ticket_created: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    approval_mutation: bool
    allocation_mutation: bool
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def render_chat_voice_hud_page() -> str:
    extra_css = """
<style>
.chat-grid { display:grid; grid-template-columns:minmax(0,1.1fr) minmax(340px,.9fr); gap:16px; align-items:start; }
.chat-hero { grid-column:1 / -1; min-height:250px; }
.hero-row { display:flex; justify-content:space-between; align-items:center; gap:22px; }
.hero-copy { display:grid; gap:12px; max-width:780px; }
.chat-title { margin:0; font-size:clamp(34px,6vw,76px); line-height:.92; letter-spacing:0; }
.muted { color:var(--jarvis-muted); line-height:1.55; }
.safety { border:1px solid rgba(120,242,168,.32); border-radius:var(--radius-md); padding:14px 16px; background:rgba(22,72,51,.22); color:#ddffea; font-weight:780; }
.badges { display:flex; flex-wrap:wrap; gap:8px; margin-top:4px; }
.badge { border:1px solid rgba(125,218,255,.22); background:rgba(7,17,31,.68); color:var(--jarvis-text); border-radius:999px; padding:7px 10px; font-size:12px; font-weight:850; }
.badge.safe { border-color:rgba(120,242,168,.35); color:var(--jarvis-green); background:rgba(40,210,142,.10); }
.jarvis-orb { position:relative; width:132px; height:132px; flex:0 0 auto; border-radius:999px; background:radial-gradient(circle at 38% 32%, #f8fbff 0 7%, #55dfff 10% 26%, #2d7dff 42%, #07111f 72%); box-shadow:0 0 54px rgba(85,223,255,.42), inset 0 0 30px rgba(255,255,255,.18); overflow:hidden; animation:orbPulse 3.6s ease-in-out infinite; }
.jarvis-orb::before, .jarvis-orb::after { content:""; position:absolute; inset:12px; border-radius:inherit; border:1px solid rgba(238,248,255,.32); animation:orbRing 2.6s ease-in-out infinite; }
.jarvis-orb::after { inset:28px; border-color:rgba(255,191,92,.46); animation-delay:.55s; }
.orb-core { position:absolute; inset:48px; border-radius:999px; background:#f8fbff; box-shadow:0 0 22px rgba(255,255,255,.9); }
.orb-status { position:absolute; left:50%; bottom:17px; width:48px; height:5px; transform:translateX(-50%); border-radius:999px; background:rgba(248,251,255,.68); }
.jarvis-orb.state-idle { filter:saturate(1.08); }
.jarvis-orb.state-listening { animation-duration:1.8s; box-shadow:0 0 66px rgba(48,231,189,.56), inset 0 0 28px rgba(255,255,255,.2); }
.jarvis-orb.state-thinking { animation-duration:1.2s; background:radial-gradient(circle at 38% 32%, #f8fbff 0 7%, #ffbf5c 10% 24%, #55dfff 42%, #07111f 72%); }
.jarvis-orb.state-speaking { animation-duration:.78s; box-shadow:0 0 70px rgba(255,191,92,.58), inset 0 0 28px rgba(255,255,255,.2); }
.command-pane, .reply-pane { display:grid; gap:14px; }
.preset-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(190px,1fr)); gap:10px; }
.preset { min-height:48px; border:1px solid rgba(125,218,255,.20); background:rgba(5,13,25,.72); color:var(--jarvis-text); border-radius:var(--radius-sm); padding:11px 12px; font-weight:850; cursor:pointer; text-align:left; transition:transform var(--motion-fast) var(--motion-ease), border-color var(--motion-fast), background var(--motion-fast); }
.preset:hover, .preset:focus { border-color:rgba(85,223,255,.66); background:rgba(85,223,255,.10); outline:none; transform:translateY(-2px); }
textarea { width:100%; min-height:132px; border-radius:var(--radius-sm); border:1px solid rgba(125,218,255,.22); background:rgba(3,7,17,.78); color:var(--jarvis-text); padding:14px; font-size:16px; box-sizing:border-box; line-height:1.45; resize:vertical; }
.actions, .voice-actions { display:flex; flex-wrap:wrap; align-items:center; gap:10px; }
.primary, .voice-button, .dashboard-link { min-height:42px; border-radius:var(--radius-sm); padding:10px 13px; font-weight:900; cursor:pointer; text-decoration:none; transition:transform var(--motion-fast) var(--motion-ease), border-color var(--motion-fast), background var(--motion-fast); }
.primary { border:0; background:linear-gradient(135deg,var(--jarvis-cyan),var(--jarvis-teal)); color:#02111c; box-shadow:0 0 24px rgba(85,223,255,.24); }
.voice-button, .dashboard-link { border:1px solid rgba(125,218,255,.28); background:rgba(7,17,31,.74); color:var(--jarvis-text); }
.primary:hover, .voice-button:hover, .voice-button:focus, .dashboard-link:hover, .dashboard-link:focus { transform:translateY(-1px); border-color:rgba(85,223,255,.68); outline:none; }
.voice-status { min-height:22px; color:var(--jarvis-muted); font-size:14px; line-height:1.45; }
button:disabled { opacity:.55; cursor:not-allowed; transform:none; }
.reply-card { border:1px solid rgba(125,218,255,.18); border-radius:var(--radius-md); background:rgba(3,7,17,.66); padding:16px; min-height:220px; box-shadow:inset 0 1px 0 rgba(255,255,255,.05); }
.reply-head { display:flex; justify-content:space-between; gap:12px; margin-bottom:10px; color:var(--jarvis-muted); font-weight:900; }
.loading { color:var(--jarvis-amber); visibility:hidden; }
.loading.active { visibility:visible; }
pre { white-space:pre-wrap; margin:0; font-family:var(--font-mono); line-height:1.55; color:var(--jarvis-text); }
.links { display:flex; flex-wrap:wrap; gap:12px; margin:0; }
.links a { color:var(--jarvis-cyan); font-weight:800; text-decoration:none; }
.links a:hover, .links a:focus { color:var(--jarvis-text); outline:none; }
@keyframes orbPulse { 0%, 100% { transform:scale(1); } 50% { transform:scale(1.045); } }
@keyframes orbRing { 0% { opacity:.18; transform:scale(.86); } 50% { opacity:.82; transform:scale(1.04); } 100% { opacity:.18; transform:scale(.86); } }
@media (max-width:920px) { .chat-grid { grid-template-columns:1fr; } .hero-row { align-items:flex-start; } }
@media (max-width:640px) { .hero-row { flex-direction:column; } .jarvis-orb { width:92px; height:92px; } .orb-core { inset:33px; } .orb-status { bottom:12px; } }
</style>
"""
    body = f"""
<main class="chat-grid">
  <section class="hud-hero chat-hero">
    <div class="hero-row">
      <div class="hero-copy">
        {render_status_badge("Ready for Manual Use", "ready")}
        <h1 class="chat-title">J.A.R.V.I.S. Local Chat</h1>
        <p class="muted">Ask about today's manual plan, portfolio health, universe search, instruments, safety, blockers, or what changed since last time.</p>
        <div class="safety">Read-only and manual-only. No broker, credentials, orders, trades, account login, private account sync, or auto-approval path is enabled.</div>
        <div class="badges" aria-label="Safety and status badges">
          <span class="badge safe">manual-only</span>
          <span class="badge safe">read-only</span>
          <span class="badge safe">no broker</span>
          <span class="badge safe">no credentials</span>
          <span class="badge safe">no orders</span>
          <span class="badge safe">no trades</span>
          <span class="badge safe">no auto-approval</span>
        </div>
      </div>
      <div id="jarvisOrb" class="jarvis-orb state-idle" data-state="idle" aria-label="J.A.R.V.I.S. voice state">
        <span class="orb-core"></span>
        <span class="orb-status"></span>
      </div>
    </div>
  </section>

  <section class="glass-panel command-pane">
    <h2>Quick Commands</h2>
    <div class="preset-grid" aria-label="Preset questions">
      <button class="preset" type="button" data-question="What is my plan today?">What is my plan today?</button>
      <button class="preset" type="button" data-question="What happened today?">What happened today?</button>
      <button class="preset" type="button" data-question="What changed since last time?">What changed since last time?</button>
      <button class="preset" type="button" data-question="Why these instruments?">Why these instruments?</button>
      <button class="preset" type="button" data-question="Can I trust this data?">Can I trust this data?</button>
      <button class="preset" type="button" data-question="What news matters to my portfolio?">What news matters?</button>
      <button class="preset" type="button" data-question="Is this safe?">Is this safe?</button>
      <button class="preset" type="button" data-question="What are the blockers?">What are the blockers?</button>
      <button class="preset" type="button" data-question="Show portfolio health report card.">Portfolio Health</button>
      <button class="preset" type="button" data-question="Use Universe Explorer to find European accumulating global ETFs.">Universe Explorer</button>
      <button class="preset" type="button" data-action="dashboard">Open dashboard</button>
    </div>
    <textarea id="question">What is my plan today?</textarea>
    <div class="actions">
      <button id="askButton" class="primary" type="button">Ask J.A.R.V.I.S.</button>
      <a class="dashboard-link" href="/dashboard">Open dashboard</a>
      <a class="dashboard-link" href="/orbit">Open Orbit</a>
    </div>
    <div class="voice-actions" aria-label="Voice controls">
      <button id="voiceDraftButton" class="voice-button" type="button">Voice input</button>
      <button id="readBriefingButton" class="voice-button" type="button">Read briefing aloud</button>
      <button id="speakReplyButton" class="voice-button" type="button">Speak reply</button>
      <button id="stopVoiceButton" class="voice-button" type="button">Stop voice</button>
    </div>
    <div id="audioStatus" class="voice-status" role="status">Voice is output-only until you press Ask manually.</div>
  </section>

  <section class="glass-panel reply-pane">
    <div class="reply-card" aria-live="polite">
      <div class="reply-head">
        <span>Evidence Summary</span>
        <span id="loadingState" class="loading">Loading...</span>
      </div>
      <pre id="reply">Ready.</pre>
    </div>
    <p class="links">
      <a href="/dashboard">Dashboard</a>
      <a href="/chat">Chat</a>
      <a href="/briefing">Briefing</a>
      <a href="/memory">Memory</a>
      <a href="/safety">Safety</a>
      <a href="/instruments">Instruments</a>
    </p>
  </section>
</main>
<script>
  const question = document.getElementById("question");
  const reply = document.getElementById("reply");
  const button = document.getElementById("askButton");
  const loading = document.getElementById("loadingState");
  const audioStatus = document.getElementById("audioStatus");
  const readBriefingButton = document.getElementById("readBriefingButton");
  const speakReplyButton = document.getElementById("speakReplyButton");
  const stopVoiceButton = document.getElementById("stopVoiceButton");
  const voiceDraftButton = document.getElementById("voiceDraftButton");
  const jarvisOrb = document.getElementById("jarvisOrb");
  const canSpeak = "speechSynthesis" in window && "SpeechSynthesisUtterance" in window;
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  let recognition = null;

  function setAudioStatus(message) {{
    audioStatus.textContent = message;
  }}

  function setOrbState(state) {{
    const allowed = ["idle", "listening", "thinking", "speaking"];
    const nextState = allowed.includes(state) ? state : "idle";
    jarvisOrb.dataset.state = nextState;
    jarvisOrb.className = "jarvis-orb state-" + nextState;
  }}

  function speakText(text) {{
    if (!canSpeak) {{
      setAudioStatus("Audio unavailable in this browser. Text remains available.");
      setOrbState("idle");
      return;
    }}
    const cleanText = (text || "").trim();
    if (!cleanText) {{
      setAudioStatus("Nothing to read yet.");
      setOrbState("idle");
      return;
    }}
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.onstart = () => {{
      setAudioStatus("Speaking...");
      setOrbState("speaking");
    }};
    utterance.onend = () => {{
      setAudioStatus("Voice ready.");
      setOrbState("idle");
    }};
    utterance.onerror = () => {{
      setAudioStatus("Audio unavailable. Text remains available.");
      setOrbState("idle");
    }};
    window.speechSynthesis.speak(utterance);
  }}

  function stopVoice() {{
    if (canSpeak) {{
      window.speechSynthesis.cancel();
    }}
    if (recognition) {{
      recognition.stop();
    }}
    setOrbState("idle");
    setAudioStatus("Voice stopped.");
  }}

  async function readBriefingAloud() {{
    setOrbState("thinking");
    try {{
      const response = await fetch("/api/voice-briefing");
      const payload = await response.json();
      const briefing = payload.text || "";
      reply.textContent = briefing || "Briefing text unavailable.";
      speakText(briefing);
    }} catch (error) {{
      setAudioStatus("Audio unavailable. Briefing text could not be loaded.");
      setOrbState("idle");
    }}
  }}

  function startVoiceDraft() {{
    if (!SpeechRecognition) {{
      setAudioStatus("Microphone input unavailable in this browser.");
      return;
    }}
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";
    recognition.onstart = () => {{
      setAudioStatus("Listening...");
      setOrbState("listening");
    }};
    recognition.onresult = (event) => {{
      const transcript = event.results && event.results[0] && event.results[0][0]
        ? event.results[0][0].transcript
        : "";
      question.value = transcript;
      setAudioStatus("Voice draft ready. Press Ask J.A.R.V.I.S. manually.");
      setOrbState("idle");
    }};
    recognition.onerror = () => {{
      setAudioStatus("Microphone input unavailable in this browser.");
      setOrbState("idle");
    }};
    recognition.onend = () => {{
      recognition = null;
      if (jarvisOrb.dataset.state === "listening") {{
        setOrbState("idle");
      }}
    }};
    recognition.start();
  }}

  async function askJarvis() {{
    button.disabled = true;
    loading.classList.add("active");
    reply.textContent = "Loading reply...";
    setOrbState("thinking");
    try {{
      const response = await fetch("/api/chat", {{
        method: "POST",
        headers: {{"Content-Type": "application/json"}},
        body: JSON.stringify({{query: question.value}})
      }});
      const payload = await response.json();
      reply.textContent = payload.reply || payload.response || JSON.stringify(payload, null, 2);
    }} catch (error) {{
      reply.textContent = "Local chat error: " + error;
    }} finally {{
      button.disabled = false;
      loading.classList.remove("active");
      if (jarvisOrb.dataset.state === "thinking") {{
        setOrbState("idle");
      }}
    }}
  }}

  button.addEventListener("click", askJarvis);
  readBriefingButton.addEventListener("click", readBriefingAloud);
  speakReplyButton.addEventListener("click", () => speakText(reply.textContent));
  stopVoiceButton.addEventListener("click", stopVoice);
  voiceDraftButton.addEventListener("click", startVoiceDraft);
  document.querySelectorAll(".preset").forEach((preset) => {{
    preset.addEventListener("click", () => {{
      if (preset.dataset.action === "dashboard") {{
        window.location.href = "/dashboard";
        return;
      }}
      question.value = preset.dataset.question || preset.textContent;
      askJarvis();
    }});
  }});
</script>
"""
    return render_shell(
        title="J.A.R.V.I.S. Local Chat",
        active="chat",
        body=body,
        extra_head=extra_css,
    )


def build_chat_voice_hud_polish_result(*, rendered_html: str | None = None) -> ChatVoiceHudPolishResult:
    html = rendered_html if rendered_html is not None else render_chat_voice_hud_page()
    blockers: list[str] = []

    premium_design = all(marker in html for marker in ("jarvis-shell", "hud-hero", "glass-panel", "status-badge"))
    if not premium_design:
        blockers.append("premium_design_system_not_present")

    orb_present = all(
        marker in html
        for marker in ("jarvis-orb", "state-idle", "state-listening", "state-thinking", "state-speaking", "@keyframes orbPulse")
    )
    if not orb_present:
        blockers.append("jarvis_orb_not_present")

    voice_controls = all(
        marker in html
        for marker in ("Voice input", "Read briefing aloud", "Speak reply", "Stop voice", "Audio unavailable", "Press Ask J.A.R.V.I.S. manually")
    )
    if not voice_controls:
        blockers.append("voice_controls_not_present")

    quick_commands = all(marker in html for marker in ("Portfolio Health", "Universe Explorer", "What changed since last time?"))
    if not quick_commands:
        blockers.append("quick_commands_not_present")

    safe_language = all(
        marker in html.lower()
        for marker in ("manual-only", "read-only", "no broker", "no credentials", "no orders", "no trades", "no auto-approval")
    )
    if not safe_language:
        blockers.append("manual_only_language_not_present")

    return ChatVoiceHudPolishResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if not blockers else "REVIEW_REQUIRED_FOR_PREMIUM_CHAT_VOICE_HUD",
        chat_voice_hud_ready=not blockers,
        premium_design_system_present=premium_design,
        jarvis_orb_present=orb_present,
        voice_controls_present=voice_controls,
        quick_commands_present=quick_commands,
        manual_only_language_present=safe_language,
        manual_only=True,
        execution_forbidden=True,
        broker_connection_enabled=False,
        credentials_required=False,
        account_login_enabled=False,
        private_account_ingestion_enabled=False,
        buy_sell_request_created=False,
        order_ticket_created=False,
        order_created=False,
        trade_created=False,
        auto_approval_enabled=False,
        approval_mutation=False,
        allocation_mutation=False,
        blockers=blockers,
        warnings=[
            "chat and voice HUD polish is local, manual-only, and does not add broker, credential, account, order, trade, approval, or allocation paths",
            "voice input only drafts text and still requires pressing Ask J.A.R.V.I.S. manually",
        ],
    )


def format_chat_voice_hud_polish(result: ChatVoiceHudPolishResult) -> str:
    return "\n".join(
        [
            result.status,
            f"final_verdict: {result.final_verdict}",
            f"chat_voice_hud_ready: {result.chat_voice_hud_ready}",
            f"premium_design_system_present: {result.premium_design_system_present}",
            f"jarvis_orb_present: {result.jarvis_orb_present}",
            f"voice_controls_present: {result.voice_controls_present}",
            f"quick_commands_present: {result.quick_commands_present}",
            f"manual_only_language_present: {result.manual_only_language_present}",
            "manual_only: True",
            "execution_forbidden: True",
            "broker_connection_enabled: False",
            "credentials_required: False",
            "account_login_enabled: False",
            "private_account_ingestion_enabled: False",
            "buy_sell_request_created: False",
            "order_ticket_created: False",
            "order_created: False",
            "trade_created: False",
            "auto_approval_enabled: False",
            "approval_mutation: False",
            "allocation_mutation: False",
            "blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or validate the premium J.A.R.V.I.S. chat and voice HUD.")
    parser.add_argument("--chat-voice-hud-polish", action="store_true")
    parser.add_argument("--html", action="store_true")
    args, _ = parser.parse_known_args(argv)

    if args.html:
        print(render_chat_voice_hud_page())
        return 0

    result = build_chat_voice_hud_polish_result()
    print(format_chat_voice_hud_polish(result))
    return 0 if result.chat_voice_hud_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "ChatVoiceHudPolishResult",
    "build_chat_voice_hud_polish_result",
    "format_chat_voice_hud_polish",
    "render_chat_voice_hud_page",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
