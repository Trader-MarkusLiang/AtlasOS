"""Market-derived source plans and per-asset source status."""

from __future__ import annotations

from typing import Any, Mapping
from urllib.parse import quote


SOURCE_CATALOG: dict[str, dict[str, Any]] = {
    "eastmoney_kline": {
        "label": "Eastmoney market database",
        "channel": "price_volume",
        "reliability": "PUBLIC_MARKET_DATABASE",
        "automated": True,
        "url": "https://quote.eastmoney.com/",
    },
    "tencent_kline": {
        "label": "Tencent market database",
        "channel": "price_volume",
        "reliability": "PUBLIC_MARKET_DATABASE",
        "automated": True,
        "url": "https://web.ifzq.gtimg.cn/appstock/app/fqkline/get",
    },
    "eastmoney_quote": {
        "label": "Eastmoney realtime quote fallback",
        "channel": "price_volume",
        "reliability": "PUBLIC_MARKET_DATABASE",
        "automated": True,
        "url": "https://quote.eastmoney.com/",
    },
    "tencent_quote": {
        "label": "Tencent realtime quote fallback",
        "channel": "price_volume",
        "reliability": "PUBLIC_MARKET_DATABASE",
        "automated": True,
        "url": "https://qt.gtimg.cn/",
    },
    "akshare": {
        "label": "AKShare public-data adapter",
        "channel": "price_volume",
        "reliability": "PUBLIC_DATA_ADAPTER",
        "automated": True,
        "url": "https://akshare.akfamily.xyz/",
    },
    "yfinance": {
        "label": "Yahoo Finance adapter",
        "channel": "price_volume",
        "reliability": "PUBLIC_MARKET_DATABASE",
        "automated": True,
        "url": "https://finance.yahoo.com/",
    },
    "yahoo_chart": {
        "label": "Yahoo Finance chart API",
        "channel": "price_volume",
        "reliability": "PUBLIC_MARKET_DATABASE",
        "automated": True,
        "url": "https://finance.yahoo.com/",
    },
    "sse_official": {
        "label": "Shanghai Stock Exchange disclosures",
        "channel": "company_disclosure",
        "reliability": "OFFICIAL_EXCHANGE",
        "automated": True,
        "url": "https://www.sse.com.cn/disclosure/listedinfo/announcement/",
    },
    "cninfo_official_disclosure": {
        "label": "CNInfo official disclosures",
        "channel": "company_disclosure",
        "reliability": "OFFICIAL_DISCLOSURE_PLATFORM",
        "automated": True,
        "url": "https://www.cninfo.com.cn/new/index",
    },
    "eastmoney_stock_rank": {
        "label": "Eastmoney public attention rank",
        "channel": "public_attention",
        "reliability": "PUBLIC_ATTENTION_PROXY",
        "automated": True,
        "url": "https://emappdata.eastmoney.com/stockrank/getAllCurrentList",
    },
    "hkex_issuer_search": {
        "label": "HKEXnews listed-company search",
        "channel": "company_disclosure",
        "reliability": "OFFICIAL_EXCHANGE",
        "automated": False,
        "url": "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en",
    },
    "sec_edgar": {
        "label": "SEC EDGAR company filings",
        "channel": "company_disclosure",
        "reliability": "OFFICIAL_REGULATOR",
        "automated": False,
        "url": "https://www.sec.gov/edgar/search/",
    },
}


MARKET_SOURCE_PLANS = {
    "SH": ["eastmoney_kline", "tencent_kline", "akshare", "yfinance", "yahoo_chart", "eastmoney_quote", "tencent_quote", "sse_official", "eastmoney_stock_rank"],
    "SZ": ["eastmoney_kline", "tencent_kline", "akshare", "yfinance", "yahoo_chart", "eastmoney_quote", "tencent_quote", "cninfo_official_disclosure", "eastmoney_stock_rank"],
    "HK": ["eastmoney_kline", "tencent_kline", "akshare", "yfinance", "yahoo_chart", "eastmoney_quote", "tencent_quote", "hkex_issuer_search"],
    "US": ["yahoo_chart", "yfinance", "sec_edgar"],
}


def source_plan_for_asset(asset: str, market: str) -> list[dict[str, Any]]:
    """Return the fixed public-source plan derived from market identity."""

    market_key = _market_key(asset, market)
    return [
        {
            "source_id": source_id,
            **SOURCE_CATALOG[source_id],
            "url": _asset_url(source_id, asset, SOURCE_CATALOG[source_id]["url"]),
        }
        for source_id in MARKET_SOURCE_PLANS.get(market_key, [])
    ]


def build_asset_source_map(
    positions: list[Mapping[str, Any]],
    observations: list[Mapping[str, Any]],
    evidence_items: list[Mapping[str, Any]],
    source_errors: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Attach actual use and health to every configured asset's fixed source plan."""

    errors = source_errors if isinstance(source_errors, Mapping) else {}
    observation_by_asset = {
        str(item.get("asset") or ""): item
        for item in observations
        if isinstance(item, Mapping) and item.get("asset")
    }
    global_evidence_sources = {
        str(item.get("source") or "")
        for item in evidence_items
        if isinstance(item, Mapping)
    }
    output = []
    for position in positions:
        asset = str(position.get("asset") or "")
        market = str(position.get("market") or "")
        observation = observation_by_asset.get(asset, {})
        asset_evidence = [
            item
            for item in evidence_items
            if isinstance(item, Mapping) and asset in item.get("affected_assets", [])
        ]
        sources = []
        for source in source_plan_for_asset(asset, market):
            source_id = str(source["source_id"])
            used_observation = source_id == str(observation.get("source") or "")
            matched_evidence = [item for item in asset_evidence if item.get("source") == source_id]
            checked_globally = source_id in global_evidence_sources
            error = _source_error(source_id, errors, observation)
            status = _source_status(
                source,
                used_observation=used_observation,
                matched_evidence=matched_evidence,
                checked_globally=checked_globally,
                error=error,
            )
            latest = observation.get("timestamp") if used_observation else _latest_timestamp(matched_evidence)
            freshness = observation.get("freshness") if used_observation else _freshest(matched_evidence)
            sources.append(
                {
                    **source,
                    "status": status,
                    "latest_timestamp": latest,
                    "freshness": freshness,
                    "record_count": 1 if used_observation else len(matched_evidence),
                    "error": error,
                }
            )
        output.append(
            {
                "asset": asset,
                "market": market,
                "sources": sources,
                "summary": {
                    "used": sum(item["status"] == "USED" for item in sources),
                    "standby": sum(item["status"] == "STANDBY" for item in sources),
                    "checked_no_record": sum(item["status"] in {"CHECKED_NO_RECENT_RECORD", "CHECKED_NOT_IN_SAMPLE"} for item in sources),
                    "failed": sum(item["status"] == "FAILED" for item in sources),
                    "manual_review": sum(item["status"] == "MANUAL_REVIEW" for item in sources),
                },
            }
        )
    return output


def _source_status(
    source: Mapping[str, Any],
    *,
    used_observation: bool,
    matched_evidence: list[Mapping[str, Any]],
    checked_globally: bool,
    error: str,
) -> str:
    if error:
        return "FAILED"
    if used_observation or matched_evidence:
        return "USED"
    if not source.get("automated"):
        return "MANUAL_REVIEW"
    if checked_globally and source.get("channel") == "public_attention":
        return "CHECKED_NOT_IN_SAMPLE"
    if source.get("channel") == "company_disclosure":
        return "CHECKED_NO_RECENT_RECORD"
    return "STANDBY"


def _source_error(source_id: str, errors: Mapping[str, Any], observation: Mapping[str, Any]) -> str:
    aliases = {
        "sse_official": "sse_announcements",
        "cninfo_official_disclosure": "cninfo_announcements",
        "eastmoney_stock_rank": "narrative_attention",
    }
    direct = errors.get(source_id) or errors.get(aliases.get(source_id, ""))
    if direct:
        return str(direct)
    for error in observation.get("raw_reference", {}).get("errors", []) if isinstance(observation, Mapping) else []:
        if str(error).startswith(source_id + ":"):
            return str(error)[:240]
    return ""


def _market_key(asset: str, market: str) -> str:
    upper_asset = asset.upper()
    lower_market = market.lower()
    if upper_asset.endswith(".SH"):
        return "SH"
    if upper_asset.endswith(".SZ"):
        return "SZ"
    if upper_asset.endswith(".HK") or "hk" in lower_market:
        return "HK"
    if "a-share" in lower_market:
        code = asset.split(".")[0]
        return "SH" if code.startswith(("5", "6", "9")) else "SZ"
    if "us" in lower_market or "etf" in lower_market:
        return "US"
    return ""


def _asset_url(source_id: str, asset: str, default: str) -> str:
    code = asset.split(".")[0]
    if source_id == "hkex_issuer_search":
        return f"https://www1.hkexnews.hk/search/prefix.do?lang=EN&type=A&name={quote(code)}&market=SEHK"
    if source_id == "sec_edgar":
        return f"https://www.sec.gov/edgar/search/#/q={quote(code)}"
    return default


def _latest_timestamp(items: list[Mapping[str, Any]]) -> Any:
    values = [str(item.get("timestamp") or "") for item in items if item.get("timestamp")]
    return max(values) if values else None


def _freshest(items: list[Mapping[str, Any]]) -> Any:
    order = {"LIVE": 3, "DELAYED": 2, "CACHED": 1}
    values = [str(item.get("freshness") or "").upper() for item in items]
    return max(values, key=lambda value: order.get(value, 0)) if values else None
