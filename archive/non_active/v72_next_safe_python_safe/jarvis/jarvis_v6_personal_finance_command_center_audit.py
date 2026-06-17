"""J.A.R.V.I.S. v6 personal finance command-center audit.

This audit bridges the sealed v5 research OS into the true v6 product vision:
a personal finance command center that can scan a broad investable universe,
recommend aggressive-but-bounded portfolio policies, and prepare manual buy
actions.

This module is report-only. It does not fetch, call APIs, connect to brokers,
approve assets, create buy requests, change policy, execute trades, or mutate
registries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V6_COMMAND_CENTER_FOUNDATION_READY_NEXT_POLICY_INTELLIGENCE"
STATUS_BLOCKED = "JARVIS_V6_COMMAND_CENTER_FOUNDATION_BLOCKED_SAFE"

CAPABILITY_READY = "CAPABILITY_READY"
CAPABILITY_PARTIAL = "CAPABILITY_PARTIAL"
CAPABILITY_MISSING = "CAPABILITY_MISSING"

CLASS_CORE = "CORE"
CLASS_SUPPORT = "SUPPORT"
CLASS_NEXT_BUILD = "NEXT_BUILD"
CLASS_SAFETY = "SAFETY"


@dataclass(frozen=True)
class JarvisV6CommandCenterCapability:
    capability_id: str
    name: str
    classification: str
    status: str
    existing_files: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    next_stage: str | None
    wired_to_current_system: bool
    safety_notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "name": self.name,
            "classification": self.classification,
            "status": self.status,
            "existing_files": list(self.existing_files),
            "missing_requirements": list(self.missing_requirements),
            "next_stage": self.next_stage,
            "wired_to_current_system": self.wired_to_current_system,
            "safety_notes": list(self.safety_notes),
        }


@dataclass(frozen=True)
class JarvisV6CommandCenterAuditResult:
    status: str
    release_anchor: str
    capability_count: int
    ready_count: int
    partial_count: int
    missing_count: int
    recommended_next_stage: str
    capabilities: tuple[JarvisV6CommandCenterCapability, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    broad_universe_scan_required: bool
    flexible_policy_bands_required: bool
    policy_intelligence_required: bool
    weekly_crypto_buy_allowed_if_within_risk_bands: bool
    manual_policy_approval_required: bool
    manual_buy_execution_only: bool
    automatic_policy_change_forbidden: bool
    automatic_approval_forbidden: bool
    broker_execution_forbidden: bool
    creates_buy_request: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "release_anchor": self.release_anchor,
            "capability_count": self.capability_count,
            "ready_count": self.ready_count,
            "partial_count": self.partial_count,
            "missing_count": self.missing_count,
            "recommended_next_stage": self.recommended_next_stage,
            "capabilities": [capability.to_dict() for capability in self.capabilities],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "broad_universe_scan_required": self.broad_universe_scan_required,
            "flexible_policy_bands_required": self.flexible_policy_bands_required,
            "policy_intelligence_required": self.policy_intelligence_required,
            "weekly_crypto_buy_allowed_if_within_risk_bands": (
                self.weekly_crypto_buy_allowed_if_within_risk_bands
            ),
            "manual_policy_approval_required": self.manual_policy_approval_required,
            "manual_buy_execution_only": self.manual_buy_execution_only,
            "automatic_policy_change_forbidden": self.automatic_policy_change_forbidden,
            "automatic_approval_forbidden": self.automatic_approval_forbidden,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "creates_buy_request": self.creates_buy_request,
            "no_trades_executed": self.no_trades_executed,
        }


def _repo_path(repo_root: str | Path, relative_path: str) -> Path:
    return Path(repo_root) / relative_path


def _present_files(repo_root: str | Path, relative_paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(path for path in relative_paths if _repo_path(repo_root, path).exists())


def _missing_files(repo_root: str | Path, relative_paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(path for path in relative_paths if not _repo_path(repo_root, path).exists())


def _capability(
    repo_root: str | Path,
    capability_id: str,
    name: str,
    classification: str,
    expected_files: tuple[str, ...],
    status_if_present: str,
    missing_requirements: tuple[str, ...],
    next_stage: str | None,
    wired_to_current_system: bool,
    safety_notes: tuple[str, ...],
) -> tuple[JarvisV6CommandCenterCapability, tuple[str, ...]]:
    missing_files = _missing_files(repo_root, expected_files)
    existing_files = _present_files(repo_root, expected_files)

    blockers: list[str] = []
    status = status_if_present
    if missing_files:
        status = CAPABILITY_MISSING
        blockers.extend(f"{capability_id}: expected file missing: {path}" for path in missing_files)

    return (
        JarvisV6CommandCenterCapability(
            capability_id=capability_id,
            name=name,
            classification=classification,
            status=status,
            existing_files=existing_files,
            missing_requirements=missing_requirements,
            next_stage=next_stage,
            wired_to_current_system=wired_to_current_system,
            safety_notes=safety_notes,
        ),
        tuple(blockers),
    )


def audit_jarvis_v6_personal_finance_command_center(
    repo_root: str | Path = ".",
) -> JarvisV6CommandCenterAuditResult:
    warnings: list[str] = []
    blockers: list[str] = []
    capabilities: list[JarvisV6CommandCenterCapability] = []

    capability_specs = (
        {
            "capability_id": "public_data_foundation",
            "name": "Public market-data and source-quality foundation",
            "classification": CLASS_CORE,
            "expected_files": (
                "jarvis/data/dynamic_public_source_candidates.template.json",
                "jarvis/dynamic_market_data_source_quality_gate.py",
                "jarvis/dynamic_public_source_transformer_readiness.py",
                "jarvis/dynamic_public_data_fetcher_adapter.py",
                "jarvis/dynamic_market_raw_cache_normalizer.py",
                "jarvis/dynamic_coingecko_market_chart_transformer.py",
                "jarvis/dynamic_market_data_intake_validator.py",
            ),
            "status_if_present": CAPABILITY_READY,
            "missing_requirements": (),
            "next_stage": None,
            "wired_to_current_system": True,
            "safety_notes": (
                "Public-source data remains quality-gated.",
                "Raw data remains unverified until operator review.",
                "No endpoint promotion is granted by this audit.",
            ),
        },
        {
            "capability_id": "private_portfolio_wing",
            "name": "Private portfolio snapshot and finance state",
            "classification": CLASS_CORE,
            "expected_files": (
                "jarvis/portfolio_schema.py",
                "jarvis/manual_snapshot_loader.py",
                "jarvis/portfolio_snapshot_engine.py",
                "jarvis/portfolio_drift.py",
                "jarvis/data/manual_snapshot.example.json",
            ),
            "status_if_present": CAPABILITY_PARTIAL,
            "missing_requirements": (
                "Private snapshot v2 with account roles, protected cash, platform routing, and investable cash.",
                "Explicit emergency-fund and contribution-cash separation.",
                "Operator-owned local snapshot path outside tracked fixtures.",
            ),
            "next_stage": "v6.2_private_portfolio_snapshot_v2",
            "wired_to_current_system": True,
            "safety_notes": (
                "Private data should remain local/operator-owned.",
                "Private snapshot ingestion must not imply approval or execution.",
            ),
        },
        {
            "capability_id": "policy_intelligence",
            "name": "Aggressive-but-bounded policy intelligence",
            "classification": CLASS_NEXT_BUILD,
            "expected_files": (
                "jarvis/portfolio_policy.py",
                "jarvis/dynamic_allocation_optimizer.py",
            ),
            "status_if_present": CAPABILITY_MISSING,
            "missing_requirements": (
                "Candidate policy generator.",
                "Policy scorecard with risk bands, crypto permissions, ETF/fund/stock/crypto sleeves.",
                "Manual policy-change ticket before any policy becomes active.",
                "Flexible allocation bands instead of strict fixed targets.",
            ),
            "next_stage": "v6.1_policy_intelligence_boundary",
            "wired_to_current_system": False,
            "safety_notes": (
                "J.A.R.V.I.S. may recommend policy changes but must not apply them silently.",
                "Policy changes require manual operator approval.",
            ),
        },
        {
            "capability_id": "universal_asset_scan",
            "name": "Universal ETF/fund/stock/crypto candidate scanning",
            "classification": CLASS_NEXT_BUILD,
            "expected_files": (
                "jarvis/jarvis_public_asset_universe_discovery_plan.py",
                "jarvis/jarvis_public_asset_universe_classifier.py",
                "jarvis/data/dynamic_public_source_candidates.template.json",
            ),
            "status_if_present": CAPABILITY_PARTIAL,
            "missing_requirements": (
                "Unified investable candidate registry across ETF, fund, stock, crypto, cash-like, bond, and commodity sleeves.",
                "Asset eligibility states: DISCOVERED, DATA_READY, QUALITY_READY, POLICY_CANDIDATE, APPROVED_POLICY_ASSET, WEEKLY_BUY_CANDIDATE, BLOCKED, AVOID.",
                "Platform availability and currency-fit scoring.",
            ),
            "next_stage": "v6.3_universal_asset_candidate_registry",
            "wired_to_current_system": False,
            "safety_notes": (
                "Broad universe scans must still pass source, identity, freshness, risk, and manual-review gates.",
                "Unverified assets must not be recommended for buying.",
            ),
        },
        {
            "capability_id": "manual_weekly_buy_planner",
            "name": "Weekly/day-by-day manual buy planner",
            "classification": CLASS_CORE,
            "expected_files": (
                "jarvis/dynamic_allocation_weekly_plan.py",
                "jarvis/dynamic_allocation_weekly_plan_report.py",
                "jarvis/contribution_planner.py",
            ),
            "status_if_present": CAPABILITY_PARTIAL,
            "missing_requirements": (
                "Manual buy ticket with asset, amount, platform, reason, counterargument, risk warning, and approval status.",
                "Explicit WAIT/HOLD/AVOID/RESEARCH_MORE outputs.",
                "Weekly crypto buy permission bounded by risk bands and portfolio state.",
            ),
            "next_stage": "v6.6_manual_buy_ticket_planner",
            "wired_to_current_system": True,
            "safety_notes": (
                "Buy tickets are instructions for Diogo to review manually, not broker orders.",
                "The system must never create a broker buy request.",
            ),
        },
        {
            "capability_id": "news_risk_context",
            "name": "News and risk context layer",
            "classification": CLASS_NEXT_BUILD,
            "expected_files": (
                "jarvis/evidence_freshness_policy.py",
                "jarvis/evidence_provenance.py",
            ),
            "status_if_present": CAPABILITY_MISSING,
            "missing_requirements": (
                "News-source credibility ranking.",
                "Portfolio-impact tagging.",
                "Risk regime summary.",
                "Daily/weekly brief that informs but does not override policy automatically.",
            ),
            "next_stage": "v6.7_news_risk_context_layer",
            "wired_to_current_system": False,
            "safety_notes": (
                "News can modify risk context but must not trigger automatic buying/selling.",
            ),
        },
        {
            "capability_id": "professional_dashboard",
            "name": "Professional portfolio command-center dashboard",
            "classification": CLASS_SUPPORT,
            "expected_files": (
                "jarvis/dynamic_operator_status_dashboard.py",
                "jarvis/dynamic_command_center_audit.py",
            ),
            "status_if_present": CAPABILITY_PARTIAL,
            "missing_requirements": (
                "Portfolio allocation view.",
                "Policy recommendation panel.",
                "Manual buy ticket panel.",
                "Risk/news ticker.",
                "Decision history.",
                "Voice/chat status panel.",
            ),
            "next_stage": "v6.8_professional_dashboard",
            "wired_to_current_system": True,
            "safety_notes": (
                "Dashboard should display manual actions only.",
                "Dashboard must not contain broker execution controls.",
            ),
        },
        {
            "capability_id": "voice_conversational_layer",
            "name": "Conversational and voice J.A.R.V.I.S. layer",
            "classification": CLASS_SUPPORT,
            "expected_files": (
                "docs/JARVIS_DYNAMIC_PORTFOLIO_PREFLIGHT_RUNBOOK.md",
            ),
            "status_if_present": CAPABILITY_MISSING,
            "missing_requirements": (
                "Chat interface grounded in audited backend outputs.",
                "Voice brief and response layer.",
                "Session memory for decisions and summaries.",
                "No tool that can execute trades.",
            ),
            "next_stage": "v6.9_voice_conversational_layer",
            "wired_to_current_system": False,
            "safety_notes": (
                "Voice is an interface layer only.",
                "Voice must never bypass manual approval.",
            ),
        },
        {
            "capability_id": "execution_safety_boundary",
            "name": "Manual-only execution safety boundary",
            "classification": CLASS_SAFETY,
            "expected_files": (
                "jarvis/dynamic_command_center_audit.py",
                "jarvis/dynamic_operator_status_dashboard.py",
                "jarvis/jarvis_v5_final_research_os_mvp_audit.py",
            ),
            "status_if_present": CAPABILITY_READY,
            "missing_requirements": (),
            "next_stage": None,
            "wired_to_current_system": True,
            "safety_notes": (
                "No broker execution.",
                "No automatic approval.",
                "No buy request creation.",
                "No trades executed.",
                "Manual policy approval required.",
            ),
        },
    )

    for spec in capability_specs:
        capability, capability_blockers = _capability(repo_root, **spec)
        capabilities.append(capability)
        blockers.extend(capability_blockers)

    warnings.extend(
        (
            "v6 requires policy intelligence before broad autonomous recommendations.",
            "The current system should not be final-tagged until manual buy tickets and policy-change tickets exist.",
            "Flexible allocation bands should replace strict fixed-allocation behavior.",
            "Weekly crypto buying should be allowed only inside bounded risk, cash, and portfolio-state rules.",
            "The global ETF is a core sleeve, not the full ETF universe.",
        )
    )

    ready_count = sum(1 for capability in capabilities if capability.status == CAPABILITY_READY)
    partial_count = sum(1 for capability in capabilities if capability.status == CAPABILITY_PARTIAL)
    missing_count = sum(1 for capability in capabilities if capability.status == CAPABILITY_MISSING)

    safety_flags = {
        "manual_policy_approval_required": True,
        "manual_buy_execution_only": True,
        "automatic_policy_change_forbidden": True,
        "automatic_approval_forbidden": True,
        "broker_execution_forbidden": True,
        "creates_buy_request": False,
        "no_trades_executed": True,
    }

    if not all(
        (
            safety_flags["manual_policy_approval_required"],
            safety_flags["manual_buy_execution_only"],
            safety_flags["automatic_policy_change_forbidden"],
            safety_flags["automatic_approval_forbidden"],
            safety_flags["broker_execution_forbidden"],
            safety_flags["no_trades_executed"],
        )
    ):
        blockers.append("v6 command-center safety flags are not all enforced.")
    if safety_flags["creates_buy_request"]:
        blockers.append("v6 command-center audit must not create buy requests.")

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return JarvisV6CommandCenterAuditResult(
        status=status,
        release_anchor="v5.11-coingecko-raw-fixture-transformer-safe",
        capability_count=len(capabilities),
        ready_count=ready_count,
        partial_count=partial_count,
        missing_count=missing_count,
        recommended_next_stage="v6.1_policy_intelligence_boundary",
        capabilities=tuple(capabilities),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        broad_universe_scan_required=True,
        flexible_policy_bands_required=True,
        policy_intelligence_required=True,
        weekly_crypto_buy_allowed_if_within_risk_bands=True,
        **safety_flags,
    )
