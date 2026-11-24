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

export const methodLabel = (m) => (m && m.kind === "feedback" ? "Run feedback" : m ? m.kind : null);

/* ---------------- learner actions (each returns { state, msg }) ---------------- */

export function selectCell(s, id) {
  if (!CELLS.includes(id)) return { state: s, msg: "" };
  const n = cloneState(s);
  n.selected = id;
  return { state: n, msg: `selected ${id}` };
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
    msg += ` — edit after ${methodLabel(s.method)}: that method's credit is cancelled`;
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
  return { state: n, msg: "Run feedback: one pass pushing cells out of oversubscribed tiles." };
}

/** Study reveal: the spread placement. It never counts for any challenge. */
export function toggleReveal(s) {
  if (s.revealed) {
    const n = cloneState(s);
    n.positions = clonePositions(CONGESTED_SEED);
    n.revealed = false;
    n.method = null;
    n.base = null;
    return { state: n, msg: "Golden hidden; back to the congested seed." };
  }
  const n = cloneState(s);
  n.positions = clonePositions(PLACEMENT);
  n.revealed = true;
  n.method = null;
  n.base = null;
  return { state: n, msg: "Revealed spread placement (study only — it never counts)." };
}

export function reset() {
  return { state: createState(), msg: "Workspace reset to the congested seed." };
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
 * on page load, from the preset seed alone, from the reveal, or from one Run feedback click alone:
 *   seed    cong (1,0)=3.5, ov total 5 count 1, hottest (1,0), HPWL 7
 *   reveal  spread: hottest (2,0)@3.33, ov total 22 count 6, HPWL 34 — and revealed=true
 *   feedback once from the seed: ov total 0 count 0, hottest (2,0) @ exactly 1.0 (cooled, not
 *           cold), HPWL 3.5 — but it is a method result, and feedback-cooled also needs typed answers
 */

export const FIELD_LABELS = {
  hotTile: "hottest tile (i,j)",
  hotVal: "its congestion",
  tile10: "congestion at tile (1,0)",
  tile20: "congestion at tile (2,0)",
  tieTile: "tile the R2 rule picks (i,j)",
  fbTotal: "total overflow after the pass",
  fbTile: "hottest tile (i,j) after the pass",
  fbVal: "its congestion",
};

export const CHALLENGES = [
  {
    id: "read-hot",
    title: "Read the hottest tile of your map",
    level: "Intro",
    fields: ["hotTile", "hotVal"],
    prompt:
      "Type the hottest tile of YOUR current map as i,j and its congestion (2 decimals). Rule R2 decides: scan columns i outer, rows j inner, strict greater — the first maximum wins. The map must have a tile above 1.",
    hint: "The seed lights tile (1,0) at 3.5. The typed numbers must match the map on screen, not a golden.",
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
    title: "Type two tiles of your own matrix",
    level: "Intro",
    fields: ["tile10", "tile20"],
    prompt:
      "Type the congestion (demand / capacity) of tile (1,0) and of tile (2,0) on YOUR current map, 2 decimals. Then move a cell and watch these change — the check always reads the map on screen.",
    hint: "On the seed all demand sits in tile (1,0): 7 over capacity 2 = 3.5, and tile (2,0) is 0.",
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
    title: "Drag A across the boundary x=6",
    level: "Practice",
    fields: [],
    prompt:
      "Move cell A BY HAND (click A, then click the canvas at (6.5, 2)) across the GCell boundary x=6. The oversubscribed count must become 2 with total overflow 7.5 and the hottest tile still in column 1. No method button.",
    hint: "With A at (6.5,2) the nets AB, AC and ABCD spill into tile (2,0) as well: count 2, total 7.5, hottest (1,0) at 3.625.",
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
    title: "Build a tie, name the R2 winner",
    level: "Practice",
    fields: ["tieTile"],
    prompt:
      "Build BY HAND a placement where at least two tiles tie for the maximum congestion. Type the tile the written rule R2 picks: scan i (columns) outer, j (rows) inner, strict greater — the first maximum in that scan order wins.",
    hint: "Symmetric works: A(2,2) B(4,2) C(2,6) D(4,6) E(3,4) F(3,4) — all four tiles end at congestion 2.25, so R2 picks (0,0), not the last one.",
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
    title: "Cool the peak to 3 (by hand)",
    level: "Practice",
    fields: [],
    prompt:
      "Move cells BY HAND (no method button, no reveal) so the hottest tile of your map is at most 3.0 — and at least one tile must still be oversubscribed (count >= 1), so an empty map does not count.",
    hint: "The seed is at 3.5. Spread the four big cells over both middle columns: A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) gives hottest 2.5.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      const ov = overflowOf(s);
      return h.v <= 3 + TOL && ov.count >= 1;
    },
  },
  {
    id: "cool-2",
    title: "Cooler: peak 2.5 and total overflow 6",
    level: "Practice",
    fields: [],
    prompt:
      "BY HAND: hottest tile at most 2.5, total overflow at most 6, and at least one tile still oversubscribed (count >= 1) so an empty map does not count. Spreading lowers the peak but raises the total — the bounds must hold on your map at once.",
    hint: "The spread golden lowers the peak only to 3.33 and its total is 22. The placement A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) gives peak 2.5, total 6, count 2.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      const ov = overflowOf(s);
      return h.v <= 2.5 + TOL && ov.total <= 6 + TOL && ov.count >= 1;
    },
  },
  {
    id: "edge-hot",
    title: "Move the hotspot to an edge column",
    level: "Challenge",
    fields: [],
    prompt:
      "BY HAND: make the hottest tile of your map sit in an edge column (i=0 or i=3), still above 1, with total HPWL at least 8. No method button, no reveal.",
    hint: "Push E and F to the left edge next to the spread golden: A(1,1) B(8,1) C(1,5) D(8,5) E(1,3) F(2,3) makes tile (0,0) the hottest at 3.58 with HPWL 34.",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      return (h.i === 0 || h.i === GCELL_NX - 1) && h.v > 1 + TOL && hpwlOf(s) >= 8 - TOL;
    },
  },
  {
    id: "joint-bound",
    title: "Peak + total + HPWL bounded together",
    level: "Challenge",
    fields: [],
    prompt:
      "BY HAND, all three at once on your map: hottest tile at most 3.0, total overflow at most 6, AND total HPWL at least 8 (so collapsing all cells into one point does not count). No method button.",
    hint: "A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5): peak 2.5, total overflow 6, HPWL 10. The seed fails the peak, the spread golden fails the total, one feedback pass is a method result (and HPWL 3.5).",
    check: (s) => {
      if (!handOnly(s)) return false;
      const h = hottestOf(s);
      const ov = overflowOf(s);
      return h.v <= 3 + TOL && ov.total <= 6 + TOL && hpwlOf(s) >= 8 - TOL;
    },
  },
  {
    id: "feedback-cooled",
    title: "Run feedback, read the cooled map",
    level: "Challenge",
    fields: ["fbTotal", "fbTile", "fbVal"],
    prompt:
      "Click “Run feedback” ONCE from the seed and leave the result untouched. Type its total overflow, its hottest tile (i,j) and that tile's congestion. Cooled, not cold: the hottest tile sits at exactly 1.0, right at capacity.",
    hint: "One pass from the seed zeroes the total overflow but the hottest tile is (2,0) at exactly 1.0 — not below. Editing after the button cancels its credit, so do not touch the cells.",
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
