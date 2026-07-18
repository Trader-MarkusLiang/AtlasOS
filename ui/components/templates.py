"""Reusable HTML component templates for Atlas OS product pages.

Every function returns an HTML string fragment. These are pure presentation
helpers with zero cognition, portfolio, or trading semantics.
"""

from __future__ import annotations

from html import escape
from typing import Any, Mapping, Sequence


def page_shell(
    *,
    title: str = "Atlas OS",
    lang: str = "en",
    content: str = "",
    nav_links: Sequence[Mapping[str, str]] | None = None,
    extra_style: str = "",
    extra_script: str = "",
) -> str:
    """Return a full <!doctype html> page shell with nav, content, and footer.

    nav_links: [{"href": "/page", "label": "Page Name"}, ...]
    """
    nav_html = ""
    if nav_links:
        items = "".join(
            f'<a href="{escape(item.get("href", "#"))}">{escape(item.get("label", ""))}</a>'
            for item in nav_links
        )
        nav_html = f'<nav class="nav">{items}</nav>'
    return f"""<!doctype html>
<html lang="{escape(lang)}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<style>
:root {{ color-scheme:dark; --bg:#0b0f14; --panel:rgba(255,255,255,.065); --line:rgba(255,255,255,.12); --text:#eef2f7; --muted:#99a3b3; --accent:#7dd3fc; --warn:#f8d66d; --danger:#fb7185; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:linear-gradient(140deg,#0b0f14,#111827 52%,#080b10); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
a {{ color:var(--accent); text-decoration:none; }}
.shell {{ max-width:1180px; margin:0 auto; padding:28px 22px 44px; }}
.nav {{ display:flex; flex-wrap:wrap; gap:10px; margin-bottom:28px; }}
.nav a {{ padding:8px 12px; border:1px solid var(--line); border-radius:12px; background:rgba(255,255,255,.04); }}
.hero {{ min-height:260px; display:grid; align-content:center; gap:18px; padding:32px; border:1px solid var(--line); border-radius:22px; background:rgba(255,255,255,.07); }}
.hero-wide {{ min-height:200px; }}
.kicker {{ color:var(--muted); font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; }}
.card {{ min-height:120px; padding:18px; border:1px solid var(--line); border-radius:18px; background:var(--panel); }}
.card strong {{ display:block; margin-top:8px; font-size:1.2rem; }}
.grid-2 {{ display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:14px; }}
.grid-3 {{ display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:14px; }}
.grid-4 {{ display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:14px; }}
.wide {{ grid-column:span 2; }}
.pill {{ display:inline-block; padding:3px 10px; border-radius:999px; font-size:.75rem; font-weight:700; }}
.pill-green {{ background:rgba(134,239,172,.15); color:#86efac; }}
.pill-red {{ background:rgba(251,113,133,.15); color:#fb7185; }}
.pill-yellow {{ background:rgba(248,214,109,.15); color:#f8d66d; }}
.pill-gray {{ background:rgba(148,163,184,.15); color:#94a3b8; }}
pre {{ max-height:260px; overflow:auto; white-space:pre-wrap; color:#d6deea; }}
table {{ width:100%; border-collapse:collapse; }}
th, td {{ padding:10px 12px; border:1px solid var(--line); text-align:left; }}
th {{ color:var(--muted); font-size:.78rem; text-transform:uppercase; }}
.empty {{ color:var(--muted); font-style:italic; }}
.btn-row {{ display:flex; flex-wrap:wrap; gap:10px; margin-top:12px; }}
.btn {{ padding:8px 14px; border:1px solid var(--line); border-radius:12px; color:var(--text); text-decoration:none; background:rgba(255,255,255,.04); }}
.btn-primary {{ border-color:var(--accent); background:rgba(125,211,252,.12); }}
{extra_style}
</style>
</head>
<body>
<main class="shell">
{nav_html}
{content}
</main>
{extra_script}
</body>
</html>"""


def hero_section(*, kicker: str = "", title: str = "", summary: str = "", extra: str = "") -> str:
    """Return a hero section with optional kicker, large title, and summary."""
    parts = ""
    if kicker:
        parts += f'<span class="kicker">{escape(kicker)}</span>'
    if title:
        parts += f"<h1>{escape(title)}</h1>"
    if summary:
        parts += f'<p class="summary">{escape(summary)}</p>'
    if extra:
        parts += extra
    return f'<section class="hero">\n{parts}\n</section>'


def card(title: str, body: str, *, kicker: str = "", wide: bool = False) -> str:
    """Return a single info card with optional kicker and title."""
    css = ' class="card wide"' if wide else ' class="card"'
    parts = ""
    if kicker:
        parts += f'<span class="kicker">{escape(kicker)}</span>'
    if title:
        parts += f"<strong>{escape(title)}</strong>"
    parts += body
    return f"<article{css}>\n{parts}\n</article>"


def grid(items: str, cols: int = 3) -> str:
    """Wrap content in a responsive grid container."""
    col_class = {2: "grid-2", 3: "grid-3", 4: "grid-4"}.get(cols, "grid-3")
    return f'<section class="{col_class}">\n{items}\n</section>'


def pill(value: str, status: str = "gray") -> str:
    """Return a colored status pill.

    status: green, red, yellow, gray
    """
    color_map = {"green": "pill-green", "red": "pill-red", "yellow": "pill-yellow", "gray": "pill-gray"}
    css = color_map.get(status, "pill-gray")
    return f'<span class="pill {css}">{escape(value)}</span>'


def section_card(heading: str, body: str, *, step: str = "", action_link: str = "") -> str:
    """Return a section card with heading, optional step number, and action link."""
    step_html = f'<div class="journey-step"><span>{escape(step)}</span></div>' if step else ""
    link_html = f'<a class="btn" href="{escape(action_link)}">View</a>' if action_link else ""
    head = f'<div class="home-section-header"><div><h2>{escape(heading)}</h2></div>{link_html}</div>' if heading else ""
    return f"""<article class="decision-card">
{step_html}
{head}
{body}
</article>"""


def metric(label: str, value: str, *, primary: bool = False) -> str:
    """Return a metric display card."""
    css = "metric primary" if primary else "metric"
    return f"""<div class="{css}">
<span class="metric-label">{escape(label)}</span>
<strong>{escape(value)}</strong>
</div>"""


def data_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    """Return a data table with header row and body rows."""
    header_cells = "".join(f"<th>{escape(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        cells = "".join(f"<td>{escape(str(cell))}</td>" for cell in row)
        body += f"<tr>{cells}</tr>"
    if not body:
        body = '<tr><td class="empty" colspan="' + str(len(headers)) + '">No data available</td></tr>'
    return f"<table><thead><tr>{header_cells}</tr></thead><tbody>{body}</tbody></table>"


def button_row(buttons: Sequence[dict[str, str]]) -> str:
    """Return a button row. Each button is {"href": "...", "label": "...", "primary": bool}."""
    items = ""
    for btn in buttons:
        css = "btn btn-primary" if btn.get("primary") else "btn"
        items += f'<a class="{css}" href="{escape(btn.get("href", "#"))}">{escape(btn.get("label", "Button"))}</a>'
    return f'<div class="btn-row">{items}</div>'


def status_block(label: str, value: str, *, status: str = "gray") -> str:
    """Return a label + pill pair for inline status display."""
    return f"""<div>
<span>{escape(label)}</span>
{pill(value, status)}
</div>"""


def section(title: str, body: str, *, extra_class: str = "") -> str:
    """Wrap content in a titled section."""
    return f"""<section class="{extra_class}">
<h2>{escape(title)}</h2>
{body}
</section>"""