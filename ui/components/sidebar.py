"""Sidebar navigation for the Atlas OS control plane."""

from __future__ import annotations


def render_sidebar() -> str:
    """Render the left system-control sidebar."""

    items = [
        ("System Status", "/dashboard", "status"),
        ("Model Configuration", "/settings#llm-config", "model"),
        ("API Keys", "/settings#llm-config", "keys"),
        ("Runtime Settings", "/settings#system-config", "runtime"),
        ("Asset Configuration", "/settings#asset-config", "assets"),
        ("LLM Providers", "/settings#llm-config", "providers"),
        ("Logs", "/replay?format=json", "logs"),
        ("Roadmap", "/roadmap", "roadmap"),
    ]
    links = "\n".join(
        f'<a class="sidebar-link" href="{href}" data-sidebar-section="{section}"><span>{label}</span></a>'
        for label, href, section in items
    )
    return f"""
    <aside class="control-sidebar" data-component="sidebar">
      <div class="sidebar-brand">
        <div class="sidebar-mark">AT</div>
        <div>
          <strong>Atlas Control Plane</strong>
          <span>Production runtime console</span>
        </div>
      </div>
      <nav class="sidebar-nav" aria-label="System control navigation">
        {links}
      </nav>
      <div class="sidebar-footer">
        <span>Mode</span>
        <strong>Simulation</strong>
      </div>
    </aside>
    """
