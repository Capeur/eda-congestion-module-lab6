/**
 * Congestion heat map — Lab 06 browser lab (UI half).
 *
 * All state, rules and challenge predicates live in the pure model
 * ./congestion-map-lab-model.js (no DOM, tested in Node against the module's checker).
 * This file only draws and wires controls:
 *   - click a cell to select it, click empty canvas to drag it (drag clamp [0,11.5]x[0,7.5]);
 *   - “Run feedback” is a method button: its untouched result can earn credit, an edit after it
 *     cancels that credit (the model does this, see moveSelectedTo);
 *   - “Reveal golden (study)” shows the spread placement and never counts;
 *   - challenges also read the learner's TYPED answers, so nothing passes on page load, from the
 *     preset seed, from the reveal, or from one Run feedback click alone.
 * Colours follow R5: t = clamp(cong / maxC) on the paper palette (drawn with paper: true);
 * oversubscription is not a colour boundary.
 */
import {
  CAPACITY,
  drawCongestion,
} from "../../assets/congestion-core.js";
import { createChallengeLab, el, metricsBlock } from "../../assets/clustering-ui.js";
import * as M from "./congestion-map-lab-model.js";

const root = document.getElementById("lab-root");

let state = M.createState();
let lastMsg = "";

/* The shared canvasToChip/hitCell (congestion-core.js) ignore the paper legend that
 * drawCongestion(paper: true) reserves at the bottom, so with the paper palette they would map
 * clicks ~14px off. Map clicks through the draw's own transform instead (canvas.__draw). */
function canvasWorld(canvas, clientX, clientY) {
  const d = canvas.__draw;
  const rect = canvas.getBoundingClientRect();
  const mx = clientX - rect.left;
  const my = clientY - rect.top;
  return { x: (mx - d.ox) / d.scale, y: (d.oy - my) / d.scale, scale: d.scale };
}

function hitCellLocal(positions, canvas, clientX, clientY) {
  const w = canvasWorld(canvas, clientX, clientY);
  let best = null;
  let bestD = 12 / Math.max(w.scale, 1e-9);
  for (const id of M.CELLS) {
    const p = positions[id];
    if (!p) continue;
    const dist = Math.hypot(p.x - w.x, p.y - w.y);
    if (dist <= bestD) {
      bestD = dist;
      best = id;
    }
  }
  return best;
}

function apply(ctx, res) {
  state = res.state;
  lastMsg = res.msg || "";
  ctx.rerender();
}

/* ---------------- controls ---------------- */

function btn(text, cls, onClick) {
  return el("button", { className: `btn ${cls}`, type: "button", text, onClick });
}

function extraActions(ctx) {
  const btns = [];
  for (const id of M.CELLS) {
    btns.push(
      btn(id, state.selected === id ? "btn-primary" : "btn-secondary", () =>
        apply(ctx, M.selectCell(state, id))
      )
    );
  }
  btns.push(
    btn("←", "btn-ghost", () => apply(ctx, M.nudge(state, -0.5, 0))),
    btn("→", "btn-ghost", () => apply(ctx, M.nudge(state, 0.5, 0))),
    btn("↑", "btn-ghost", () => apply(ctx, M.nudge(state, 0, 0.5))),
    btn("↓", "btn-ghost", () => apply(ctx, M.nudge(state, 0, -0.5))),
    btn("Run feedback", "btn-secondary", () => apply(ctx, M.runFeedback(state))),
    btn(state.revealed ? "Hide golden" : "Reveal golden (study)", "btn-ghost", () =>
      apply(ctx, M.toggleReveal(state))
    )
  );
  return btns;
}

/* ---------------- workspace ---------------- */

function viewLine() {
  if (state.revealed) return "view: revealed spread golden (study — never counts)";
  if (M.isMethod(state, "feedback")) return "view: Run feedback result (unchanged since the button)";
  if (state.base) {
    const moved = M.movedSinceMethod(state);
    return `view: your edits of the ${M.methodLabel(state.base.method)} result (${moved ? moved.length : 0} cell(s) moved — its credit is cancelled)`;
  }
  return "view: your placement (built by dragging)";
}

function renderWorkspace(ctx) {
  const s = state;
  const demand = M.demandOf(s);
  const cong = M.congOf(s);
  const ov = M.overflowOf(s);
  const h = M.hottestOf(s);

  // R5 colours: paper palette, t = clamp(cong / maxC) — drawCongestion computes the same t.
  const draw = drawCongestion(ctx.canvas, {
    positions: s.positions,
    heat: cong,
    heatMode: "cong",
    capacity: CAPACITY,
    highlight: [s.selected],
    showNets: true,
    paper: true,
  });
  ctx.canvas.__draw = draw; // { scale, ox, oy, toScreen, cong } — used by the colour tests

  ctx.canvas.onclick = (ev) => {
    const hit = hitCellLocal(s.positions, ctx.canvas, ev.clientX, ev.clientY);
    if (hit && !ev.shiftKey) {
      apply(ctx, M.selectCell(state, hit));
      return;
    }
    const w = canvasWorld(ctx.canvas, ev.clientX, ev.clientY);
    apply(ctx, M.moveSelectedTo(state, w.x, w.y));
  };

  const gc = M.cellGcell(s.positions[s.selected].x, s.positions[s.selected].y);
  const lines = [
    `selected: ${s.selected} @ GCell (${gc.i},${gc.j})`,
    `HPWL: ${M.hpwlOf(s).toFixed(1)}`,
    `overflow total: ${ov.total.toFixed(2)} · max: ${ov.max.toFixed(2)} · count: ${ov.count}`,
    `hottest: (${h.i},${h.j}) @ ${h.v.toFixed(2)}`,
    `capacity: ${CAPACITY}`,
    viewLine(),
  ];

  const box = el("div", { className: "cm-panel" });
  box.append(metricsBlock(lines));

  // typed answers for the active challenge
  const ch = ctx.getChallenge();
  if (ch.fields && ch.fields.length) {
    const form = el("div", { className: "cm-form" });
    form.append(
      el("p", {
        className: "cm-muted",
        text: "Type your answers — they must match YOUR map on screen:",
      })
    );
    for (const f of ch.fields) {
      const inp = el("input", {
        id: `cm-in-${f}`,
        className: "cm-input",
        type: "text",
        value: s.typed[f] ?? "",
        "aria-label": M.FIELD_LABELS[f] || f,
        onInput: (e) => {
          state = M.setTyped(state, f, e.target.value).state; // no rerender: keep the focus
        },
      });
      form.append(el("label", { className: "cm-field" }, [el("span", { text: M.FIELD_LABELS[f] || f }), inp]));
    }
    box.append(form);
  }
  if (lastMsg) box.append(el("p", { className: "cm-msg", text: lastMsg }));

  ctx.metrics.innerHTML = "";
  ctx.metrics.append(box);
}

/* ---------------- mount ---------------- */

createChallengeLab(root, {
  starterButtonLabel: "Reset workspace",
  idlePromptHtml:
    "Pick a challenge and click <strong>Start</strong>. Drag cells and type answers, then <strong>Check</strong>. The reveal is study-only: what it shows never counts.",
  starterHtml: `
    <p><strong>Your workspace:</strong> click a cell to select it, click empty canvas to move it
    (nudge buttons move by 0.5). The heat map paints each GCell with
    <em>t = clamp(congestion / max congestion)</em> on the paper palette — the colour is relative to
    the current hottest tile, so oversubscribed is not a colour boundary.</p>
    <p>Challenges check <em>what you built</em>: your own congestion matrix, your own hottest tile
    under the written tie-break, and peak + total overflow + HPWL bounded together. Nothing passes on
    page load, from the seed alone, from the reveal, or from one <em>Run feedback</em> click alone —
    and editing after a method button cancels that method's credit.</p>
  `,
  challenges: M.CHALLENGES.map((ch) => ({
    id: ch.id,
    title: ch.title,
    level: ch.level,
    prompt: ch.prompt,
    hint: ch.hint,
    fields: ch.fields,
    setup: () => {
      state = M.createState();
      lastMsg = "";
    },
    check: () => M.checkChallenge(state, ch.id),
  })),
  loadStarter() {
    state = M.createState();
    lastMsg = "";
  },
  extraActions,
  renderWorkspace,
});
