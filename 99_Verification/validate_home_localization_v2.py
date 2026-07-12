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

    section_ids = [
        "home-portfolio-command",
        "home-current-holdings",
        "home-action-today",
        "home-material-changes",
        "home-reasoning-chain",
        "home-scenario-outlook",
        "home-action-playbook",
        "home-candidate-board",
        "home-forecast-accountability",
    ]
    checks = {
        "A_portfolio_first_chinese": _has_all(zh_visible, ["当前组合状态", "已配置暴露", "未部署资金"]),
        "B_action_status_localized": _has_any(zh_visible, ["需要条件确认", "暂不需要", "需要复核"]) and "CONDITIONAL" not in zh_visible,
        "C_reasoning_chain_chinese": _has_all(zh_visible, ["从信号到条件结论", "结构解释", "反方证据", "缺失证据"]),
        "D_scenarios_chinese": _has_all(zh_visible, ["四种可问责情景", "基准情景", "上行延续", "下行加速"]),
        "E_candidate_cde_separation": "只代表研究优先级，不代表 CDE 资本权限" in zh_visible,
        "F_forecast_accountability_chinese": "近期预测责任检查" in zh_visible,
        "G_evidence_truth_localized": _has_any(zh_visible, ["实时观测", "数据源观测", "尚未评估"]),
        "H_no_fake_multiday_zero": "5d 0.0%, 20d 0.0%" not in zh_visible,
        "I_runtime_terms_hidden": not _has_any(zh_visible, ["UNASSESSED", "Not created by runtime", "next review cycle"]),
        "J_supporting_context_collapsed": '<details class="supporting-context"' in zh_html,
        "K_english_mode_clean": _has_all(en_visible, ["Current Portfolio State", "Latest Evidence That Matters", "Four Accountable Scenarios"]),
        "L_zh_en_section_parity": all(section_id in zh_html and section_id in en_html for section_id in section_ids),
        "M_private_amount_not_rendered": "account_value" not in zh_full and "net_worth" not in zh_full,
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
    source = source.split('<details class="supporting-context"', 1)[0]
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
