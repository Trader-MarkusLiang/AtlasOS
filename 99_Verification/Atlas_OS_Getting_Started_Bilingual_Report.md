# Atlas OS Getting Started Bilingual Report

Date: 2026-07-09

## Scope

Validate EN/ZH parity for the Guided Start Center and navigation entries.

## Checks

| Check | Result |
| --- | --- |
| `nav.getting_started` exists in EN/ZH | PASS |
| `page.getting_started` exists in EN/ZH | PASS |
| `getting.*` key parity | PASS |
| Language switch via `/ui/language` | PASS |
| Primary page copy renders in zh after selection | PASS |
| User-facing setup states avoid raw `UNKNOWN` as primary text | PASS |

## Validator Evidence

`python3 99_Verification/validate_getting_started_center.py`

Result:

```json
{
  "status": "PASS",
  "i18n_keys": 107
}
```

## Bilingual Route Evidence

The isolated browser flow selected Chinese and reloaded `/getting-started`. The page then rendered:

- Sidebar entry: `开始使用`
- Hero kicker: `引导启动中心`
- Progress: `7 / 8 步已完成`
- Stop state: `已停止`

## Remaining Risk

Some existing non-Guided-Start pages still contain English product terms such as `Provider`, `Runtime`, or `Decision Brief`. The new Guided Start Center itself has EN/ZH primary text parity.
