"""Small public-source adapters for portfolio-relevant market evidence."""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from html.parser import HTMLParser
from typing import Any, Mapping
from urllib.parse import urlencode, urljoin
from urllib.request import Request, urlopen

from runtime.logging import utc_now_iso


SINA_BREADTH_URL = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData"
PBOC_NEWS_URL = "https://www.pbc.gov.cn/goutongjiaoliu/113456/113469/index.html"
SSE_ANNOUNCEMENT_URL = "https://query.sse.com.cn/security/stock/queryCompanyBulletin.do"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AtlasOS/1.0"


def fetch_public_market_evidence(positions: list[Mapping[str, Any]], *, timeout: float = 8.0) -> dict[str, Any]:
    """Fetch bounded public evidence and preserve per-channel failure truth."""

    items: list[dict[str, Any]] = []
    errors: dict[str, str] = {}
    statuses = {
        "market_breadth": "NOT_CONFIGURED",
        "news_announcement": "NOT_CONFIGURED",
        "macro_policy": "NOT_CONFIGURED",
    }
    try:
        breadth = fetch_market_breadth_sample(timeout=timeout)
        items.append(breadth)
        statuses["market_breadth"] = str(breadth.get("channel_status") or "DELAYED")
    except Exception as exc:
        statuses["market_breadth"] = "FAILED"
        errors["market_breadth"] = _error(exc)
    try:
        policy = fetch_pbo_c_policy(limit=3, timeout=timeout)
        items.extend(policy)
        statuses["macro_policy"] = _items_status(policy)
    except Exception as exc:
        statuses["macro_policy"] = "FAILED"
        errors["macro_policy"] = _error(exc)
    try:
        announcements = fetch_sse_announcements(positions, limit_per_asset=3, timeout=timeout)
        items.extend(announcements)
        statuses["news_announcement"] = _items_status(announcements) if announcements else "NOT_CONFIGURED"
    except Exception as exc:
        statuses["news_announcement"] = "FAILED"
        errors["news_announcement"] = _error(exc)
    return {
        "timestamp": utc_now_iso(),
        "items": items,
        "channel_statuses": statuses,
        "errors": errors,
        "read_only": True,
        "no_trading_execution": True,
    }


def fetch_market_breadth_sample(*, timeout: float = 8.0) -> dict[str, Any]:
    params = {
        "page": 1,
        "num": 100,
        "sort": "symbol",
        "asc": 1,
        "node": "hs_a",
        "symbol": "",
        "_s_r_a": "page",
    }
    rows = _get_json(SINA_BREADTH_URL + "?" + urlencode(params), timeout=timeout)
    if not isinstance(rows, list) or not rows:
        raise ValueError("empty_breadth_sample")
    changes = [_number(item.get("changepercent")) for item in rows if isinstance(item, Mapping)]
    advancing = sum(1 for value in changes if value > 0)
    declining = sum(1 for value in changes if value < 0)
    unchanged = len(changes) - advancing - declining
    ratio = round(advancing / max(1, advancing + declining), 4)
    return _evidence_item(
        channel="market_breadth",
        source="sina_market_center",
        source_url=SINA_BREADTH_URL,
        published_at=utc_now_iso(),
        freshness="DELAYED",
        source_type="public_market_snapshot",
        classification="LIVE_OBSERVATION_SAMPLE",
        verification_status="VERIFIED_SOURCE_PARTIAL_COVERAGE",
        headline=f"A-share breadth sample: {advancing} advancing, {declining} declining, {unchanged} unchanged",
        affected_assets=[],
        affected_themes=["A-share market breadth"],
        world_model_node="Market Participation",
        details={
            "sample_size": len(changes),
            "advancing": advancing,
            "declining": declining,
            "unchanged": unchanged,
            "advance_ratio": ratio,
            "coverage": "first_100_sina_hs_a_symbols",
        },
        channel_status="DELAYED",
    )


def fetch_pbo_c_policy(*, limit: int = 3, timeout: float = 8.0) -> list[dict[str, Any]]:
    parser = _PBOCListParser()
    parser.feed(_get_text(PBOC_NEWS_URL, timeout=timeout))
    results = []
    for row in parser.items[: max(1, limit)]:
        results.append(
            _evidence_item(
                channel="macro_policy",
                source="pbo_c_official",
                source_url=urljoin(PBOC_NEWS_URL, row["href"]),
                published_at=row["date"],
                freshness=_date_freshness(row["date"]),
                source_type="official_policy_release",
                classification="VERIFIED_EVIDENCE",
                verification_status="VERIFIED_OFFICIAL_SOURCE",
                headline=row["title"],
                affected_assets=[],
                affected_themes=["Macro Policy"],
                world_model_node="Macro Liquidity",
            )
        )
    if not results:
        raise ValueError("no_policy_items")
    return results


def fetch_sse_announcements(
    positions: list[Mapping[str, Any]],
    *,
    limit_per_asset: int = 3,
    timeout: float = 8.0,
) -> list[dict[str, Any]]:
    output = []
    for position in positions:
        asset = str(position.get("asset") or "")
        market = str(position.get("market") or "").lower()
        code = asset.split(".")[0]
        if not code.isdigit() or not (asset.upper().endswith(".SH") or "a-share" in market and code.startswith("6")):
            continue
        params = {
            "isPagination": "true",
            "productId": code,
            "keyWord": "",
            "securityType": "0101,120100,020100,020200,120200",
            "reportType2": "DQGG",
            "reportType": "ALL",
            "pageHelp.pageSize": max(1, limit_per_asset),
            "pageHelp.pageNo": 1,
            "pageHelp.beginPage": 1,
            "pageHelp.endPage": 1,
        }
        payload = _get_json(
            SSE_ANNOUNCEMENT_URL + "?" + urlencode(params),
            timeout=timeout,
            headers={"Referer": "https://www.sse.com.cn/"},
        )
        page = payload.get("pageHelp", {}) if isinstance(payload, Mapping) else {}
        rows = page.get("data", []) if isinstance(page, Mapping) else []
        for row in rows[:limit_per_asset]:
            if not isinstance(row, Mapping):
                continue
            date = str(row.get("SSEDATE") or row.get("ADDDATE") or "")[:10]
            output.append(
                _evidence_item(
                    channel="news_announcement",
                    source="sse_official",
                    source_url=urljoin("https://www.sse.com.cn", str(row.get("URL") or "")),
                    published_at=date,
                    freshness=_date_freshness(date),
                    source_type="official_company_announcement",
                    classification="VERIFIED_EVIDENCE",
                    verification_status="VERIFIED_OFFICIAL_SOURCE",
                    headline=str(row.get("TITLE") or "Company announcement")[:300],
                    affected_assets=[asset],
                    affected_themes=[str(position.get("theme") or "Unspecified")],
                    world_model_node="Company Evidence",
                )
            )
    return output


def _evidence_item(**values: Any) -> dict[str, Any]:
    identity = "|".join(str(values[key]) for key in ("source", "channel", "published_at", "headline"))
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    return {
        "evidence_id": f"{values['source']}:{values['channel']}:{digest}",
        "channel": values["channel"],
        "source": values["source"],
        "source_url": values["source_url"],
        "timestamp": values["published_at"],
        "freshness": values["freshness"],
        "source_type": values["source_type"],
        "classification": values["classification"],
        "verification_status": values["verification_status"],
        "headline": values["headline"],
        "affected_assets": values.get("affected_assets", []),
        "affected_themes": values.get("affected_themes", []),
        "world_model_node": values.get("world_model_node", "Unknown"),
        "thesis_changed": "UNASSESSED",
        "details": values.get("details", {}),
        "channel_status": values.get("channel_status", values["freshness"]),
    }


def _get_json(url: str, *, timeout: float, headers: Mapping[str, str] | None = None) -> Any:
    return json.loads(_get_text(url, timeout=timeout, headers=headers))


def _get_text(url: str, *, timeout: float, headers: Mapping[str, str] | None = None) -> str:
    request_headers = {"User-Agent": USER_AGENT, "Accept": "application/json,text/html;q=0.9,*/*;q=0.8"}
    request_headers.update(dict(headers or {}))
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=timeout) as response:
        raw = response.read()
        encoding = response.headers.get_content_charset() or "utf-8"
    return raw.decode(encoding, errors="replace")


def _items_status(items: list[Mapping[str, Any]]) -> str:
    freshness = {str(item.get("freshness") or "").upper() for item in items}
    if "LIVE" in freshness:
        return "LIVE"
    if "DELAYED" in freshness:
        return "DELAYED"
    if "CACHED" in freshness:
        return "CACHED"
    return "NOT_CONFIGURED"


def _date_freshness(value: str) -> str:
    try:
        published = datetime.fromisoformat(value[:10]).replace(tzinfo=timezone.utc)
    except (TypeError, ValueError):
        return "CACHED"
    age_days = max(0, (datetime.now(timezone.utc) - published).days)
    if age_days <= 1:
        return "LIVE"
    if age_days <= 7:
        return "DELAYED"
    return "CACHED"


def _number(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _error(exc: Exception) -> str:
    return f"{type(exc).__name__}: {exc}"[:240]


class _PBOCListParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.items: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None
        self._in_anchor = False
        self._in_date = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "a" and "/goutongjiaoliu/113456/113469/20" in str(attributes.get("href") or ""):
            self._current = {"href": str(attributes.get("href") or ""), "title": "", "date": ""}
            self._in_anchor = True
        elif tag == "span" and self._current is not None and "hui12" in str(attributes.get("class") or ""):
            self._in_date = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "a":
            self._in_anchor = False
        elif tag == "span" and self._in_date:
            self._in_date = False
            if self._current and self._current["title"] and self._current["date"]:
                self.items.append(self._current)
            self._current = None

    def handle_data(self, data: str) -> None:
        if self._current is None:
            return
        text = " ".join(data.split())
        if not text:
            return
        if self._in_anchor:
            self._current["title"] = (self._current["title"] + " " + text).strip()
        elif self._in_date and len(text) >= 10:
            self._current["date"] = text[:10]
