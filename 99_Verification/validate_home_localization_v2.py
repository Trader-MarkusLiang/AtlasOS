#!/usr/bin/env python3
"""Validate Atlas Home dynamic cognitive-output localization.

The validator checks the rendered Home route in both zh and en modes. It treats
closed expert details as source evidence, not primary UI, so raw DecisionPacket
English and ISO timestamps are allowed only inside that collapsed area.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


ARTIFACT_DIR = Path("99_Verification/artifacts/home_localization")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8765")
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    zh_html = _fetch_home(base_url, "zh")
    en_html = _fetch_home(base_url, "en")
    (ARTIFACT_DIR / "home_zh_validator.html").write_text(zh_html, encoding="utf-8")
    (ARTIFACT_DIR / "home_en_validator.html").write_text(en_html, encoding="utf-8")

    zh_visible = _visible_text_without_expert(zh_html)
    en_visible = _visible_text_without_expert(en_html)
    zh_full = html.unescape(zh_html)

    checks = {
        "A_chinese_hero": _has_any(zh_visible, ["当前主导状态", "流动性压力", "风险防御", "市场状态发生变化"]),
        "B_secondary_english_label": bool(re.search(r"<small>(Liquidity Stress|Risk-Off|Reduce|Neutral|Volatility Shock|Portfolio Relevance)</small>", zh_html)),
        "C_action_localized": _has_any(zh_visible, ["降低暴露", "观察", "保持", "逐步建立", "逐步增加", "中性观察"]),
        "D_causal_summary_chinese": _has_all(zh_visible, ["主要驱动", "组合影响", "不确定性"]),
        "E_right_inspector_chinese": _has_all(zh_visible, ["为什么会这样", "主要因果因素"]),
        "F_factor_badges_chinese": _has_any(zh_visible, ["流动性压力", "波动冲击", "组合相关性", "叙事压力", "市场注意力"]),
        "G_freshness_channels_chinese": _has_all(zh_visible, ["市场广度", "新闻与公告", "叙事与注意力", "宏观政策"]),
        "H_asset_descriptions_chinese": _has_all(zh_visible, ["价格、成交量、流动性与公告更新", "A股"]),
        "I_no_raw_iso_visible": not bool(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", zh_visible)),
        "J_raw_english_hidden_default": not _has_any(zh_visible, ["The fused runtime state", "RISK_OFF remains", "Because execution", "NOT_CONFIGURED"]),
        "K_expert_evidence_accessible": "<details class=\"expert-details\"" in zh_html and "last_decision_packet" in zh_full,
        "L_english_mode_clean": _has_any(en_visible, ["Current dominant state", "Primary driver", "Portfolio impact"]) and not _has_any(_strip_language_toggle(en_visible), ["当前主导状态", "主要驱动", "组合影响", "不确定性", "降低暴露"]),
        "M_zh_en_parity": _has_all(zh_visible, ["当前主导状态", "为什么会这样"]) and _has_all(en_visible, ["Current dominant state", "Why this happened"]),
    }
    passed = all(checks.values())
    result = {"status": "PASS" if passed else "FAIL", "checks": checks}
    (ARTIFACT_DIR / "home_localization_validator_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed else 1


def _fetch_home(base_url: str, language: str) -> str:
    payload = json.dumps({"language": language}).encode("utf-8")
    request = urllib.request.Request(
        base_url + "/ui/language",
        data=payload,
        headers={"content-type": "application/json"},
        method="POST",
    )
    urllib.request.urlopen(request, timeout=10).read()
    return urllib.request.urlopen(base_url + "/", timeout=15).read().decode("utf-8", errors="replace")


def _visible_text_without_expert(source: str) -> str:
    text = re.sub(r"<details class=\"expert-details\".*?</details>", " ", source, flags=re.S)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    return " ".join(text.split())


def _strip_language_toggle(text: str) -> str:
    return text.replace("中文", "").replace("语言", "")


def _has_any(text: str, needles: list[str]) -> bool:
    return any(needle in text for needle in needles)


def _has_all(text: str, needles: list[str]) -> bool:
    return all(needle in text for needle in needles)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, TimeoutError) as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        raise SystemExit(2)
