from __future__ import annotations

import re


CANONICAL_ASSET_SYMBOLS = (
    "BTC",
    "ETH",
    "GLOBAL_CORE_ETF",
    "GROWTH_NASDAQ_ETF",
    "VWCE",
    "IS3Q.DE",
    "MSFT",
)

ASSET_ALIAS_MAP = {
    # Crypto
    "BTC": "BTC",
    "BITCOIN": "BTC",
    "ETH": "ETH",
    "ETHEREUM": "ETH",

    # Core/global ETF sleeve
    "GLOBAL_CORE_ETF": "GLOBAL_CORE_ETF",
    "GLOBAL CORE ETF": "GLOBAL_CORE_ETF",
    "CORE ETF": "GLOBAL_CORE_ETF",
    "EUNL": "GLOBAL_CORE_ETF",
    "EUNL.DE": "GLOBAL_CORE_ETF",
    "IWDA": "GLOBAL_CORE_ETF",

    # Growth/Nasdaq sleeve
    "GROWTH_NASDAQ_ETF": "GROWTH_NASDAQ_ETF",
    "GROWTH NASDAQ ETF": "GROWTH_NASDAQ_ETF",
    "GROWTH ETF": "GROWTH_NASDAQ_ETF",
    "NASDAQ ETF": "GROWTH_NASDAQ_ETF",
    "NASDAQ-100 ETF": "GROWTH_NASDAQ_ETF",
    "NASDAQ 100 ETF": "GROWTH_NASDAQ_ETF",
    "SXRV": "GROWTH_NASDAQ_ETF",
    "SXRV.DE": "GROWTH_NASDAQ_ETF",
    "CNDX": "GROWTH_NASDAQ_ETF",
    "EQAC": "GROWTH_NASDAQ_ETF",
    "XNAS": "GROWTH_NASDAQ_ETF",
    "XNAS.DE": "GROWTH_NASDAQ_ETF",

    # ETF/fund instruments
    "VWCE": "VWCE",
    "VWCE.DE": "VWCE",
    "IS3Q": "IS3Q.DE",
    "IS3Q.DE": "IS3Q.DE",
    "QUALITY ETF": "IS3Q.DE",
    "QUALITY FACTOR ETF": "IS3Q.DE",

    # Stock
    "MSFT": "MSFT",
    "MICROSOFT": "MSFT",
    "MICROSOFT STOCK": "MSFT",
}

ASSET_ALIAS_TERMS_LOWER = tuple(sorted((key.lower() for key in ASSET_ALIAS_MAP), key=len, reverse=True))


def _normalize_text(value: str) -> str:
    cleaned = str(value or "").upper()
    cleaned = cleaned.replace("?", " ").replace(",", " ").replace(":", " ").replace(";", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def normalize_asset_symbol_from_query(query: str) -> str | None:
    text = _normalize_text(query)
    if not text:
        return None

    compact = text.replace("-", " ")
    candidates = sorted(ASSET_ALIAS_MAP.items(), key=lambda item: len(item[0]), reverse=True)

    for alias, canonical in candidates:
        alias_clean = _normalize_text(alias)
        alias_compact = alias_clean.replace("-", " ")
        if alias_clean == text or alias_clean in text or alias_compact in compact:
            return canonical

    return None
