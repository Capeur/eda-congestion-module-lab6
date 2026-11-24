/**
 * Congestion heat map — Lab 06 browser lab (UI half).
 *
 * All state, rules and challenge predicates live in the pure model
 * ./congestion-map-lab-model.js (no DOM, tested in Node against the module's checker).
 * This file only draws and wires controls:
 *   - click a cell to select it, click empty canvas to drag it (drag clamp [0,11.5]x[0,7.5]);
 *   - « Lancer la rétroaction » est un bouton de méthode : son résultat intact peut rapporter des points, une édition après
 *     cancels that credit (the model does this, see moveSelectedTo);
 *   - “Reveal golden (study)” shows the spread placement and never counts;
 *   - challenges also read the learner's TYPED answers, so nothing passes on page load, from the
 *     la graine seule, depuis la révélation, ou depuis un seul clic sur Lancer la rétroaction.
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
    btn("Lancer la rétroaction", "btn-secondary", () => apply(ctx, M.runFeedback(state))),
    btn(state.revealed ? "Masquer le golden" : "Révéler le golden (étude)", "btn-ghost", () =>
      apply(ctx, M.toggleReveal(state))
    )
  );
  return btns;
}

/* ---------------- workspace ---------------- */

function viewLine() {
  if (state.revealed) return "vue : golden dispersé révélé (étude — ne compte jamais)";
  if (M.isMethod(state, "feedback")) return "vue : résultat de Lancer la rétroaction (inchangé depuis le bouton)";
  if (state.base) {
    const moved = M.movedSinceMethod(state);
    return `vue : vos éditions du résultat de ${M.methodLabel(state.base.method)} (${moved ? moved.length : 0} cellule(s) déplacée(s) — son crédit est annulé)`;
  }
  return "vue : votre placement (construit en glissant)";
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
        text: "Tapez vos réponses — elles doivent correspondre à VOTRE carte à l'écran :",
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
  starterButtonLabel: "Réinitialiser l'espace de travail",
  idlePromptHtml:
    "Choisissez un défi et cliquez sur <strong>Commencer</strong>. Glissez les cellules et tapez vos réponses, puis <strong>Vérifier</strong>. La révélation est pour l'étude seule : ce qu'elle montre ne compte jamais.",
  starterHtml: `
    <p><strong>Votre espace de travail :</strong> cliquez une cellule pour la sélectionner, cliquez le canevas vide pour la déplacer
    (les boutons de poussée déplacent de 0.5). La carte de chaleur peint chaque GCell avec
    <em>t = clamp(congestion / max congestion)</em> sur la palette papier — la couleur est relative à
    la tuile la plus chaude courante, donc la sursaturation n'est pas une frontière de couleur.</p>
    <p>Les défis vérifient <em>ce que vous avez construit</em> : votre propre matrice de congestion, votre propre tuile la plus chaude
    selon le départage écrit, et pic + débordement total + HPWL bornés ensemble. Rien ne passe au
    chargement de la page, depuis la graine seule, depuis la révélation, ou depuis un seul clic sur <em>Lancer la rétroaction</em> —
    et éditer après un bouton de méthode annule le crédit de cette méthode.</p>
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
