"use strict";

const $ = (id) => document.getElementById(id);
const api = async (path, opts) => {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error(`${path} -> ${res.status}`);
  return res.json();
};

const EXAMPLE = {
  service: "checkout-service",
  description:
    "checkout-service suddenly returning 503s during a flash sale; HikariCP " +
    "'Connection is not available, request timed out after 30000ms' timeouts; " +
    "Postgres pg_stat_activity shows connections maxed out (199/200).",
};

// --- tiny, safe markdown-ish renderer (bold, code, headings, lists) ---
function esc(s) {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
function mdlite(s) {
  let h = esc(s);
  h = h.replace(/`([^`]+)`/g, "<code>$1</code>");
  h = h.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  h = h.replace(/_([^_]+)_/g, "<em>$1</em>");
  return h;
}

async function refreshStatus() {
  try {
    const s = await api("/api/status");
    $("pill-backend").textContent = "memory: " + s.memory_backend;
    $("pill-count").textContent = s.memory_count + " memories";
    $("pill-model").textContent = "model: " + s.model;
  } catch (e) {}
}

async function refreshMemories() {
  try {
    const { memories } = await api("/api/memories");
    $("mem-total").textContent = memories.length;
    const list = $("mem-list");
    list.innerHTML = "";
    memories.slice(0, 40).forEach((m) => {
      const li = document.createElement("li");
      const when = (m.timestamp || "").split("T")[0] || "";
      li.innerHTML = `<span class="when">${when}</span> · ${esc(
        (m.text || "").slice(0, 130)
      )}`;
      list.appendChild(li);
    });
  } catch (e) {}
}

function renderRecall(recalled) {
  const list = $("recall-list");
  const empty = $("recall-empty");
  list.innerHTML = "";
  if (!recalled || recalled.length === 0) {
    empty.style.display = "block";
    empty.textContent = "No prior memory matched — the agent is treating this as novel.";
    return;
  }
  empty.style.display = "none";
  recalled.forEach((h) => {
    const li = document.createElement("li");
    const when = (h.timestamp || "").split("T")[0] || "unknown";
    li.innerHTML =
      `<div class="meta"><span>${when}</span><span class="score">score ${h.score}</span></div>` +
      esc(h.text);
    list.appendChild(li);
  });
}

async function diagnose() {
  const description = $("description").value.trim();
  if (!description) return;
  const service = $("service").value.trim() || null;
  const btn = $("btn-diagnose");
  btn.disabled = true;
  btn.textContent = "Diagnosing…";
  try {
    const resp = await api("/api/incident", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description, service }),
    });
    $("answer-card").hidden = false;
    $("answer").innerHTML = mdlite(resp.answer);
    $("answer-model").textContent = "model: " + resp.model;
    $("answer-runbooks").textContent = resp.runbooks.length
      ? "runbooks: " + resp.runbooks.join(", ")
      : "no runbook matched";
    renderRecall(resp.recalled);
    // prefill resolve form
    $("resolve-card").hidden = false;
    if (service) $("r-id").placeholder = "INC-" + Math.floor(3000 + Math.random() * 900);
  } catch (e) {
    $("answer-card").hidden = false;
    $("answer").textContent = "Error: " + e.message;
  } finally {
    btn.disabled = false;
    btn.textContent = "Diagnose";
  }
}

async function seed() {
  const btn = $("btn-seed");
  btn.disabled = true;
  btn.textContent = "Seeding…";
  try {
    await api("/api/seed", { method: "POST" });
    await refreshStatus();
    await refreshMemories();
  } finally {
    btn.disabled = false;
    btn.textContent = "Seed incident history";
  }
}

async function resolve() {
  const body = {
    incident_id: $("r-id").value.trim() || "INC-" + Math.floor(3000 + Math.random() * 900),
    service: $("service").value.trim() || "unknown",
    symptoms: $("description").value.trim(),
    root_cause: $("r-cause").value.trim(),
    resolution: $("r-resolution").value.trim(),
    what_worked: $("r-worked").value.trim(),
  };
  const btn = $("btn-resolve");
  btn.disabled = true;
  try {
    await api("/api/resolve", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    ["r-cause", "r-resolution", "r-worked"].forEach((id) => ($(id).value = ""));
    await refreshStatus();
    await refreshMemories();
    btn.textContent = "Retained ✓";
    setTimeout(() => (btn.textContent = "Retain postmortem →"), 1500);
  } finally {
    btn.disabled = false;
  }
}

async function insight() {
  const q = $("insight-q").value.trim();
  if (!q) return;
  $("insight-out").textContent = "thinking…";
  try {
    const { insight } = await api("/api/insights", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: q }),
    });
    $("insight-out").innerHTML = mdlite(insight);
  } catch (e) {
    $("insight-out").textContent = "Error: " + e.message;
  }
}

$("btn-diagnose").onclick = diagnose;
$("btn-seed").onclick = seed;
$("btn-resolve").onclick = resolve;
$("btn-insight").onclick = insight;
$("btn-refresh").onclick = () => {
  refreshStatus();
  refreshMemories();
};
$("btn-example").onclick = () => {
  $("service").value = EXAMPLE.service;
  $("description").value = EXAMPLE.description;
};

refreshStatus();
refreshMemories();
