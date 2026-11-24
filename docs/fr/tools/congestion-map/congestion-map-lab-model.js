/**
 * congestion-map-lab-model.js — the pure model of the Lab 06 congestion-map browser lab.
 * No DOM, so Node can test it against the module's checker:
 *   courses/learn_congestion/module02-05-congestion-map/examples/congestion_map_check.py
 *
 * The numeric core is imported READ-ONLY from ../../assets/congestion-core.js (the checker's
 * --vs-node proved it bit-equal to the Python reference). The written rules R1–R7 of the checker:
 *   R1 rounding: checks on raw floats with tol 1e-9; typed answers are accepted within 2-decimal
 *      display precision (DISP_TOL = 0.005); --json rounds to 12 significant digits.
 *   R2 argmax tie-break: scan i (columns) OUTER, j (rows) INNER, strict > — the FIRST maximum in
 *      row-major order wins (hottest() in congestion-core.js implements exactly this).
 *   R3 RUDY fill order: nets in NETS order; per net the bbox tiles (cellGcell-clamped) filled
 *      i-outer / j-inner; each tile gets hpwl / max(1, #tiles); demand accumulates in that order.
 *   R4 feedback: neighbours tried (+1,0), (-1,0), (0,+1), (0,-1), strict <, midpoint toward the
 *      target tile centre, clamped to the chip [0,11]x[0,7] (chip-1, NOT the drag clamp).
 *   R5 heat colours: t = clamp(cong / maxC, 0, 1) with maxC = max congestion of the CURRENT map
 *      (maxC = 0 -> t = 0). Oversubscription (> 1) is NOT a colour boundary. Paper palette stops
 *      u = 0, 1/3, 2/3, 1 -> #ffffff, #0f6b5c, #b45309, #9f1239, alpha 0.15 + 0.7u.
 *      congestion-core.js does not export its heatColor (teacher-list item), so it is copied here.
 *   R6 cellGcell clamps out-of-chip coordinates into the edge GCell.
 *   R7 overflow: perCell = max(0, demand - capacity); count = #tiles with perCell > 0 (strict).
 *
 * Learner state (what the challenges read on every Check):
 *   positions  the placement on screen (the learner builds it by dragging cells)
 *   selected   the cell the next canvas click / nudge moves
 *   method     the method button whose result is on screen, or null once the learner edits it
 *   base       { method, positions } snapshot taken when the method button ran
 *   revealed   the study reveal (spread placement) is showing — never counts for anything
 *   typed      the learner's typed answers (field key -> string)
 * A manual move cancels the method's credit: method = null, base stays, so the map is neither a
 * pure hand-built map (handOnly) nor the method's untouched result (isMethod).
 */
import {
  CAPACITY,
  CELLS,
  NETS,
  CHIP_W,
  CHIP_H,
  GCELL_NX,
  GCELL_NY,
  CELL_W,
  CELL_H,
  CONGESTED_SEED,
  PLACEMENT,
  clonePositions,
  cellGcell,
  congestionMap,
  overflowMetrics,
  hottest,
  rudyDemand,
  totalHpwl,
  placementFeedbackLite,
} from "../../assets/congestion-core.js";

export {
  CAPACITY, CELLS, NETS, CHIP_W, CHIP_H, GCELL_NX, GCELL_NY, CELL_W, CELL_H,
  CONGESTED_SEED, PLACEMENT, clonePositions, cellGcell,
};

/** R1: raw-float tolerance for checks. */
export const TOL = 1e-9;
/** R1: typed answers are read at 2-decimal display precision, so allow half a display unit. */
export const DISP_TOL = 0.005 + 1e-9;
/** The interactive drag clamp (interactive-congestion-lab.js moveSelectedTo: CHIP - 0.5). */
export const DRAG_CLAMP = { x: [0, CHIP_W - 0.5], y: [0, CHIP_H - 0.5] };

const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

/* ---------------- state ---------------- */

export function createState() {
  return {
    positions: clonePositions(CONGESTED_SEED),
    selected: CELLS[0],
    method: null,
    base: null,
    revealed: false,
    typed: {},
  };
}

export const cloneState = (s) => JSON.parse(JSON.stringify(s));

export const methodLabel = (m) => (m && m.kind === "feedback" ? "Lancer la rétroaction" : m ? m.kind : null);

/* ---------------- learner actions (each returns { state, msg }) ---------------- */

export function selectCell(s, id) {
  if (!CELLS.includes(id)) return { state: s, msg: "" };
  const n = cloneState(s);
  n.selected = id;
  return { state: n, msg: `sélectionnée ${id}` };
}

/**
 * Manual move of the selected cell to chip point (wx, wy), drag-clamped to [0, 11.5] x [0, 7.5].
 * An edit after a method button cancels that method's credit (method -> null, base kept).
 */
export function moveSelectedTo(s, wx, wy) {
  const n = cloneState(s);
  const id = n.selected;
  if (!n.positions[id]) return { state: s, msg: "" };
  n.positions[id] = {
    x: clamp(wx, DRAG_CLAMP.x[0], DRAG_CLAMP.x[1]),
    y: clamp(wy, DRAG_CLAMP.y[0], DRAG_CLAMP.y[1]),
  };
  let msg = `${id} -> (${n.positions[id].x.toFixed(2)}, ${n.positions[id].y.toFixed(2)})`;
  if (s.method) {
    n.method = null; // editing after a method button cancels that method's credit
    msg += ` — édition après ${methodLabel(s.method)} : le crédit de cette méthode est annulé`;
  }
  return { state: n, msg };
}

export function nudge(s, dx, dy) {
  const p = s.positions[s.selected];
  return moveSelectedTo(s, p.x + dx, p.y + dy);
}

/** Method button: one placementFeedbackLite pass (R4, feedback clamp [0,11]x[0,7]). */
export function runFeedback(s) {
  const n = cloneState(s);
  n.positions = placementFeedbackLite(n.positions, CAPACITY);
  n.revealed = false;
  n.method = { kind: "feedback" };
  n.base = { method: { kind: "feedback" }, positions: clonePositions(n.positions) };
  return { state: n, msg: "Lancer la rétroaction : une passe qui pousse les cellules hors des tuiles sursaturées." };
}

/** Study reveal: the spread placement. It never counts for any challenge. */
export function toggleReveal(s) {
  if (s.revealed) {
    const n = cloneState(s);
    n.positions = clonePositions(CONGESTED_SEED);
    n.revealed = false;
    n.method = null;
    n.base = null;
    return { state: n, msg: "Golden masqué ; retour à la graine encombrée." };
  }
  const n = cloneState(s);
  n.positions = clonePositions(PLACEMENT);
  n.revealed = true;
  n.method = null;
  n.base = null;
  return { state: n, msg: "Placement dispersé révélé (étude seule — il ne compte jamais)." };
}

export function reset() {
  return { state: createState(), msg: "Espace de travail réinitialisé à la graine encombrée." };
}

/** Typed answer for a challenge field (no rerender needed). */
export function setTyped(s, key, value) {
  const n = cloneState(s);
  n.typed[key] = String(value);
  return { state: n, msg: "" };
}

/** Helper for tests / scenario setup: set the whole placement. NOT exposed in the UI. */
export function setPositions(s, pos) {
  const n = cloneState(s);
  n.positions = clonePositions(pos);
  n.method = null;
  return { state: n, msg: "" };
}

/* ---------------- derived quantities (the learner's own map) ---------------- */

export const demandOf = (s) => rudyDemand(s.positions, NETS);
export const congOf = (s) => congestionMap(demandOf(s), CAPACITY);
export const overflowOf = (s) => overflowMetrics(demandOf(s), CAPACITY);
export const hpwlOf = (s) => totalHpwl(s.positions, NETS);
export const hottestOf = (s) => hottest(congOf(s));

/* ---------------- R5 heat ---------------- */

/** Per-tile t = clamp(cong / maxC, 0, 1); maxC = 0 -> all t = 0. Oversubscription is not a boundary. */
export function heatT(cong) {
  let maxC = 0;
  for (const col of cong) for (const v of col) if (v > maxC) maxC = v;
  return cong.map((col) => col.map((v) => (maxC > 0 ? clamp(v / maxC, 0, 1) : 0)));
}

const PAPER_STOPS = [
  [255, 255, 255], // #ffffff
  [15, 107, 92],   // #0f6b5c
  [180, 83, 9],    // #b45309
  [159, 18, 57],   // #9f1239
];

/** Same formula as congestion-core.js heatColor(paper=true) (not exported there): segment
 *  i = min(2, floor(3u)), f = 3u - i, RGB lerped between stops, alpha 0.15 + 0.7u. */
export function heatColor(t) {
  const u = clamp(t, 0, 1);
  const x = u * (PAPER_STOPS.length - 1);
  const i = Math.min(PAPER_STOPS.length - 2, Math.floor(x));
  const f = x - i;
  const a = PAPER_STOPS[i];
  const b = PAPER_STOPS[i + 1];
  const r = Math.round(a[0] + (b[0] - a[0]) * f);
  const g = Math.round(a[1] + (b[1] - a[1]) * f);
  const bl = Math.round(a[2] + (b[2] - a[2]) * f);
  const alpha = 0.15 + 0.7 * u;
  return { r, g, b: bl, a: alpha, css: `rgba(${r},${g},${bl},${alpha})` };
}

/* ---------------- predicates on the learner state ---------------- */

const samePos = (a, b) => CELLS.every((id) => a[id] && b[id] && a[id].x === b[id].x && a[id].y === b[id].y);

/** Built by dragging only: no method button ever ran since Start/Reset, nothing revealed. */
export const handOnly = (s) => !s.base && !s.revealed && !s.method;

/** The method's untouched result is on screen (an edit cancels this). */
export function isMethod(s, kind) {
  const m = s.method;
  if (!m || m.kind !== kind || s.revealed || !s.base) return false;
  return samePos(s.positions, s.base.positions);
}

/** Cells the learner moved since the method button ran. */
export function movedSinceMethod(s) {
  if (!s.base) return null;
  return CELLS.filter((id) => !s.base.positions[id] || s.positions[id].x !== s.base.positions[id].x || s.positions[id].y !== s.base.positions[id].y);
}

export const parseNum = (v) => {
  const t = String(v ?? "").trim();
  if (!t) return null; // empty input is not a 0
  const x = Number(t.replace(",", "."));
  return Number.isFinite(x) ? x : null;
};

/** "1,0" / "1 0" / "1;0" -> [1, 0], else null. */
export function parseIJ(v) {
  const m = String(v ?? "").trim().match(/^(-?\d+)[,\s;]+(-?\d+)$/);
  return m ? [Number(m[1]), Number(m[2])] : null;
}

/* ---------------- challenges ----------------
 * Every check reads what the learner BUILT (their own positions / typed answers). Nothing passes
 * au chargement de la page, depuis la graine seule, depuis la révélation, ou depuis un seul clic sur Lancer la rétroaction :
 *   seed    cong (1,0)=3.5, ov total 5 count 1, hottest (1,0), HPWL 7
 *   reveal  spread: hottest (2,0)@3.33, ov total 22 count 6, HPWL 34 — and revealed=true
 *   feedback once from the seed: ov total 0 count 0, hottest (2,0) @ exactly 1.0 (cooled, not
 *           cold), HPWL 3.5 — but it is a method result, and feedback-cooled also needs typed answers
 */

export const FIELD_LABELS = {
  hotTile: "tuile la plus chaude (i,j)",
  hotVal: "sa congestion",
  tile10: "congestion de la tuile (1,0)",
  tile20: "congestion de la tuile (2,0)",
  tieTile: "tuile choisie par la règle R2 (i,j)",
  fbTotal: "débordement total après la passe",
  fbTile: "tuile la plus chaude (i,j) après la passe",
  fbVal: "sa congestion",
};

export const CHALLENGES = [
  {
    id: "read-hot",
    title: "Lisez la tuile la plus chaude de votre carte",
    level: "Initiation",
    fields: ["hotTile", "hotVal"],
    prompt:
      "Tapez la tuile la plus chaude de VOTRE carte courante en i,j et sa congestion (2 décimales). La règle R2 décide : balayage des colonnes i externe, des lignes j interne, strictement supérieur — le premier maximum gagne. La carte doit avoir une tuile au-dessus de 1.",
    hint: "La graine allume la tuile (1,0) à 3.5. Les nombres tapés doivent correspondre à la carte à l'écran, pas à une référence.",
    check: (s) => {
      if (s.revealed) return false;
      const h = hottestOf(s);
      if (!(h.v > 1 + TOL)) return false;
      const ij = parseIJ(s.typed.hotTile);
      if (!ij || ij[0] !== h.i || ij[1] !== h.j) return false;
      const v = parseNum(s.typed.hotVal);
      return v !== null && Math.abs(v - h.v) <= DISP_TOL;
    },
  },
  {
    id: "own-matrix",
    title: "Tapez deux tuiles de votre propre matrice",
    level: "Initiation",
    fields: ["tile10", "tile20"],
    prompt:
      "Tapez la congestion (demande / capacité) des tuiles (1,0) et (2,0) sur VOTRE carte courante, à 2 décimales. Puis déplacez une cellule et regardez changer ces valeurs — la vérification lit toujours la carte à l'écran.",
    hint: "Sur la graine toute la demande est dans la tuile (1,0) : 7 sur capacité 2 = 3.5, et la tuile (2,0) vaut 0.",
    check: (s) => {
      if (s.revealed) return false;
      const cong = congOf(s);
      const a = parseNum(s.typed.tile10);
      const b = parseNum(s.typed.tile20);
      return (
        a !== null && b !== null &&
        Math.abs(a - cong[1][0]) <= DISP_TOL && Math.abs(b - cong[2][0]) <= DISP_TOL
      );
    },
  },
  {
    id: "boundary-drag",
    title: "Glissez A à travers la frontière x=6",
    level: "Exercice",
    fields: [],
    prompt:
      "Déplacez la cellule A À LA MAIN (cliquez A, puis cliquez le canevas en (6.5, 2)) à travers la frontière de GCell x=6. Le compte de sursaturées doit devenir 2 avec un débordement total de 7.5 et la tuile la plus chaude toujours dans la colonne 1. Pas de bouton de méthode.",
    hint: "Avec A en (6.5,2), les réseaux AB, AC et ABCD débordent aussi dans la tuile (2,0) : compte 2, total 7.5, plus chaude (1,0) à 3.625.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const ov = overflowOf(s);
      const h = hottestOf(s);
      return (
        s.positions.A.x > 6 &&
        ov.count === 2 &&
        Math.abs(ov.total - 7.5) <= 0.45 &&
        h.i === 1 && Math.abs(h.v - 3.625) <= 0.2
      );
    },
  },
  {
    id: "tie-break",
    title: "Construisez un ex aequo, nommez le gagnant R2",
    level: "Exercice",
    fields: ["tieTile"],
    prompt:
      "Construisez À LA MAIN un placement où au moins deux tuiles sont à égalité pour la congestion maximale. Tapez la tuile choisie par la règle écrite R2 : balayage de i (colonnes) externe, j (lignes) interne, strictement supérieur — le premier maximum dans cet ordre de balayage gagne.",
    hint: "Le symétrique marche : A(2,2) B(4,2) C(2,6) D(4,6) E(3,4) F(3,4) — les quatre tuiles finissent à congestion 2.25, donc R2 choisit (0,0), pas la dernière.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const cong = congOf(s);
      let maxC = 0;
      for (const col of cong) for (const v of col) if (v > maxC) maxC = v;
      if (maxC <= 0) return false;
      let tied = 0;
      for (const col of cong) for (const v of col) if (Math.abs(v - maxC) <= TOL) tied++;
      if (tied < 2) return false;
      const h = hottestOf(s); // hottest() is R2: first max in row-major order
      const ij = parseIJ(s.typed.tieTile);
      return !!ij && ij[0] === h.i && ij[1] === h.j;
    },
  },
  {
    id: "cool-max",
    title: "Refroidissez le pic à 3 (à la main)",
    level: "Exercice",
    fields: [],
    prompt:
      "Déplacez des cellules À LA MAIN (pas de bouton de méthode, pas de révélation) pour que la tuile la plus chaude de votre carte soit au plus 3.0 — et au moins une tuile doit rester sursaturée (compte >= 1), donc une carte vide ne compte pas.",
    hint: "La graine est à 3.5. Étalez les quatre grosses cellules sur les deux colonnes du milieu : A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) donne une plus chaude à 2.5.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      const ov = overflowOf(s);
      return h.v <= 3 + TOL && ov.count >= 1;
    },
  },
  {
    id: "cool-2",
    title: "Plus frais : pic 2.5 et débordement total 6",
    level: "Exercice",
    fields: [],
    prompt:
      "À LA MAIN : tuile la plus chaude au plus 2.5, débordement total au plus 6, et au moins une tuile encore sursaturée (compte >= 1) pour qu'une carte vide ne compte pas. La dispersion abaisse le pic mais augmente le total — les bornes doivent tenir sur votre carte en même temps.",
    hint: "Le golden dispersé n'abaisse le pic qu'à 3.33 et son total vaut 22. Le placement A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) donne pic 2.5, total 6, compte 2.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      const ov = overflowOf(s);
      return h.v <= 2.5 + TOL && ov.total <= 6 + TOL && ov.count >= 1;
    },
  },
  {
    id: "edge-hot",
    title: "Mettez le point chaud sur une colonne de bord",
    level: "Défi",
    fields: [],
    prompt:
      "À LA MAIN : que la tuile la plus chaude de votre carte soit dans une colonne de bord (i=0 ou i=3), toujours au-dessus de 1, avec un HPWL total d'au moins 8. Pas de bouton de méthode, pas de révélation.",
    hint: "Poussez E et F sur le bord gauche à côté du golden dispersé : A(1,1) B(8,1) C(1,5) D(8,5) E(1,3) F(2,3) rend la tuile (0,0) la plus chaude à 3.58 avec HPWL 34.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      return (h.i === 0 || h.i === GCELL_NX - 1) && h.v > 1 + TOL && hpwlOf(s) >= 8 - TOL;
    },
  },
  {
    id: "joint-bound",
    title: "Pic + total + HPWL bornés ensemble",
    level: "Défi",
    fields: [],
    prompt:
      "À LA MAIN, les trois en même temps sur votre carte : tuile la plus chaude au plus 3.0, débordement total au plus 6, ET HPWL total d'au moins 8 (donc tout concentrer en un point ne compte pas). Pas de bouton de méthode.",
    hint: "A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) : pic 2.5, débordement total 6, HPWL 10. La graine échoue sur le pic, le golden dispersé sur le total, une passe de rétroaction est un résultat de méthode (et HPWL 3.5).",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      const ov = overflowOf(s);
      return h.v <= 3 + TOL && ov.total <= 6 + TOL && hpwlOf(s) >= 8 - TOL;
    },
  },
  {
    id: "feedback-cooled",
    title: "Lancez la rétroaction, lisez la carte refroidie",
    level: "Défi",
    fields: ["fbTotal", "fbTile", "fbVal"],
    prompt:
      "Cliquez UNE FOIS sur « Lancer la rétroaction » depuis la graine et ne touchez plus au résultat. Tapez son débordement total, sa tuile la plus chaude (i,j) et la congestion de cette tuile. Refroidie, pas froide : la tuile la plus chaude est à exactement 1.0, pile à la capacité.",
    hint: "Une passe depuis la graine annule le débordement total mais la tuile la plus chaude est (2,0) à exactement 1.0 — pas en dessous. Éditer après le bouton annule son crédit, donc ne touchez pas aux cellules.",
    check: (s) => {
      if (!isMethod(s, "feedback")) return false;
      const ov = overflowOf(s);
      const h = hottestOf(s);
      if (Math.abs(ov.total) > TOL) return false;
      if (Math.abs(h.v - 1) > TOL) return false; // cooled, not cold
      const t = parseIJ(s.typed.fbTile);
      const tot = parseNum(s.typed.fbTotal);
      const v = parseNum(s.typed.fbVal);
      return (
        !!t && t[0] === h.i && t[1] === h.j &&
        tot !== null && Math.abs(tot - ov.total) <= DISP_TOL &&
        v !== null && Math.abs(v - h.v) <= DISP_TOL
      );
    },
  },
];

export function checkChallenge(s, id) {
  const ch = CHALLENGES.find((c) => c.id === id);
  return ch ? !!ch.check(s) : false;
}

/** Every challenge's predicate on a state (used by the Node model test). */
export function checkAll(s) {
  return Object.fromEntries(CHALLENGES.map((c) => [c.id, !!c.check(s)]));
}
