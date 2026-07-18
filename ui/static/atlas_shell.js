  const pollMs = 1500;
  let lastTick = null;
  let stillPolls = 0;
  let lastStreamSignature = "";
  let latestReplay = null;

  function byId(id) { return document.getElementById(id); }
  function setText(id, value) {
    const node = byId(id);
    if (!node) return;
    const text = clean(value);
    node.textContent = text;
    if (text === "Waiting for cognitive signal") {
      node.title = "System has not yet converged on this metric.";
      node.classList.add("empty-pulse");
    } else if (text === "Insufficient system context" || text === "System initializing reasoning layer") {
      node.title = "Atlas needs more runtime context before this field becomes meaningful.";
      node.classList.add("empty-pulse");
    } else if (String(value || "").toLowerCase() === "neutral") {
      node.title = "No strong regime signal is active.";
      node.classList.remove("empty-pulse");
    } else {
      node.removeAttribute("title");
      node.classList.remove("empty-pulse");
    }
  }
  function setDualText(id, label) {
    const node = byId(id);
    if (!node) return;
    const data = asObject(label);
    const primary = clean(data.primary || label || "");
    const secondary = clean(data.secondary || "");
    node.textContent = "";
    const main = document.createElement("span");
    main.textContent = primary;
    node.appendChild(main);
    if (secondary && secondary !== "System initializing reasoning layer") {
      const small = document.createElement("small");
      small.textContent = secondary;
      node.appendChild(small);
    }
  }
  function clean(value) {
    if (value === null || value === undefined || value === "") return "System initializing reasoning layer";
    const textValue = String(value).trim();
    if (textValue.toUpperCase() === "UNKNOWN") return "Waiting for cognitive signal";
    if (textValue.toLowerCase() === "unknown") return "Insufficient system context";
    if (typeof value === "number") return Number.isInteger(value) ? String(value) : value.toFixed(3);
    return String(value);
  }
  function packetFrom(state) {
    return state.last_decision_packet && typeof state.last_decision_packet === "object" ? state.last_decision_packet : {};
  }
  function dashboardFrom(state) {
    return state.dashboard && typeof state.dashboard === "object" ? state.dashboard : {};
  }
  function asObject(value) {
    return value && typeof value === "object" && !Array.isArray(value) ? value : {};
  }
  function asArray(value) {
    return Array.isArray(value) ? value : [];
  }
  function updateRuntimeStatus(tick) {
    const pill = byId("runtime-status-pill");
    if (!pill) return;
    if (lastTick === null) {
      pill.textContent = "RUNNING";
      pill.className = "status-pill status-running";
    } else if (tick === lastTick) {
      stillPolls += 1;
      if (stillPolls >= 3) {
        pill.textContent = "STOPPED";
        pill.className = "status-pill status-stopped";
      }
    } else {
      stillPolls = 0;
      pill.textContent = "RUNNING";
      pill.className = "status-pill status-running";
    }
    lastTick = tick;
  }
  function updateState(state) {
    const packet = packetFrom(state);
    const presentation = asObject(state.ui_presentation);
    const hero = asObject(presentation.hero);
    const decision = asObject(presentation.decision);
    const inspector = asObject(presentation.inspector);
    setDualText("state-regime", { primary: hero.title || state.regime_state, secondary: hero.secondary || "" });
    setText("state-trust", state.trust_index);
    setText("state-liquidity", state.liquidity);
    setText("state-attention", state.attention);
    setText("state-volatility", state.volatility);
    setText("state-tick", state.tick_counter || 0);
    setDualText("decision-action", decision.action || { primary: packet.recommended_action || "neutral" });
    setText("decision-confidence", (decision.confidence ? "Confidence " + decision.confidence : "Confidence " + clean(packet.confidence || 0)));
    setDualText("decision-risk", decision.risk || { primary: packet.risk_level || "unknown" });
    setDualText("decision-attention", decision.attention || { primary: packet.attention_state || state.attention });
    setDualText("decision-liquidity", decision.liquidity || { primary: packet.liquidity_state || state.liquidity });
    setText("decision-summary", decision.summary || packet.causal_summary || "Waiting for DecisionPacket.");
    setText("causal-summary", inspector.causal_summary || decision.summary || packet.causal_summary || "Unknown");
    setText("llm-call-count", (state.llm_trace_summary || {}).call_count || 0);
    setText("llm-model", (state.llm_trace_summary || {}).latest_model);
    setText("llm-latency", clean((state.llm_trace_summary || {}).latest_latency_ms) + " ms");
    setText("focus-runtime-status", state.tick_counter ? "Runtime loop active" : "Initializing cognition layer");
    updateProviderMini(state.llm_provider_registry || {});

    const trust = typeof state.trust_index === "number" ? Math.max(0, Math.min(1, state.trust_index)) : 0;
    const meter = byId("trust-meter");
    if (meter) meter.style.width = (trust * 100).toFixed(1) + "%";
    setText("trust-trend", inspector.trust_trend || (trust >= 0.7 ? "Stable trust field" : trust >= 0.4 ? "Moderate trust field" : "Low trust field"));
    setText("stability-index", inspector.stability || (trust >= 0.7 ? "Stable" : trust >= 0.4 ? "Watchful" : "Insufficient system context"));

    const decisionTrace = {
      tick: state.tick_counter || 0,
      brief_id: state.last_decision_brief_id || null,
      regime: state.regime_state || "Unknown",
      action: packet.recommended_action || "neutral",
      risk: packet.risk_level || "unknown"
    };
    const decisionNode = byId("decision-trace");
    if (decisionNode) {
      decisionNode.textContent = "tick " + decisionTrace.tick + ", regime " + clean(decisionTrace.regime) + ", decision " + clean(decisionTrace.action);
    }

    const structuralNode = byId("structural-state");
    if (structuralNode) {
      const structuralSummary = summarizeStructure(state.structural_coevolution_state || state.self_organization_state || {});
      structuralNode.textContent = structuralSummary;
    }
    updateHypothesisState(state);
    updateDecisionExplanation(state, packet, inspector);
    updateCausalGraph(state);
    updateRegimeMap(state);
    updateDriftTimeline(state);
    updateRuntimeStatus(state.tick_counter || 0);
    pushStream(state, packet, decision);
  }
  function updateHypothesisState(state) {
    const structural = asObject(state.structural_coevolution_state || state.self_organization_state);
    const hypothesis = asObject(structural.hypothesis_state || structural.active_hypothesis || structural.causal_hypothesis);
    setText("active-hypothesis", hypothesis.id || hypothesis.name || structural.active_hypothesis_id || "Insufficient system context");
    const shadow = structural.shadow_hypothesis_count || structural.shadow_count || asArray(structural.shadow_hypotheses).length || 0;
    setText("shadow-hypothesis-count", shadow);
  }
  function summarizeStructure(value) {
    const structural = asObject(value);
    if (!Object.keys(structural).length) return "No structural drift summary yet";
    const mutation = asObject(structural.mutated_graph || structural.causal_graph_mutation || structural);
    const drift = asObject(structural.applied_drift || structural.drift_summary || structural);
    const pieces = [];
    if (mutation.structural_shift_index !== undefined) pieces.push("shift " + clean(mutation.structural_shift_index));
    if (mutation.mutation_intensity !== undefined) pieces.push("mutation " + clean(mutation.mutation_intensity));
    if (drift.bounded !== undefined) pieces.push(drift.bounded ? "bounded" : "needs review");
    return pieces.join(" · ") || "Structural state summarized";
  }
  function updateProviderMini(registry) {
    const providers = Array.isArray(registry.providers) ? registry.providers : [];
    const active = registry.active_provider || "openai";
    const provider = providers.find(function (item) { return item.id === active; }) || {};
    setText("active-provider-label", provider.label || active);
    setText("active-provider-model", provider.model || "System initializing reasoning layer");
    setText("active-provider-health", provider.health || "unknown");
  }
  function updateDecisionExplanation(state, packet, inspector) {
    inspector = asObject(inspector);
    const factors = asArray(inspector.factors).length ? asArray(inspector.factors) : dominantFactors(state, packet).map(function (item) { return { primary: item, secondary: "" }; });
    const action = asObject(asObject(state.ui_presentation).decision).action || { primary: packet.recommended_action || "neutral" };
    const regime = state.regime_state || "Unknown";
    const trust = typeof state.trust_index === "number" ? state.trust_index : null;
    const reason = packet.reasoning_trace || packet.causal_summary || "System initializing reasoning layer";
    renderReasonSections("decision-why", inspector.sections, inspector.reasoning_summary || reason);
    setText("regime-influence", inspector.regime_influence || (regime + " -> " + clean(action.primary || action)));
    setText("trust-impact", inspector.trust_impact || (trust === null ? "Unknown" : (trust >= 0.7 ? "High trust supports explanation weight" : trust >= 0.4 ? "Medium trust tempers explanation weight" : "Low trust limits explanation weight")));
    const list = byId("dominant-causal-factors");
    if (list) {
      list.textContent = "";
      factors.forEach(function (factor) {
        const chip = document.createElement("span");
        chip.className = "factor-chip";
        const label = asObject(factor);
        const primary = document.createElement("span");
        primary.textContent = clean(label.primary || factor);
        chip.appendChild(primary);
        if (label.secondary) {
          const small = document.createElement("small");
          small.textContent = clean(label.secondary);
          chip.appendChild(small);
        }
        list.appendChild(chip);
      });
    }
  }
  function renderReasonSections(id, sections, fallback) {
    const node = byId(id);
    if (!node) return;
    const usable = asArray(sections);
    if (!usable.length) {
      setText(id, fallback);
      return;
    }
    node.textContent = "";
    const list = document.createElement("ul");
    list.className = "localized-reason-list";
    usable.slice(0, 3).forEach(function (section) {
      const data = asObject(section);
      const item = document.createElement("li");
      const title = document.createElement("strong");
      const body = document.createElement("span");
      title.textContent = clean(data.title);
      body.textContent = clean(data.body);
      item.appendChild(title);
      item.appendChild(body);
      list.appendChild(item);
    });
    node.appendChild(list);
  }
  function dominantFactors(state, packet) {
    const factors = [];
    if (packet.risk_level) factors.push("risk:" + packet.risk_level);
    if (packet.attention_state || state.attention !== undefined) factors.push("attention:" + clean(packet.attention_state || state.attention));
    if (packet.liquidity_state || state.liquidity !== undefined) factors.push("liquidity:" + clean(packet.liquidity_state || state.liquidity));
    if (state.volatility !== undefined) factors.push("volatility:" + clean(state.volatility));
    if (state.trust_index !== undefined && state.trust_index !== null) factors.push("trust:" + clean(state.trust_index));
    return factors.slice(0, 3);
  }
  function extractCausalEdges(state) {
    const dashboard = dashboardFrom(state);
    const graph = asObject(dashboard.causal_graph_snapshot);
    const structural = asObject(state.structural_coevolution_state);
    const mutated = asObject(structural.mutated_graph || structural.causal_graph_mutation || structural);
    const edgeUpdates = asObject(mutated.edge_weight_updates);
    const edges = [];
    if (Array.isArray(graph.edges)) {
      graph.edges.forEach(function (edge) {
        if (!edge) return;
        edges.push({
          from: edge.from || edge.source || edge[0] || "Source",
          to: edge.to || edge.target || edge[1] || "Target",
          weight: Number(edge.weight || edge.value || 0.5),
          drift: Number(edge.drift || edge.delta || 0)
        });
      });
    }
    Object.keys(graph).forEach(function (key) {
      const value = graph[key];
      if (key.indexOf("->") > -1) {
        const parts = key.split("->");
        edges.push({ from: parts[0].trim(), to: parts[1].trim(), weight: Number(value || 0.5), drift: 0 });
      } else if (value && typeof value === "object" && !Array.isArray(value)) {
        Object.keys(value).forEach(function (target) {
          if (typeof value[target] === "number") edges.push({ from: key, to: target, weight: value[target], drift: 0 });
        });
      }
    });
    Object.keys(edgeUpdates).forEach(function (key) {
      const parts = key.indexOf("->") > -1 ? key.split("->") : key.split(":");
      edges.push({
        from: (parts[0] || "Source").trim(),
        to: (parts[1] || "Target").trim(),
        weight: Math.abs(Number(edgeUpdates[key] || 0)),
        drift: Number(edgeUpdates[key] || 0)
      });
    });
    if (!edges.length) {
      return [
        { from: "Narrative", to: "Attention", weight: 0.6, drift: 0.0 },
        { from: "Attention", to: "Retail Flow", weight: 0.55, drift: 0.0 },
        { from: "Liquidity", to: "Volatility", weight: 0.7, drift: 0.0 },
        { from: "Institutional Flow", to: "Liquidity", weight: 0.5, drift: 0.0 },
        { from: "Price Momentum", to: "Attention", weight: 0.45, drift: 0.0 }
      ];
    }
    return edges.slice(0, 14);
  }
  function updateCausalGraph(state) {
    const svg = byId("causal-graph-svg");
    const list = byId("causal-edge-list");
    if (!svg) return;
    const edges = extractCausalEdges(state);
    const nodes = Array.from(new Set(edges.flatMap(function (edge) { return [edge.from, edge.to]; }))).slice(0, 10);
    const centerX = 360, centerY = 210, radius = 145;
    const points = {};
    nodes.forEach(function (node, index) {
      const angle = -Math.PI / 2 + (Math.PI * 2 * index / Math.max(nodes.length, 1));
      points[node] = { x: centerX + Math.cos(angle) * radius, y: centerY + Math.sin(angle) * radius };
    });
    svg.textContent = "";
    edges.forEach(function (edge) {
      const a = points[edge.from], b = points[edge.to];
      if (!a || !b) return;
      const line = svgEl("line", {
        x1: a.x, y1: a.y, x2: b.x, y2: b.y,
        stroke: Math.abs(edge.drift) > 0.08 ? "#f8d66d" : "#5eead4",
        "stroke-width": 1.2 + Math.min(4, Math.abs(edge.weight || 0.2) * 4),
        opacity: 0.72
      });
      svg.appendChild(line);
      const label = svgEl("text", { x: (a.x + b.x) / 2, y: (a.y + b.y) / 2 - 4, fill: "#cbd5e1", "font-size": "11", "text-anchor": "middle" });
      label.textContent = clean(edge.weight);
      svg.appendChild(label);
    });
    nodes.forEach(function (node) {
      const point = points[node];
      svg.appendChild(svgEl("circle", { cx: point.x, cy: point.y, r: 29, fill: "rgba(15, 23, 35, 0.95)", stroke: "#5eead4", "stroke-width": 1.4 }));
      const label = svgEl("text", { x: point.x, y: point.y + 4, fill: "#e6edf3", "font-size": "11", "text-anchor": "middle" });
      label.textContent = shortLabel(node);
      svg.appendChild(label);
    });
    if (list) {
      list.textContent = "";
      edges.forEach(function (edge) {
        const item = document.createElement("div");
        item.className = "mini-item" + (Math.abs(edge.drift) > 0.08 ? " drifted" : "");
        item.textContent = edge.from + " -> " + edge.to + " | weight " + clean(edge.weight) + " | drift " + clean(edge.drift);
        list.appendChild(item);
      });
    }
  }
  function updateRegimeMap(state) {
    const svg = byId("regime-map-svg");
    const list = byId("regime-transition-list");
    if (!svg) return;
    const replayTimeline = asArray(asObject(latestReplay).decision_timeline).map(function (item) {
      return { tick: item.tick, regime_state: item.regime_state };
    });
    const timeline = asArray(dashboardFrom(state).regime_state_timeline).concat(replayTimeline);
    const names = Array.from(new Set(timeline.map(function (item) { return item.regime_state || item.state; }).filter(Boolean)));
    if (!names.includes(state.regime_state || "Unknown")) names.push(state.regime_state || "Unknown");
    const regimes = (names.length ? names : ["NORMAL", "HIGH_VOLATILITY", "RISK_OFF", "ATTENTION_EXPANSION"]).slice(0, 7);
    const current = state.regime_state || regimes[0] || "Unknown";
    const transitions = {};
    for (let i = 1; i < timeline.length; i += 1) {
      const from = timeline[i - 1].regime_state || timeline[i - 1].state || "Unknown";
      const to = timeline[i].regime_state || timeline[i].state || "Unknown";
      transitions[from + "->" + to] = (transitions[from + "->" + to] || 0) + 1;
    }
    svg.textContent = "";
    const width = 720, baseY = 210, gap = width / Math.max(regimes.length + 1, 2);
    const points = {};
    regimes.forEach(function (name, index) {
      points[name] = { x: gap * (index + 1), y: baseY + (index % 2 === 0 ? -62 : 62) };
    });
    Object.keys(transitions).forEach(function (key) {
      const parts = key.split("->"), a = points[parts[0]], b = points[parts[1]];
      if (!a || !b) return;
      svg.appendChild(svgEl("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y, stroke: "#f8d66d", "stroke-width": 1 + transitions[key], opacity: 0.6 }));
    });
    regimes.forEach(function (name) {
      const point = points[name];
      const active = name === current;
      svg.appendChild(svgEl("circle", { cx: point.x, cy: point.y, r: active ? 45 : 34, fill: active ? "rgba(94, 234, 212, 0.2)" : "rgba(15, 23, 35, 0.95)", stroke: active ? "#5eead4" : "#94a3b8", "stroke-width": active ? 2 : 1 }));
      const label = svgEl("text", { x: point.x, y: point.y + 4, fill: "#e6edf3", "font-size": "11", "text-anchor": "middle" });
      label.textContent = shortLabel(name);
      svg.appendChild(label);
      const basin = svgEl("text", { x: point.x, y: point.y + 61, fill: "#94a3b8", "font-size": "10", "text-anchor": "middle" });
      basin.textContent = active ? "active basin" : "stability basin";
      svg.appendChild(basin);
    });
    if (list) {
      list.textContent = "";
      const keys = Object.keys(transitions);
      (keys.length ? keys : [current + "->" + current]).forEach(function (key) {
        const item = document.createElement("div");
        item.className = "mini-item";
        item.textContent = key + " | weight " + clean(transitions[key] || 1);
        list.appendChild(item);
      });
    }
  }
  function updateDriftTimeline(state) {
    const svg = byId("drift-timeline-svg");
    const list = byId("drift-timeline-list");
    if (!svg) return;
    const trustCurve = asArray(dashboardFrom(state).trust_field_evolution_curve);
    const replayTimeline = asArray(asObject(latestReplay).cognitive_state_evolution).map(function (item) {
      return { tick: item.tick, trust_field_evolution: asObject(item.trust_state).feedback_stability_index, regime_state: asObject(item.system_state).current_state };
    });
    const timeline = asArray(dashboardFrom(state).regime_state_timeline).concat(replayTimeline);
    const points = trustCurve.length ? trustCurve : timeline.map(function (item, index) {
      return { tick: item.tick || index, trust_field_evolution: 0.5, regime_state: item.regime_state };
    });
    svg.textContent = "";
    const usable = points.slice(-18);
    const maxTick = Math.max(1, usable.length - 1);
    const values = usable.map(function (item) {
      const raw = item.trust_field_evolution;
      return typeof raw === "number" ? raw : (typeof state.trust_index === "number" ? state.trust_index : 0.5);
    });
    let path = "";
    values.forEach(function (value, index) {
      const x = 40 + index * (840 / Math.max(maxTick, 1));
      const y = 270 - Math.max(0, Math.min(1, value)) * 220;
      path += (index === 0 ? "M " : " L ") + x + " " + y;
      svg.appendChild(svgEl("circle", { cx: x, cy: y, r: 4, fill: "#5eead4" }));
    });
    svg.appendChild(svgEl("path", { d: path || "M 40 160 L 880 160", fill: "none", stroke: "#5eead4", "stroke-width": 2.4 }));
    svg.appendChild(svgEl("text", { x: 40, y: 28, fill: "#cbd5e1", "font-size": "12" })).textContent = "trust field evolution";
    svg.appendChild(svgEl("line", { x1: 40, y1: 270, x2: 880, y2: 270, stroke: "#334155", "stroke-width": 1 }));
    svg.appendChild(svgEl("line", { x1: 40, y1: 50, x2: 40, y2: 270, stroke: "#334155", "stroke-width": 1 }));
    if (list) {
      list.textContent = "";
      usable.slice(-8).forEach(function (item, index) {
        const row = document.createElement("div");
        row.className = "timeline-item";
        row.textContent = "tick " + clean(item.tick || index) + " | trust=" + clean(values[Math.max(0, values.length - usable.slice(-8).length + index)]) + " | regime=" + clean(item.regime_state || state.regime_state);
        list.appendChild(row);
      });
    }
  }
  function shortLabel(value) {
    const text = String(value || "Unknown").replace(/_/g, " ");
    return text.length > 18 ? text.slice(0, 16) + ".." : text;
  }
  function svgEl(name, attrs) {
    const node = document.createElementNS("http://www.w3.org/2000/svg", name);
    Object.keys(attrs || {}).forEach(function (key) { node.setAttribute(key, attrs[key]); });
    return node;
  }
  function pushStream(state, packet, decision) {
    const stream = byId("event-stream");
    if (!stream) return;
    const tick = state.tick_counter || 0;
    const action = asObject(asObject(decision).action).primary || packet.recommended_action || "neutral";
    const signature = [tick, state.regime_state, state.trust_index, action].join("|");
    if (signature === lastStreamSignature) return;
    lastStreamSignature = signature;
    const line = document.createElement("div");
    line.className = "stream-line";
    const now = new Date();
    const time = document.createElement("time");
    time.textContent = now.toLocaleTimeString();
    const msg = document.createElement("span");
    msg.textContent = "tick=" + tick + " regime=" + clean(state.regime_state) + " trust=" + clean(state.trust_index) + " decision=" + action;
    line.appendChild(time);
    line.appendChild(msg);
    stream.prepend(line);
    while (stream.children.length > 80) stream.removeChild(stream.lastChild);
    setText("stream-clock", now.toLocaleTimeString());
  }
  async function refreshState() {
    try {
      const response = await fetch("/state", { cache: "no-store" });
      if (!response.ok) throw new Error("state request failed");
      const state = await response.json();
      updateState(state);
      refreshReplay(state.tick_counter || 0);
    } catch (error) {
      const pill = byId("runtime-status-pill");
      if (pill) {
        pill.textContent = "STOPPED";
        pill.className = "status-pill status-stopped";
      }
      addChatLine("system", "State refresh failed: " + error.message);
    }
  }
  async function refreshReplay(tick) {
    const endTick = Math.max(1, Number(tick || 1));
    const startTick = Math.max(0, endTick - 20);
    try {
      const response = await fetch("/replay?start_tick=" + startTick + "&end_tick=" + endTick + "&format=json", { cache: "no-store" });
      if (response.ok) latestReplay = await response.json();
    } catch (error) {
      latestReplay = latestReplay || null;
    }
  }
  function addChatLine(kind, text) {
    const box = byId("chat-messages");
    if (!box) return;
    const line = document.createElement("div");
    line.className = "chat-line " + (kind || "system");
    line.textContent = text;
    box.prepend(line);
    while (box.children.length > 40) box.removeChild(box.lastChild);
  }
  async function postForm(url, values) {
    const body = new URLSearchParams(values || {});
    const response = await fetch(url, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body
    });
    return response.json();
  }
  function bindControls() {
    bindOnboarding();
    bindModeSwitcher();
    bindWorkflowExplanation();
    document.querySelectorAll("[data-open-overlay]").forEach(function (button) {
      button.addEventListener("click", function () {
        const target = byId(button.getAttribute("data-open-overlay"));
        if (target) target.classList.remove("hidden");
      });
    });
    document.querySelectorAll("[data-close-overlay]").forEach(function (button) {
      button.addEventListener("click", function () {
        const overlay = button.closest(".explainability-overlay");
        if (overlay) overlay.classList.add("hidden");
      });
    });
    document.querySelectorAll(".explainability-overlay").forEach(function (overlay) {
      overlay.addEventListener("click", function (event) {
        if (event.target === overlay) overlay.classList.add("hidden");
      });
    });
    const form = byId("chat-form");
    if (form) {
      form.addEventListener("submit", async function (event) {
        event.preventDefault();
        const input = byId("chat-input");
        const message = input ? input.value.trim() : "";
        if (!message) return;
        addChatLine("user", "You: " + message);
        if (input) input.value = "";
        try {
          const result = await postForm("/chat/send", { message });
          addChatLine("system", "Queued: " + clean(result.status));
          refreshState();
        } catch (error) {
          addChatLine("system", "Queue failed: " + error.message);
        }
      });
    }
    const start = byId("runtime-start");
    if (start) start.addEventListener("click", async function () {
      try {
        const result = await postForm("/control/start", {});
        addChatLine("system", "Start: " + clean(result.status));
        await refreshState();
      }
      catch (error) { addChatLine("system", "Start failed: " + error.message); }
    });
    const stop = byId("runtime-stop");
    if (stop) stop.addEventListener("click", async function () {
      try {
        const result = await postForm("/control/stop", {});
        addChatLine("system", "Stop: " + clean(result.status));
        const pill = byId("runtime-status-pill");
        if (pill) {
          pill.textContent = "STOPPED";
          pill.className = "status-pill status-stopped";
        }
        await refreshState();
      }
      catch (error) { addChatLine("system", "Stop failed: " + error.message); }
    });
    const interval = byId("tick-interval");
    if (interval) interval.addEventListener("change", async function () {
      try { addChatLine("system", "Tick interval saved: " + clean((await postForm("/control/set_interval", { interval_seconds: interval.value })).tick_interval_seconds) + "s"); }
      catch (error) { addChatLine("system", "Interval update failed: " + error.message); }
    });
    const language = byId("language-select");
    if (language) language.addEventListener("change", async function () {
      try {
        await postForm("/ui/language", { language: language.value });
        window.location.reload();
      } catch (error) {
        addChatLine("system", "Language update failed: " + error.message);
      }
    });
  }
  function bindModeSwitcher() {
    document.querySelectorAll("[data-v2-mode]").forEach(function (button) {
      button.addEventListener("click", function () {
        const mode = button.getAttribute("data-v2-mode");
        document.querySelectorAll("[data-v2-mode]").forEach(function (item) { item.classList.toggle("active", item === button); });
        document.querySelectorAll("[data-mode-panel]").forEach(function (panel) {
          panel.classList.toggle("active", panel.getAttribute("data-mode-panel") === mode);
        });
      });
    });
  }
  function bindWorkflowExplanation() {
    document.querySelectorAll("[data-workflow-node]").forEach(function (node) {
      node.addEventListener("click", function (event) {
        event.preventDefault();
        const panel = byId("workflow-node-explanation");
        if (!panel) return;
        document.querySelectorAll("[data-workflow-node]").forEach(function (item) { item.classList.remove("active"); });
        node.classList.add("active");
        panel.innerHTML = "<strong>" + node.textContent.trim() + "</strong><span>" + (node.getAttribute("data-explanation") || "") + "</span>";
      });
    });
  }
  function bindOnboarding() {
    const overlay = byId("onboarding-overlay");
    if (!overlay) return;
    overlay.classList.remove("hidden");
    runBootSequence();
    const enter = byId("enter-dashboard");
    if (enter) enter.addEventListener("click", function () {
      overlay.classList.add("hidden");
    });
    const tour = byId("start-system-tour");
    if (tour) tour.addEventListener("click", function () {
      overlay.classList.add("hidden");
      const target = byId("system-navigation-card") || document.querySelector(".nav-tabs");
      if (target) {
        target.classList.add("tour-highlight");
        target.scrollIntoView({ behavior: "smooth", block: "center" });
        window.setTimeout(function () { target.classList.remove("tour-highlight"); }, 4200);
      }
      addChatLine("system", "Tour started: use System State for live regime, Roadmap for lifecycle, Dev Registry for history, and System Guide for state meanings.");
    });
  }
  function runBootSequence() {
    const steps = Array.from(document.querySelectorAll(".boot-step"));
    steps.forEach(function (step) { step.classList.remove("active"); });
    steps.forEach(function (step, index) {
      window.setTimeout(function () {
        steps.forEach(function (item) { item.classList.remove("active"); });
        step.classList.add("active");
      }, index * 2500);
    });
  }
  bindControls();
  refreshState();
  window.setInterval(refreshState, pollMs);
})();
