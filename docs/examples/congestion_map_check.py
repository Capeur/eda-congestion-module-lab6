#!/usr/bin/env python3
"""Golden self-check for module02-05 congestion heat map (Track A).

    python3 examples/congestion_map_check.py                    # check every examples/*.json (all tables)
    python3 examples/congestion_map_check.py --show             # print the rules and every table
    python3 examples/congestion_map_check.py --instance examples/cap_one.json
    python3 examples/congestion_map_check.py --impl my_cong.py  # check YOUR functions
    python3 examples/congestion_map_check.py --vs-node          # bit-for-bit vs platform/assets/congestion-core.js
    python3 examples/congestion_map_check.py --json             # the lesson replay file (see --help / §0.4 of UPGRADE_NOTES.md)
    python3 examples/congestion_map_check.py --dump-goldens     # regenerate the GOLDENS block below (after a deliberate core change)

Your file may define any of (same signatures as common/solvers.py, so you can compare):
    cell_gcell(x, y, nx, ny, cell_w, cell_h)          -> (i, j)
    net_bbox(net, positions)                          -> (x0, y0, x1, y1)
    hpwl(net, positions)                              -> float
    deposit_events(positions, data)                   -> [{net, pins, bbox, hpwl, tiles, share}, ...] in fill order
    rudy_demand(positions, data)                      -> demand matrix [i][j]
    congestion_map(demand, capacity)                  -> matrix [i][j]
    overflow_metrics(demand, capacity)                -> {"perCell", "total", "max", "count"}
    hottest(cong)                                     -> (i, j, v)
    placement_feedback_lite(positions, data)          -> new positions dict
`positions` is {cell: {"x", "y"}}, `data` is the instance dict loaded from an examples/*.json file.
Functions you have not written yet are reported as SKIP. Never change the positions, nets or data you are given.

DETERMINISM: this module is fully deterministic — every position comes from the instance file and nothing in the
pipeline draws a random number — so NO PRNG is needed and none is used anywhere in this checker. Python and
JavaScript therefore agree BIT-FOR-BIT per cell (not just within a tolerance): see --vs-node, which imports the real
platform/assets/congestion-core.js and compares every demand / congestion / overflow cell with ==.

THE RULES (written exactly, because the course code never wrote them down)
    R1  rounding. Checks compare raw floats with abs tol 1e-9. Display uses 2 decimals, round-half-even (Python
        `format`; never compare JS `toFixed` strings). --json rounds every float to 12 significant digits so the
        JS and Python files agree. NOTE: JS `total += v` and Python `sum()` differ in the last ulp (CPython >= 3.12
        compensates), so this checker accumulates `total` with an explicit loop, exactly like the JS.
    R2  argmax tie-break (hottest). Scan i (columns) outer, j (rows) inner, strict `>`: the FIRST maximum in
        row-major order wins. All-zeros (or empty) matrix -> (0, 0) with v = its value (0 for all-zeros; init -1).
    R3  RUDY fill order. Nets in `nets` file order. Per net: bbox from the positioned pins, tiles = the GCells of
        the bbox corners (clamped, min/max normalized) filled i-outer / j-inner; each tile gets
        share = hpwl / max(1, #tiles); demand accumulates in that order (float addition order matters in the last ulp).
    R4  feedback neighbour order. Neighbours tried in order (+1,0), (-1,0), (0,+1), (0,-1), strict `<`: the first
        strictly-smaller overflow wins, else the cell stays. Cells are processed in positions-dict insertion order
        (A..F) — the result is order-independent because the overflow map is computed once, before the loop.
        Move = midpoint toward the chosen tile centre, clamped by the FEEDBACK clamp (see below).
    R5  colour thresholds (heat). t = clamp(cong / maxC, 0, 1) — relative to the CURRENT map max, NOT to capacity;
        oversubscribed (> 1) is not a colour boundary. maxC = max cong (0 -> t = 0 everywhere). Paper palette stops
        at u = 0, 1/3, 2/3, 1 -> #ffffff, #0f6b5c, #b45309, #9f1239; segment i = min(2, floor(3u)), f = 3u - i,
        RGB lerped between stops; alpha = 0.15 + 0.7u. (Screen palette: linear rgb(40+200u, 180-140u, 80-40u),
        alpha 0.55.) heatColor is not exported from congestion-core.js — these thresholds are pinned HERE.
    R6  cellGcell clamp. i = clamp(floor(x / cellW), 0, nx-1), same for j: out-of-chip coordinates clamp into the
        edge GCell, e.g. (12, 8) -> (3, 1) and (-1, -1) -> (0, 0) on the 4x2 grid.
    R7  overflow. perCell = max(0, demand - capacity); count = #cells with perCell > 0 (STRICT — a tile at exactly
        capacity has overflow 0 and does not count); max init 0; total = sum in scan order (see R1).

THE TWO IN-CHIP CLAMP RULES — kept AS WRITTEN, tested AS WRITTEN, NOT unified silently:
    DRAG clamp (interactive use): x in [0, 11.5], y in [0, 7.5] — hard-coded literals in
        platform/assets/interactive-congestion-lab.js `moveSelectedTo` (Math.min(11.5, wx) / Math.min(7.5, wy),
        i.e. CHIP - 0.5). Tested by the `drag_clamp` probe below and by --vs-node (the helper reads the literals
        from the real lab file).
    FEEDBACK clamp (placementFeedbackLite): x in [0, chip-1] = [0, 11], y in [0, chip-1] = [0, 7] —
        Math.min(CHIP_W - 1, ...) in congestion-core.js. Tested by the fb_clamp_x / fb_clamp_y probes, which put a
        cell outside the chip so the midpoint overshoots and the clamp bites: F (15, 2.5) -> (11, 4.25) and
        F (4.5, 20) -> (6, 7).
    They are different rules (11.5/7.5 vs 11/7); the checker keeps two separate code paths for them.

Standard library only; runs with `python3` from the module folder (paths are resolved from __file__, so any cwd
works). --vs-node needs `node` and the clone's platform/. Set PYTHONDONTWRITEBYTECODE=1 so common/ stays clean.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # do not leave __pycache__ in common/
HERE = Path(__file__).resolve().parent
MODULE = HERE.parent
COURSE = MODULE.parent
ROOT = HERE.parents[3]  # the clone root (courses/learn_congestion/<module>/examples -> up 3)
CORE_JS = ROOT / "platform" / "assets" / "congestion-core.js"
LAB_JS = ROOT / "platform" / "assets" / "interactive-congestion-lab.js"
NODE_HELPER = HERE / "cong_node.mjs"

TOL = 1e-9  # R1
KNOWN_KEYS = {"chip", "gcell", "capacity", "cells", "nets", "notes", "sweep", "widths"}

PAPER_STOPS = [  # R5
    {"u": 0.0, "hex": "#ffffff", "rgb": [255, 255, 255]},
    {"u": 1.0 / 3.0, "hex": "#0f6b5c", "rgb": [15, 107, 92]},
    {"u": 2.0 / 3.0, "hex": "#b45309", "rgb": [180, 83, 9]},
    {"u": 1.0, "hex": "#9f1239", "rgb": [159, 18, 57]},
]


# ---------------- the reference implementation (the written rules R1-R7) ----------------
def cell_gcell(x, y, nx, ny, cell_w, cell_h):
    """R6: clamp(floor(x/cellW), 0, nx-1), same for j."""
    i = math.floor(x / cell_w)
    j = math.floor(y / cell_h)
    return max(0, min(nx - 1, i)), max(0, min(ny - 1, j))


def net_bbox(net, positions):
    xs = [float(positions[c]["x"]) for c in net if c in positions]
    ys = [float(positions[c]["y"]) for c in net if c in positions]
    return min(xs), min(ys), max(xs), max(ys)


def hpwl(net, positions):
    x0, y0, x1, y1 = net_bbox(net, positions)
    return (x1 - x0) + (y1 - y0)


def tiles_for_bbox(x0, y0, x1, y1, nx, ny, cw, ch):
    """R3: bbox corners -> GCells (clamped), min/max normalized, filled i-outer / j-inner."""
    i0, j0 = cell_gcell(x0, y0, nx, ny, cw, ch)
    i1, j1 = cell_gcell(x1, y1, nx, ny, cw, ch)
    i0, i1 = min(i0, i1), max(i0, i1)
    j0, j1 = min(j0, j1), max(j0, j1)
    return [(i, j) for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)]


def geom(data):
    g = data["gcell"]
    return int(g["nx"]), int(g["ny"]), float(g["cellW"]), float(g["cellH"])


def zeros(nx, ny):
    return [[0.0 for _ in range(ny)] for _ in range(nx)]


def clone_positions(pos):
    return {k: {"x": float(v["x"]), "y": float(v["y"])} for k, v in pos.items()}


def deposit_events(positions, data):
    """R3: one ordered event per net; demand accumulates in fill order. Returns (events, demand)."""
    nx, ny, cw, ch = geom(data)
    demand = zeros(nx, ny)
    events = []
    for idx, net in enumerate(data["nets"]):
        x0, y0, x1, y1 = net_bbox(net, positions)
        wl = hpwl(net, positions)
        tiles = tiles_for_bbox(x0, y0, x1, y1, nx, ny, cw, ch)
        share = wl / max(1, len(tiles))
        for i, j in tiles:
            demand[i][j] += share
        events.append({
            "net": idx, "pins": list(net), "bbox": [x0, y0, x1, y1], "hpwl": wl,
            "tiles": [[i, j] for i, j in tiles], "share": share,
            "demandAfter": [row[:] for row in demand],
        })
    return events, demand


def rudy_demand(positions, data):
    return deposit_events(positions, data)[1]


def congestion_map(demand, capacity):
    return [[float(d) / capacity for d in col] for col in demand]


def overflow_metrics(demand, capacity):
    """R7 (and R1: total accumulated with an explicit loop, in JS scan order, for bit-equality)."""
    per_cell = [[max(0.0, float(d) - capacity) for d in col] for col in demand]
    total = 0.0
    mx = 0.0
    count = 0
    for col in per_cell:
        for v in col:
            total += v
            if v > mx:
                mx = v
            if v > 0:
                count += 1
    return {"perCell": per_cell, "total": total, "max": mx, "count": count}


def hottest(cong):
    """R2: scan i outer, j inner, strict >; first max in row-major order wins; init (0, 0, -1)."""
    best = (0, 0, -1.0)
    for i, col in enumerate(cong):
        for j, v in enumerate(col):
            if v > best[2]:
                best = (i, j, float(v))
    return best


def placement_feedback_lite(positions, data):
    """R4 + the FEEDBACK clamp [0, chip-1]x[0, chip-1] (NOT the drag clamp — see header)."""
    nx, ny, cw, ch = geom(data)
    cap = float(data["capacity"])
    chip_w = float(data["chip"]["W"])
    chip_h = float(data["chip"]["H"])
    demand = rudy_demand(positions, data)
    ov = overflow_metrics(demand, cap)["perCell"]
    out = clone_positions(positions)
    for cid, p in list(out.items()):
        i, j = cell_gcell(p["x"], p["y"], nx, ny, cw, ch)
        if ov[i][j] <= 0:
            continue
        best = (i, j, ov[i][j])
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):  # R4 order, strict <
            ni, nj = i + di, j + dj
            if 0 <= ni < nx and 0 <= nj < ny and ov[ni][nj] < best[2]:
                best = (ni, nj, ov[ni][nj])
        tx = (best[0] + 0.5) * cw
        ty = (best[1] + 0.5) * ch
        out[cid] = {
            "x": max(0.0, min(chip_w - 1.0, 0.5 * (p["x"] + tx))),  # FEEDBACK clamp: chip - 1
            "y": max(0.0, min(chip_h - 1.0, 0.5 * (p["y"] + ty))),
        }
    return out


def drag_clamp(x, y):
    """The DRAG clamp, AS WRITTEN in platform/assets/interactive-congestion-lab.js `moveSelectedTo`:
    x = Math.max(0, Math.min(11.5, wx)); y = Math.max(0, Math.min(7.5, wy)) — hard-coded 11.5 / 7.5 (CHIP - 0.5).
    Kept separate from the feedback clamp on purpose (see header)."""
    return max(0.0, min(11.5, float(x))), max(0.0, min(7.5, float(y)))


def heat_t(cong):
    """R5: t = clamp(cong / maxC, 0, 1) with maxC = max cong (0 -> all t = 0). Returns (t matrix, maxC)."""
    max_c = 0.0
    for col in cong:
        for v in col:
            if v > max_c:
                max_c = v
    if max_c <= 0:
        return [[0.0 for _ in col] for col in cong], max_c
    return [[min(1.0, max(0.0, v / max_c)) for v in col] for col in cong], max_c


def sig12(x):
    """R1: round a float to 12 significant digits (for --json, so JS and Python files agree)."""
    if isinstance(x, float):
        if x == 0.0 or not math.isfinite(x):
            return x
        return float(f"{x:.12g}")
    if isinstance(x, dict):
        return {k: sig12(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [sig12(v) for v in x]
    return x


# ---------------- instances ----------------
def load_instance(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    cells = [c["id"] for c in data["cells"]]
    placements = {}
    for key, val in data.items():  # json preserves file order
        if key in KNOWN_KEYS or not isinstance(val, dict):
            continue
        if all(c in val for c in cells):
            placements["spread" if key == "placement" else key] = clone_positions(val)
    order = sorted(placements, key=lambda n: (n != "congested_seed", n != "spread", n))
    return {
        "path": Path(path), "stem": Path(path).stem, "data": data,
        "cells": cells, "widths": {c["id"]: float(c.get("width", 1)) for c in data["cells"]},
        "nets": [list(n) for n in data["nets"]],
        "placements": {n: placements[n] for n in order},
        "sweep": [float(c) for c in data.get("sweep", [1.0, 2.0, 3.0, 4.0, 5.0, 8.0])],
    }


def instance_files():
    return sorted(HERE.glob("*.json"))


def run_events(fns, positions, inst):
    data = inst["data"]
    if fns.get("deposit_events"):
        ev = fns["deposit_events"](clone_positions(positions), data)
        return ev
    ev, _ = deposit_events(positions, data)
    return ev


def run_demand(fns, positions, inst):
    if fns.get("rudy_demand"):
        return fns["rudy_demand"](clone_positions(positions), inst["data"])
    return rudy_demand(positions, inst["data"])


# ---------------- reporting ----------------
class Report:
    def __init__(self):
        self.ok = self.fail = self.skip = 0

    def add(self, ok, label, detail=""):
        if ok is None:
            self.skip += 1
            print(f"SKIP  {label}   {detail}".rstrip())
        elif ok:
            self.ok += 1
            print(f"PASS  {label}")
        else:
            self.fail += 1
            print(f"FAIL  {label}   {detail}".rstrip())

    def close(self):
        print(f"\n{self.ok} PASS, {self.fail} FAIL, {self.skip} SKIP")
        return 1 if self.fail else 0


def close(a, b, tol=TOL):
    return a is not None and b is not None and abs(float(a) - float(b)) <= tol


def matrices_close(a, b, tol=TOL):
    if a is None or b is None or len(a) != len(b):
        return False
    return all(len(ra) == len(rb) and all(abs(float(x) - float(y)) <= tol for x, y in zip(ra, rb))
            for ra, rb in zip(a, b))


def safe(rep, label, fn, *args, **kw):
    try:
        return fn(*args, **kw)
    except Exception as exc:  # a learner's bug must be a FAIL line, not a traceback
        rep.add(False, label, f"raised {type(exc).__name__}: {exc}")
        return None


# ---------------- goldens (pinned literals; regenerate with --dump-goldens) ----------------
# >>> GOLDENS >>>
GOLDENS = {'boundary_move': {'runs': {'congested_seed': {'positions': {'A': {'x': 6.5, 'y': 2.0},
                                                             'B': {'x': 5.0, 'y': 2.0},
                                                             'C': {'x': 4.0, 'y': 3.0},
                                                             'D': {'x': 5.0, 'y': 3.0},
                                                             'E': {'x': 4.5, 'y': 2.5},
                                                             'F': {'x': 5.5, 'y': 2.5}},
                                               'events': [{'net': 0,
                                                           'pins': ['A', 'B'],
                                                           'bbox': [5.0, 2.0, 6.5, 2.0],
                                                           'hpwl': 1.5,
                                                           'tiles': [[1, 0], [2, 0]],
                                                           'share': 0.75},
                                                          {'net': 1,
                                                           'pins': ['C', 'D'],
                                                           'bbox': [4.0, 3.0, 5.0, 3.0],
                                                           'hpwl': 1.0,
                                                           'tiles': [[1, 0]],
                                                           'share': 1.0},
                                                          {'net': 2,
                                                           'pins': ['A', 'C'],
                                                           'bbox': [4.0, 2.0, 6.5, 3.0],
                                                           'hpwl': 3.5,
                                                           'tiles': [[1, 0], [2, 0]],
                                                           'share': 1.75},
                                                          {'net': 3,
                                                           'pins': ['B', 'D'],
                                                           'bbox': [5.0, 2.0, 5.0, 3.0],
                                                           'hpwl': 1.0,
                                                           'tiles': [[1, 0]],
                                                           'share': 1.0},
                                                          {'net': 4,
                                                           'pins': ['A', 'B', 'C', 'D'],
                                                           'bbox': [4.0, 2.0, 6.5, 3.0],
                                                           'hpwl': 3.5,
                                                           'tiles': [[1, 0], [2, 0]],
                                                           'share': 1.75},
                                                          {'net': 5,
                                                           'pins': ['E', 'F'],
                                                           'bbox': [4.5, 2.5, 5.5, 2.5],
                                                           'hpwl': 1.0,
                                                           'tiles': [[1, 0]],
                                                           'share': 1.0}],
                                               'demand': [[0.0, 0.0], [7.25, 0.0], [4.25, 0.0], [0.0, 0.0]],
                                               'congestion': [[0.0, 0.0],
                                                              [3.625, 0.0],
                                                              [2.125, 0.0],
                                                              [0.0, 0.0]],
                                               'overflow': {'perCell': [[0.0, 0.0],
                                                                        [5.25, 0.0],
                                                                        [2.25, 0.0],
                                                                        [0.0, 0.0]],
                                                            'total': 7.5,
                                                            'max': 5.25,
                                                            'count': 2},
                                               'hottest': [1, 0, 3.625],
                                               'hpwl': 11.5,
                                               'net_hpwl': [1.5, 1.0, 3.5, 1.0, 3.5, 1.0]},
                            'spread': {'positions': {'A': {'x': 1.0, 'y': 1.0},
                                                     'B': {'x': 8.0, 'y': 1.0},
                                                     'C': {'x': 1.0, 'y': 5.0},
                                                     'D': {'x': 8.0, 'y': 5.0},
                                                     'E': {'x': 5.0, 'y': 3.0},
                                                     'F': {'x': 6.0, 'y': 3.0}},
                                       'events': [{'net': 0,
                                                   'pins': ['A', 'B'],
                                                   'bbox': [1.0, 1.0, 8.0, 1.0],
                                                   'hpwl': 7.0,
                                                   'tiles': [[0, 0], [1, 0], [2, 0]],
                                                   'share': 2.3333333333333335},
                                                  {'net': 1,
                                                   'pins': ['C', 'D'],
                                                   'bbox': [1.0, 5.0, 8.0, 5.0],
                                                   'hpwl': 7.0,
                                                   'tiles': [[0, 1], [1, 1], [2, 1]],
                                                   'share': 2.3333333333333335},
                                                  {'net': 2,
                                                   'pins': ['A', 'C'],
                                                   'bbox': [1.0, 1.0, 1.0, 5.0],
                                                   'hpwl': 4.0,
                                                   'tiles': [[0, 0], [0, 1]],
                                                   'share': 2.0},
                                                  {'net': 3,
                                                   'pins': ['B', 'D'],
                                                   'bbox': [8.0, 1.0, 8.0, 5.0],
                                                   'hpwl': 4.0,
                                                   'tiles': [[2, 0], [2, 1]],
                                                   'share': 2.0},
                                                  {'net': 4,
                                                   'pins': ['A', 'B', 'C', 'D'],
                                                   'bbox': [1.0, 1.0, 8.0, 5.0],
                                                   'hpwl': 11.0,
                                                   'tiles': [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]],
                                                   'share': 1.8333333333333333},
                                                  {'net': 5,
                                                   'pins': ['E', 'F'],
                                                   'bbox': [5.0, 3.0, 6.0, 3.0],
                                                   'hpwl': 1.0,
                                                   'tiles': [[1, 0], [2, 0]],
                                                   'share': 0.5}],
                                       'demand': [[6.166666666666667, 6.166666666666667],
                                                  [4.666666666666667, 4.166666666666667],
                                                  [6.666666666666667, 6.166666666666667],
                                                  [0.0, 0.0]],
                                       'congestion': [[3.0833333333333335, 3.0833333333333335],
                                                      [2.3333333333333335, 2.0833333333333335],
                                                      [3.3333333333333335, 3.0833333333333335],
                                                      [0.0, 0.0]],
                                       'overflow': {'perCell': [[4.166666666666667, 4.166666666666667],
                                                                [2.666666666666667, 2.166666666666667],
                                                                [4.666666666666667, 4.166666666666667],
                                                                [0.0, 0.0]],
                                                    'total': 22.000000000000004,
                                                    'max': 4.666666666666667,
                                                    'count': 6},
                                       'hottest': [2, 0, 3.3333333333333335],
                                       'hpwl': 34.0,
                                       'net_hpwl': [7.0, 7.0, 4.0, 4.0, 11.0, 1.0]}},
                   'sweep': {'caps': [1.0, 2.0, 3.0, 4.0, 5.0, 8.0],
                             'perRun': {'congested_seed': [[1.0, 9.5, 6.25, 2],
                                                           [2.0, 7.5, 5.25, 2],
                                                           [3.0, 5.5, 4.25, 2],
                                                           [4.0, 3.5, 3.25, 2],
                                                           [5.0, 2.25, 2.25, 1],
                                                           [8.0, 0.0, 0.0, 0]],
                                        'spread': [[1.0, 28.000000000000004, 5.666666666666667, 6],
                                                   [2.0, 22.000000000000004, 4.666666666666667, 6],
                                                   [3.0, 16.000000000000004, 3.666666666666667, 6],
                                                   [4.0, 10.000000000000002, 2.666666666666667, 6],
                                                   [5.0, 5.166666666666668, 1.666666666666667, 4],
                                                   [8.0, 0.0, 0.0, 0]]}},
                   'feedback': {'from': 'congested_seed',
                                'to': {'A': {'x': 8.5, 'y': 2.0},
                                       'B': {'x': 3.25, 'y': 2.0},
                                       'C': {'x': 2.75, 'y': 2.5},
                                       'D': {'x': 3.25, 'y': 2.5},
                                       'E': {'x': 3.0, 'y': 2.25},
                                       'F': {'x': 3.5, 'y': 2.25}},
                                'demandAfter': [[4.416666666666667, 0.0],
                                                [8.041666666666668, 0.0],
                                                [6.791666666666668, 0.0],
                                                [0.0, 0.0]],
                                'overflowBefore': {'total': 7.5, 'max': 5.25, 'count': 2},
                                'overflowAfter': {'total': 13.250000000000004,
                                                  'max': 6.041666666666668,
                                                  'count': 3},
                                'hottestAfter': [1, 0, 4.020833333333334]},
                   'probes': {'hottest_tie': {'cong': [[1, 2], [0, 0], [0, 0], [2, 0]], 'want': [0, 1, 2.0]},
                              'hottest_zeros': {'cong': [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                                'want': [0, 0, 0.0]},
                              'cell_gcell': [[12, 8, [3, 1]],
                                             [-1, -1, [0, 0]],
                                             [3, 0, [1, 0]],
                                             [2.999, 3.999, [0, 0]]],
                              'drag_clamp': [[20, -3, [11.5, 0.0]],
                                             [11.7, 7.6, [11.5, 7.5]],
                                             [5, 5, [5.0, 5.0]]]}},
 'cap_below_one': {'runs': {'spread': {'positions': {'A': {'x': 2.5, 'y': 1.0}, 'B': {'x': 3.5, 'y': 1.0}},
                                       'events': [{'net': 0,
                                                   'pins': ['A', 'B'],
                                                   'bbox': [2.5, 1.0, 3.5, 1.0],
                                                   'hpwl': 1.0,
                                                   'tiles': [[0, 0], [1, 0]],
                                                   'share': 0.5}],
                                       'demand': [[0.5], [0.5]],
                                       'congestion': [[1.25], [1.25]],
                                       'overflow': {'perCell': [[0.09999999999999998], [0.09999999999999998]],
                                                    'total': 0.19999999999999996,
                                                    'max': 0.09999999999999998,
                                                    'count': 2},
                                       'hottest': [0, 0, 1.25],
                                       'hpwl': 1.0,
                                       'net_hpwl': [1.0]}},
                   'sweep': {'caps': [1.0, 0.5, 0.4],
                             'perRun': {'spread': [[1.0, 0.0, 0.0, 0],
                                                   [0.5, 0.0, 0.0, 0],
                                                   [0.4, 0.19999999999999996, 0.09999999999999998, 2]]}},
                   'probes': {'hottest_tie': {'cong': [[1, 2], [0, 0], [0, 0], [2, 0]], 'want': [0, 1, 2.0]},
                              'hottest_zeros': {'cong': [[0.0], [0.0]], 'want': [0, 0, 0.0]},
                              'cell_gcell': [[12, 8, [1, 0]],
                                             [-1, -1, [0, 0]],
                                             [3, 0, [1, 0]],
                                             [2.999, 3.999, [0, 0]]],
                              'drag_clamp': [[20, -3, [11.5, 0.0]],
                                             [11.7, 7.6, [11.5, 7.5]],
                                             [5, 5, [5.0, 5.0]]]}},
 'cap_one': {'runs': {'congested_seed': {'positions': {'A': {'x': 4.0, 'y': 2.0},
                                                       'B': {'x': 5.0, 'y': 2.0},
                                                       'C': {'x': 4.0, 'y': 3.0},
                                                       'D': {'x': 5.0, 'y': 3.0},
                                                       'E': {'x': 4.5, 'y': 2.5},
                                                       'F': {'x': 5.5, 'y': 2.5}},
                                         'events': [{'net': 0,
                                                     'pins': ['A', 'B'],
                                                     'bbox': [4.0, 2.0, 5.0, 2.0],
                                                     'hpwl': 1.0,
                                                     'tiles': [[1, 0]],
                                                     'share': 1.0},
                                                    {'net': 1,
                                                     'pins': ['C', 'D'],
                                                     'bbox': [4.0, 3.0, 5.0, 3.0],
                                                     'hpwl': 1.0,
                                                     'tiles': [[1, 0]],
                                                     'share': 1.0},
                                                    {'net': 2,
                                                     'pins': ['A', 'C'],
                                                     'bbox': [4.0, 2.0, 4.0, 3.0],
                                                     'hpwl': 1.0,
                                                     'tiles': [[1, 0]],
                                                     'share': 1.0},
                                                    {'net': 3,
                                                     'pins': ['B', 'D'],
                                                     'bbox': [5.0, 2.0, 5.0, 3.0],
                                                     'hpwl': 1.0,
                                                     'tiles': [[1, 0]],
                                                     'share': 1.0},
                                                    {'net': 4,
                                                     'pins': ['A', 'B', 'C', 'D'],
                                                     'bbox': [4.0, 2.0, 5.0, 3.0],
                                                     'hpwl': 2.0,
                                                     'tiles': [[1, 0]],
                                                     'share': 2.0},
                                                    {'net': 5,
                                                     'pins': ['E', 'F'],
                                                     'bbox': [4.5, 2.5, 5.5, 2.5],
                                                     'hpwl': 1.0,
                                                     'tiles': [[1, 0]],
                                                     'share': 1.0}],
                                         'demand': [[0.0, 0.0], [7.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                         'congestion': [[0.0, 0.0], [7.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                         'overflow': {'perCell': [[0.0, 0.0],
                                                                  [6.0, 0.0],
                                                                  [0.0, 0.0],
                                                                  [0.0, 0.0]],
                                                      'total': 6.0,
                                                      'max': 6.0,
                                                      'count': 1},
                                         'hottest': [1, 0, 7.0],
                                         'hpwl': 7.0,
                                         'net_hpwl': [1.0, 1.0, 1.0, 1.0, 2.0, 1.0]},
                      'spread': {'positions': {'A': {'x': 1.0, 'y': 1.0},
                                               'B': {'x': 8.0, 'y': 1.0},
                                               'C': {'x': 1.0, 'y': 5.0},
                                               'D': {'x': 8.0, 'y': 5.0},
                                               'E': {'x': 5.0, 'y': 3.0},
                                               'F': {'x': 6.0, 'y': 3.0}},
                                 'events': [{'net': 0,
                                             'pins': ['A', 'B'],
                                             'bbox': [1.0, 1.0, 8.0, 1.0],
                                             'hpwl': 7.0,
                                             'tiles': [[0, 0], [1, 0], [2, 0]],
                                             'share': 2.3333333333333335},
                                            {'net': 1,
                                             'pins': ['C', 'D'],
                                             'bbox': [1.0, 5.0, 8.0, 5.0],
                                             'hpwl': 7.0,
                                             'tiles': [[0, 1], [1, 1], [2, 1]],
                                             'share': 2.3333333333333335},
                                            {'net': 2,
                                             'pins': ['A', 'C'],
                                             'bbox': [1.0, 1.0, 1.0, 5.0],
                                             'hpwl': 4.0,
                                             'tiles': [[0, 0], [0, 1]],
                                             'share': 2.0},
                                            {'net': 3,
                                             'pins': ['B', 'D'],
                                             'bbox': [8.0, 1.0, 8.0, 5.0],
                                             'hpwl': 4.0,
                                             'tiles': [[2, 0], [2, 1]],
                                             'share': 2.0},
                                            {'net': 4,
                                             'pins': ['A', 'B', 'C', 'D'],
                                             'bbox': [1.0, 1.0, 8.0, 5.0],
                                             'hpwl': 11.0,
                                             'tiles': [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]],
                                             'share': 1.8333333333333333},
                                            {'net': 5,
                                             'pins': ['E', 'F'],
                                             'bbox': [5.0, 3.0, 6.0, 3.0],
                                             'hpwl': 1.0,
                                             'tiles': [[1, 0], [2, 0]],
                                             'share': 0.5}],
                                 'demand': [[6.166666666666667, 6.166666666666667],
                                            [4.666666666666667, 4.166666666666667],
                                            [6.666666666666667, 6.166666666666667],
                                            [0.0, 0.0]],
                                 'congestion': [[6.166666666666667, 6.166666666666667],
                                                [4.666666666666667, 4.166666666666667],
                                                [6.666666666666667, 6.166666666666667],
                                                [0.0, 0.0]],
                                 'overflow': {'perCell': [[5.166666666666667, 5.166666666666667],
                                                          [3.666666666666667, 3.166666666666667],
                                                          [5.666666666666667, 5.166666666666667],
                                                          [0.0, 0.0]],
                                              'total': 28.000000000000004,
                                              'max': 5.666666666666667,
                                              'count': 6},
                                 'hottest': [2, 0, 6.666666666666667],
                                 'hpwl': 34.0,
                                 'net_hpwl': [7.0, 7.0, 4.0, 4.0, 11.0, 1.0]}},
             'sweep': {'caps': [2.0, 1.0, 5.0, 8.0],
                       'perRun': {'congested_seed': [[2.0, 5.0, 5.0, 1],
                                                     [1.0, 6.0, 6.0, 1],
                                                     [5.0, 2.0, 2.0, 1],
                                                     [8.0, 0.0, 0.0, 0]],
                                  'spread': [[2.0, 22.000000000000004, 4.666666666666667, 6],
                                             [1.0, 28.000000000000004, 5.666666666666667, 6],
                                             [5.0, 5.166666666666668, 1.666666666666667, 4],
                                             [8.0, 0.0, 0.0, 0]]}},
             'feedback': {'from': 'congested_seed',
                          'to': {'A': {'x': 5.75, 'y': 2.0},
                                 'B': {'x': 6.25, 'y': 2.0},
                                 'C': {'x': 5.75, 'y': 2.5},
                                 'D': {'x': 6.25, 'y': 2.5},
                                 'E': {'x': 6.0, 'y': 2.25},
                                 'F': {'x': 6.5, 'y': 2.25}},
                          'demandAfter': [[0.0, 0.0], [1.5, 0.0], [2.0, 0.0], [0.0, 0.0]],
                          'overflowBefore': {'total': 6.0, 'max': 6.0, 'count': 1},
                          'overflowAfter': {'total': 1.5, 'max': 1.0, 'count': 2},
                          'hottestAfter': [2, 0, 2.0]},
             'probes': {'hottest_tie': {'cong': [[1, 2], [0, 0], [0, 0], [2, 0]], 'want': [0, 1, 2.0]},
                        'hottest_zeros': {'cong': [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                          'want': [0, 0, 0.0]},
                        'cell_gcell': [[12, 8, [3, 1]],
                                       [-1, -1, [0, 0]],
                                       [3, 0, [1, 0]],
                                       [2.999, 3.999, [0, 0]]],
                        'drag_clamp': [[20, -3, [11.5, 0.0]], [11.7, 7.6, [11.5, 7.5]], [5, 5, [5.0, 5.0]]]}},
 'tiny_cong': {'runs': {'congested_seed': {'positions': {'A': {'x': 4.0, 'y': 2.0},
                                                         'B': {'x': 5.0, 'y': 2.0},
                                                         'C': {'x': 4.0, 'y': 3.0},
                                                         'D': {'x': 5.0, 'y': 3.0},
                                                         'E': {'x': 4.5, 'y': 2.5},
                                                         'F': {'x': 5.5, 'y': 2.5}},
                                           'events': [{'net': 0,
                                                       'pins': ['A', 'B'],
                                                       'bbox': [4.0, 2.0, 5.0, 2.0],
                                                       'hpwl': 1.0,
                                                       'tiles': [[1, 0]],
                                                       'share': 1.0},
                                                      {'net': 1,
                                                       'pins': ['C', 'D'],
                                                       'bbox': [4.0, 3.0, 5.0, 3.0],
                                                       'hpwl': 1.0,
                                                       'tiles': [[1, 0]],
                                                       'share': 1.0},
                                                      {'net': 2,
                                                       'pins': ['A', 'C'],
                                                       'bbox': [4.0, 2.0, 4.0, 3.0],
                                                       'hpwl': 1.0,
                                                       'tiles': [[1, 0]],
                                                       'share': 1.0},
                                                      {'net': 3,
                                                       'pins': ['B', 'D'],
                                                       'bbox': [5.0, 2.0, 5.0, 3.0],
                                                       'hpwl': 1.0,
                                                       'tiles': [[1, 0]],
                                                       'share': 1.0},
                                                      {'net': 4,
                                                       'pins': ['A', 'B', 'C', 'D'],
                                                       'bbox': [4.0, 2.0, 5.0, 3.0],
                                                       'hpwl': 2.0,
                                                       'tiles': [[1, 0]],
                                                       'share': 2.0},
                                                      {'net': 5,
                                                       'pins': ['E', 'F'],
                                                       'bbox': [4.5, 2.5, 5.5, 2.5],
                                                       'hpwl': 1.0,
                                                       'tiles': [[1, 0]],
                                                       'share': 1.0}],
                                           'demand': [[0.0, 0.0], [7.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                           'congestion': [[0.0, 0.0], [3.5, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                           'overflow': {'perCell': [[0.0, 0.0],
                                                                    [5.0, 0.0],
                                                                    [0.0, 0.0],
                                                                    [0.0, 0.0]],
                                                        'total': 5.0,
                                                        'max': 5.0,
                                                        'count': 1},
                                           'hottest': [1, 0, 3.5],
                                           'hpwl': 7.0,
                                           'net_hpwl': [1.0, 1.0, 1.0, 1.0, 2.0, 1.0]},
                        'spread': {'positions': {'A': {'x': 1.0, 'y': 1.0},
                                                 'B': {'x': 8.0, 'y': 1.0},
                                                 'C': {'x': 1.0, 'y': 5.0},
                                                 'D': {'x': 8.0, 'y': 5.0},
                                                 'E': {'x': 5.0, 'y': 3.0},
                                                 'F': {'x': 6.0, 'y': 3.0}},
                                   'events': [{'net': 0,
                                               'pins': ['A', 'B'],
                                               'bbox': [1.0, 1.0, 8.0, 1.0],
                                               'hpwl': 7.0,
                                               'tiles': [[0, 0], [1, 0], [2, 0]],
                                               'share': 2.3333333333333335},
                                              {'net': 1,
                                               'pins': ['C', 'D'],
                                               'bbox': [1.0, 5.0, 8.0, 5.0],
                                               'hpwl': 7.0,
                                               'tiles': [[0, 1], [1, 1], [2, 1]],
                                               'share': 2.3333333333333335},
                                              {'net': 2,
                                               'pins': ['A', 'C'],
                                               'bbox': [1.0, 1.0, 1.0, 5.0],
                                               'hpwl': 4.0,
                                               'tiles': [[0, 0], [0, 1]],
                                               'share': 2.0},
                                              {'net': 3,
                                               'pins': ['B', 'D'],
                                               'bbox': [8.0, 1.0, 8.0, 5.0],
                                               'hpwl': 4.0,
                                               'tiles': [[2, 0], [2, 1]],
                                               'share': 2.0},
                                              {'net': 4,
                                               'pins': ['A', 'B', 'C', 'D'],
                                               'bbox': [1.0, 1.0, 8.0, 5.0],
                                               'hpwl': 11.0,
                                               'tiles': [[0, 0], [0, 1], [1, 0], [1, 1], [2, 0], [2, 1]],
                                               'share': 1.8333333333333333},
                                              {'net': 5,
                                               'pins': ['E', 'F'],
                                               'bbox': [5.0, 3.0, 6.0, 3.0],
                                               'hpwl': 1.0,
                                               'tiles': [[1, 0], [2, 0]],
                                               'share': 0.5}],
                                   'demand': [[6.166666666666667, 6.166666666666667],
                                              [4.666666666666667, 4.166666666666667],
                                              [6.666666666666667, 6.166666666666667],
                                              [0.0, 0.0]],
                                   'congestion': [[3.0833333333333335, 3.0833333333333335],
                                                  [2.3333333333333335, 2.0833333333333335],
                                                  [3.3333333333333335, 3.0833333333333335],
                                                  [0.0, 0.0]],
                                   'overflow': {'perCell': [[4.166666666666667, 4.166666666666667],
                                                            [2.666666666666667, 2.166666666666667],
                                                            [4.666666666666667, 4.166666666666667],
                                                            [0.0, 0.0]],
                                                'total': 22.000000000000004,
                                                'max': 4.666666666666667,
                                                'count': 6},
                                   'hottest': [2, 0, 3.3333333333333335],
                                   'hpwl': 34.0,
                                   'net_hpwl': [7.0, 7.0, 4.0, 4.0, 11.0, 1.0]}},
               'sweep': {'caps': [1.0, 2.0, 3.0, 4.0, 5.0, 8.0],
                         'perRun': {'congested_seed': [[1.0, 6.0, 6.0, 1],
                                                       [2.0, 5.0, 5.0, 1],
                                                       [3.0, 4.0, 4.0, 1],
                                                       [4.0, 3.0, 3.0, 1],
                                                       [5.0, 2.0, 2.0, 1],
                                                       [8.0, 0.0, 0.0, 0]],
                                    'spread': [[1.0, 28.000000000000004, 5.666666666666667, 6],
                                               [2.0, 22.000000000000004, 4.666666666666667, 6],
                                               [3.0, 16.000000000000004, 3.666666666666667, 6],
                                               [4.0, 10.000000000000002, 2.666666666666667, 6],
                                               [5.0, 5.166666666666668, 1.666666666666667, 4],
                                               [8.0, 0.0, 0.0, 0]]}},
               'feedback': {'from': 'congested_seed',
                            'to': {'A': {'x': 5.75, 'y': 2.0},
                                   'B': {'x': 6.25, 'y': 2.0},
                                   'C': {'x': 5.75, 'y': 2.5},
                                   'D': {'x': 6.25, 'y': 2.5},
                                   'E': {'x': 6.0, 'y': 2.25},
                                   'F': {'x': 6.5, 'y': 2.25}},
                            'demandAfter': [[0.0, 0.0], [1.5, 0.0], [2.0, 0.0], [0.0, 0.0]],
                            'overflowBefore': {'total': 5.0, 'max': 5.0, 'count': 1},
                            'overflowAfter': {'total': 0.0, 'max': 0.0, 'count': 0},
                            'hottestAfter': [2, 0, 1.0]},
               'probes': {'hottest_tie': {'cong': [[1, 2], [0, 0], [0, 0], [2, 0]], 'want': [0, 1, 2.0]},
                          'hottest_zeros': {'cong': [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]],
                                            'want': [0, 0, 0.0]},
                          'cell_gcell': [[12, 8, [3, 1]],
                                         [-1, -1, [0, 0]],
                                         [3, 0, [1, 0]],
                                         [2.999, 3.999, [0, 0]]],
                          'drag_clamp': [[20, -3, [11.5, 0.0]], [11.7, 7.6, [11.5, 7.5]], [5, 5, [5.0, 5.0]]],
                          'fb_clamp_x': {'F': [15.0, 2.5], 'want': [11.0, 4.25]},
                          'fb_clamp_y': {'F': [4.5, 20.0], 'want': [6.0, 7.0]}},
               'reversed': {'spread_nets_reversed': {'demand': [[6.166666666666666, 6.166666666666666],
                                                                [4.666666666666666, 4.166666666666667],
                                                                [6.666666666666666, 6.166666666666666],
                                                                [0.0, 0.0]],
                                                     'hottest': [2, 0, 3.333333333333333],
                                                     'total': 21.999999999999993,
                                                     'count': 6},
                            'seed_positions_dict_reversed_feedback_equal': True}}}

# <<< GOLDENS <<<


def compute_golden(inst):
    """Compute the golden block for one instance with the reference implementation (used by --dump-goldens)."""
    fns = REF_FNS
    g = {"runs": {}, "sweep": {"caps": inst["sweep"], "perRun": {}}}
    for name, pos in inst["placements"].items():
        ev = run_events(fns, pos, inst)
        dem = run_demand(fns, pos, inst)
        cap = float(inst["data"]["capacity"])
        cong = congestion_map(dem, cap)
        ov = overflow_metrics(dem, cap)
        h = hottest(cong)
        g["runs"][name] = {
            "positions": clone_positions(pos),
            "events": [{k: v for k, v in e.items() if k != "demandAfter"} for e in ev],
            "demand": dem, "congestion": cong,
            "overflow": {"perCell": ov["perCell"], "total": ov["total"], "max": ov["max"], "count": ov["count"]},
            "hottest": [h[0], h[1], h[2]],
            "hpwl": sum(hpwl(n, pos) for n in inst["nets"]),
            "net_hpwl": [hpwl(n, pos) for n in inst["nets"]],
        }
        g["sweep"]["perRun"][name] = []
        for c in inst["sweep"]:
            o = overflow_metrics(dem, c)
            g["sweep"]["perRun"][name].append([c, o["total"], o["max"], o["count"]])
    if "congested_seed" in inst["placements"]:
        pos = inst["placements"]["congested_seed"]
        cap = float(inst["data"]["capacity"])
        dem = run_demand(fns, pos, inst)
        before = overflow_metrics(dem, cap)
        to = placement_feedback_lite(pos, inst["data"])
        dem_a = run_demand(fns, to, inst)
        after = overflow_metrics(dem_a, cap)
        cong_a = congestion_map(dem_a, cap)
        g["feedback"] = {
            "from": "congested_seed", "to": clone_positions(to),
            "demandAfter": dem_a,
            "overflowBefore": {"total": before["total"], "max": before["max"], "count": before["count"]},
            "overflowAfter": {"total": after["total"], "max": after["max"], "count": after["count"]},
            "hottestAfter": list(hottest(cong_a)),
        }
    nx, ny, cw, ch = geom(inst["data"])
    g["probes"] = {
        "hottest_tie": {"cong": [[1, 2], [0, 0], [0, 0], [2, 0]], "want": list(hottest([[1, 2], [0, 0], [0, 0], [2, 0]]))},
        "hottest_zeros": {"cong": zeros(nx, ny), "want": list(hottest(zeros(nx, ny)))},
        "cell_gcell": [[12, 8, list(cell_gcell(12, 8, nx, ny, cw, ch))], [-1, -1, list(cell_gcell(-1, -1, nx, ny, cw, ch))],
                       [3, 0, list(cell_gcell(3, 0, nx, ny, cw, ch))], [2.999, 3.999, list(cell_gcell(2.999, 3.999, nx, ny, cw, ch))]],
        "drag_clamp": [[20, -3, list(drag_clamp(20, -3))], [11.7, 7.6, list(drag_clamp(11.7, 7.6))],
                       [5, 5, list(drag_clamp(5, 5))]],
    }
    if inst["stem"] == "tiny_cong":
        nx, ny, cw, ch = geom(inst["data"])
        seed = inst["placements"]["congested_seed"]
        for tag, f in (("fb_clamp_x", {"x": 15.0, "y": 2.5}), ("fb_clamp_y", {"x": 4.5, "y": 20.0})):
            pos = clone_positions(seed)
            pos["F"] = dict(f)
            out = placement_feedback_lite(pos, inst["data"])
            g["probes"][tag] = {"F": [f["x"], f["y"]], "want": [out["F"]["x"], out["F"]["y"]]}
        # reversed-input probes
        data_rev = dict(inst["data"])
        data_rev["nets"] = list(reversed(inst["nets"]))
        inst_rev = dict(inst)
        inst_rev["data"] = data_rev
        dem_rev = rudy_demand(inst["placements"]["spread"], data_rev)
        ov_rev = overflow_metrics(dem_rev, float(inst["data"]["capacity"]))
        h_rev = hottest(congestion_map(dem_rev, float(inst["data"]["capacity"])))
        g["reversed"] = {
            "spread_nets_reversed": {
                "demand": dem_rev, "hottest": [h_rev[0], h_rev[1], h_rev[2]],
                "total": ov_rev["total"], "count": ov_rev["count"],
            },
            "seed_positions_dict_reversed_feedback_equal": (
                placement_feedback_lite(dict(reversed(list(seed.items()))), inst["data"]) == placement_feedback_lite(seed, inst["data"])
            ),
        }
    return g


REF_FNS = {
    "cell_gcell": cell_gcell, "net_bbox": net_bbox, "hpwl": hpwl,
    "deposit_events": lambda positions, data: deposit_events(positions, data)[0],
    "rudy_demand": rudy_demand, "congestion_map": congestion_map,
    "overflow_metrics": overflow_metrics, "hottest": hottest,
    "placement_feedback_lite": placement_feedback_lite,
}


# ---------------- checks that run on any implementation (reference or --impl) ----------------
def check_instance(rep, fns, inst, show=False):
    stem = inst["stem"]
    g = GOLDENS.get(stem)
    if g is None:
        rep.add(None, f"{stem}: pinned golden block", "(no GOLDENS entry — run --dump-goldens)")
        return
    data = inst["data"]
    cap = float(data["capacity"])
    nx, ny, cw, ch = geom(data)
    print(f"\n== instance {stem} ({inst['path'].name}): chip {data['chip']['W']}x{data['chip']['H']}, "
          f"GCell {nx}x{ny} of {cw}x{ch}, capacity {cap:g}, cells {', '.join(inst['cells'])}, {len(inst['nets'])} nets ==")

    for name, want in g["runs"].items():
        pos = inst["placements"][name]
        rep.add(pos == want["positions"], f"{stem}/{name}: positions as loaded")

        # R3 deposit events, in fill order
        if fns.get("deposit_events") is None:
            rep.add(None, f"{stem}/{name}: deposit_events fill order", "(function not defined yet)")
        else:
            ev = safe(rep, f"{stem}/{name} events", fns["deposit_events"], clone_positions(pos), data)
            if ev is not None:
                ok = len(ev) == len(want["events"])
                detail = ""
                if ok:
                    for got, w in zip(ev, want["events"]):
                        if got.get("pins") != w["pins"] or got.get("tiles") != w["tiles"] or not close(got.get("hpwl"), w["hpwl"]) \
                           or not close(got.get("share"), w["share"]) or not all(close(a, b) for a, b in zip(got.get("bbox", []), w["bbox"])):
                            ok = False
                            detail = f"event net {w['net']}: got {got}"
                            break
                else:
                    detail = f"got {len(ev)} events, want {len(want['events'])}"
                rep.add(ok, f"{stem}/{name}: {len(want['events'])} deposit events (bbox, hpwl, tiles in fill order, share)", detail)

        # R3 demand
        if fns.get("rudy_demand") is None:
            rep.add(None, f"{stem}/{name}: rudy_demand", "(function not defined yet)")
        else:
            dem = safe(rep, f"{stem}/{name} demand", fns["rudy_demand"], clone_positions(pos), data)
            rep.add(matrices_close(dem, want["demand"]), f"{stem}/{name}: RUDY demand matrix", f"got {dem}")

        # congestion
        if fns.get("congestion_map") is None:
            rep.add(None, f"{stem}/{name}: congestion_map", "(function not defined yet)")
        else:
            cong = safe(rep, f"{stem}/{name} cong", fns["congestion_map"], want["demand"], cap)
            rep.add(matrices_close(cong, want["congestion"]), f"{stem}/{name}: congestion = demand / {cap:g}", f"got {cong}")

        # R7 overflow
        if fns.get("overflow_metrics") is None:
            rep.add(None, f"{stem}/{name}: overflow_metrics", "(function not defined yet)")
        else:
            ov = safe(rep, f"{stem}/{name} overflow", fns["overflow_metrics"], want["demand"], cap)
            if ov is not None:
                w = want["overflow"]
                rep.add(matrices_close(ov.get("perCell"), w["perCell"]) and close(ov.get("total"), w["total"])
                        and close(ov.get("max"), w["max"]) and ov.get("count") == w["count"],
                        f"{stem}/{name}: overflow total {w['total']:g}, max {w['max']:g}, count {w['count']} (strict > 0)",
                        f"got total {ov.get('total')}, max {ov.get('max')}, count {ov.get('count')}")

        # R2 hottest
        if fns.get("hottest") is None:
            rep.add(None, f"{stem}/{name}: hottest", "(function not defined yet)")
        else:
            h = safe(rep, f"{stem}/{name} hottest", fns["hottest"], want["congestion"])
            if h is not None:
                w = want["hottest"]
                rep.add(h[0] == w[0] and h[1] == w[1] and close(h[2], w[2]),
                        f"{stem}/{name}: hottest ({w[0]},{w[1]}) @ {w[2]:g} (R2 row-major first-wins)", f"got {h}")

        # hpwl
        if fns.get("hpwl") is None:
            rep.add(None, f"{stem}/{name}: hpwl", "(function not defined yet)")
        else:
            nh = safe(rep, f"{stem}/{name} net hpwl", lambda: [fns["hpwl"](n, pos) for n in inst["nets"]])
            if nh is not None:
                rep.add(all(close(a, b) for a, b in zip(nh, want["net_hpwl"])) and close(sum(nh), want["hpwl"]),
                        f"{stem}/{name}: per-net HPWL {want['net_hpwl']}, total {want['hpwl']:g}", f"got {nh}")

        # capacity sweep on this run
        if fns.get("overflow_metrics") is not None and fns.get("congestion_map") is not None:
            dem = want["demand"]
            for c, tot, mx, cnt in g["sweep"]["perRun"][name]:
                ov = safe(rep, f"{stem}/{name} sweep cap {c:g}", fns["overflow_metrics"], dem, c)
                if ov is not None:
                    rep.add(close(ov["total"], tot) and close(ov["max"], mx) and ov["count"] == cnt,
                            f"{stem}/{name}: capacity {cap:g} -> {c:g}: overflow total {tot:g}, max {mx:g}, count {cnt}",
                            f"got {ov['total']}, {ov['max']}, {ov['count']}")

    # feedback (R4 + feedback clamp)
    if "feedback" in g:
        if fns.get("placement_feedback_lite") is None:
            rep.add(None, f"{stem}: placement_feedback_lite", "(function not defined yet)")
        else:
            fb = g["feedback"]
            pos = inst["placements"][fb["from"]]
            to = safe(rep, f"{stem} feedback", fns["placement_feedback_lite"], clone_positions(pos), data)
            if to is not None:
                ok = all(close(to[c]["x"], fb["to"][c]["x"]) and close(to[c]["y"], fb["to"][c]["y"]) for c in fb["to"])
                rep.add(ok, f"{stem}: feedback from {fb['from']}: positions (R4 neighbour order, feedback clamp [0,11]x[0,7])",
                        f"got {to}")
                if fns.get("rudy_demand") and fns.get("overflow_metrics"):
                    dem_a = safe(rep, f"{stem} feedback demand", fns["rudy_demand"], to, data)
                    ov_a = safe(rep, f"{stem} feedback overflow", fns["overflow_metrics"], dem_a, cap)
                    if ov_a is not None:
                        w = fb["overflowAfter"]
                        rep.add(close(ov_a["total"], w["total"]) and close(ov_a["max"], w["max"]) and ov_a["count"] == w["count"],
                                f"{stem}: overflow {fb['overflowBefore']['total']:g}/{fb['overflowBefore']['max']:g}/"
                                f"{fb['overflowBefore']['count']} before -> {w['total']:g}/{w['max']:g}/{w['count']} after",
                                f"got {ov_a['total']}, {ov_a['max']}, {ov_a['count']}")

    # probes
    pr = g.get("probes", {})
    if "hottest_tie" in pr and fns.get("hottest"):
        h = safe(rep, "probe hottest tie", fns["hottest"], pr["hottest_tie"]["cong"])
        if h is not None:
            rep.add(list(h) == pr["hottest_tie"]["want"],
                    f"probe R2 tie: cong {pr['hottest_tie']['cong']} -> first max wins {pr['hottest_tie']['want']}", f"got {list(h)}")
    if "hottest_zeros" in pr and fns.get("hottest"):
        h = safe(rep, "probe hottest zeros", fns["hottest"], pr["hottest_zeros"]["cong"])
        if h is not None:
            rep.add(list(h) == pr["hottest_zeros"]["want"], "probe R2 all-zeros -> (0,0,0)", f"got {list(h)}")
    if pr.get("cell_gcell") and fns.get("cell_gcell"):
        for x, y, want in pr["cell_gcell"]:
            got = safe(rep, f"probe cell_gcell({x},{y})", fns["cell_gcell"], x, y, nx, ny, cw, ch)
            if got is not None:
                rep.add(list(got) == want, f"probe R6 cell_gcell({x}, {y}) -> {want} (clamp into edge GCell)", f"got {list(got)}")
    if pr.get("drag_clamp"):
        for x, y, want in pr["drag_clamp"]:
            got = safe(rep, f"probe drag_clamp({x},{y})", drag_clamp, x, y)  # the rule as written, not the learner's
            rep.add(list(got) == want, f"probe DRAG clamp ({x},{y}) -> {want}  [0,11.5]x[0,7.5] as written in interactive-congestion-lab.js",
                    f"got {list(got)}")
    for tag in ("fb_clamp_x", "fb_clamp_y"):
        if pr.get(tag) and fns.get("placement_feedback_lite"):
            pos = clone_positions(inst["placements"]["congested_seed"])
            pos["F"] = {"x": pr[tag]["F"][0], "y": pr[tag]["F"][1]}
            out = safe(rep, f"probe {tag}", fns["placement_feedback_lite"], pos, data)
            if out is not None:
                rep.add(close(out["F"]["x"], pr[tag]["want"][0]) and close(out["F"]["y"], pr[tag]["want"][1]),
                        f"probe FEEDBACK clamp: F {pr[tag]['F']} -> ({pr[tag]['want'][0]:g},{pr[tag]['want'][1]:g})  [0,11]x[0,7] as written",
                        f"got ({out['F']['x']},{out['F']['y']})")

    # reversed-input check
    rev = g.get("reversed")
    if rev:
        if fns.get("rudy_demand") and fns.get("hottest") and fns.get("overflow_metrics"):
            data_rev = dict(data)
            data_rev["nets"] = list(reversed(inst["nets"]))
            dem = safe(rep, "reversed nets demand", fns["rudy_demand"], inst["placements"]["spread"], data_rev)
            if dem is not None:
                w = rev["spread_nets_reversed"]
                ov = fns["overflow_metrics"](dem, cap)
                h = fns["hottest"](fns["congestion_map"](dem, cap))
                rep.add(matrices_close(dem, w["demand"]) and h[0] == w["hottest"][0] and h[1] == w["hottest"][1]
                        and close(h[2], w["hottest"][2]) and ov["count"] == w["count"] and close(ov["total"], w["total"]),
                        f"{stem}: reversed nets on spread — same tiles per net, demand within 1e-9, count {w['count']}, hottest ({w['hottest'][0]},{w['hottest'][1]})",
                        f"got count {ov['count']}, hottest {list(h)}, total {ov['total']} (last-ulp differences allowed, R1)")
        if rev.get("seed_positions_dict_reversed_feedback_equal") and fns.get("placement_feedback_lite"):
            seed = inst["placements"]["congested_seed"]
            a = safe(rep, "reversed dict feedback a", fns["placement_feedback_lite"], clone_positions(seed), data)
            b = safe(rep, "reversed dict feedback b", fns["placement_feedback_lite"],
                     {k: v for k, v in reversed(list(seed.items()))}, data)
            if a is not None and b is not None:
                rep.add(a == b, f"{stem}: positions dict in reverse key order -> identical feedback (R4: overflow map computed once)",
                        f"got {b}")


def common_crosscheck(rep, inst):
    """The course's common/solvers.py must agree with the pinned goldens within 1e-9 (R1)."""
    try:
        sys.path.insert(0, str(COURSE))
        sys.path.insert(0, str(COURSE / "common"))
        import solvers  # noqa: PLC0415  (common/solvers.py)
        import congestionutil  # noqa: PLC0415
    except Exception as exc:
        rep.add(None, "common/solvers.py cross-check", f"(import failed: {exc})")
        return
    g = GOLDENS.get(inst["stem"])
    if not g:
        return
    data = inst["data"]
    cap = float(data["capacity"])
    for name, want in g["runs"].items():
        pos = inst["placements"][name]
        dem = solvers.rudy_demand(pos, data)
        ok = matrices_close(dem, want["demand"])
        ov = solvers.overflow_metrics(dem, cap)
        ok = ok and close(ov["total"], want["overflow"]["total"], 1e-9) and ov["count"] == want["overflow"]["count"]
        h = solvers.hottest(solvers.congestion_map(dem, cap))
        ok = ok and h[0] == want["hottest"][0] and h[1] == want["hottest"][1] and close(h[2], want["hottest"][2])
        rep.add(ok, f"common/solvers.py agrees on {inst['stem']}/{name} (tol 1e-9; its sum() may differ in the last ulp, R1)",
                f"demand {dem}")
    if "feedback" in g and "congested_seed" in inst["placements"]:
        to = solvers.placement_feedback_lite(inst["placements"]["congested_seed"], data)
        fb = g["feedback"]["to"]
        rep.add(all(close(to[c]["x"], fb[c]["x"]) and close(to[c]["y"], fb[c]["y"]) for c in fb),
                f"common/solvers.py placement_feedback_lite agrees on {inst['stem']}")


# ---------------- --vs-node ----------------
def core_matches(data):
    """The JS core hard-codes the tiny geometry; --vs-node can only compare matching instances."""
    return (data["chip"] == {"W": 12, "H": 8} and data["gcell"] == {"nx": 4, "ny": 2, "cellW": 3, "cellH": 4}
            and [c["id"] for c in data["cells"]] == list("ABCDEF")
            and [list(n) for n in data["nets"]] == [["A", "B"], ["C", "D"], ["A", "C"], ["B", "D"], ["A", "B", "C", "D"], ["E", "F"]])


def vs_node(insts):
    rep = Report()
    if not CORE_JS.exists() or not NODE_HELPER.exists():
        print("SKIP  --vs-node: platform/assets/congestion-core.js or examples/cong_node.mjs not found")
        return 0
    matching = [i for i in insts if core_matches(i["data"])]
    skipped = [i["stem"] for i in insts if i not in matching]
    if skipped:
        print(f"note: --vs-node compares only instances matching the JS core's hard-coded tiny geometry; "
              f"skipped: {', '.join(skipped)} (the Python reference still checks them)")
    if not matching:
        print("SKIP  --vs-node: no instance matches the core geometry")
        return 0
    req = {
        "instances": [{
            "name": i["stem"], "capacity": float(i["data"]["capacity"]),
            "nets": i["nets"], "placements": i["placements"], "caps": i["sweep"],
        } for i in matching],
        "probes": {
            "hottest_tie": [[1, 2], [0, 0], [0, 0], [2, 0]],
            "hottest_zeros": [[0, 0], [0, 0], [0, 0], [0, 0]],
            "cell_gcell": [[12, 8], [-1, -1], [3, 0], [2.999, 3.999]],
            "fb_clamp_x": {"F": [15, 2.5]}, "fb_clamp_y": {"F": [4.5, 20]},
            "drag": [[20, -3], [11.7, 7.6], [5, 5]],
        },
    }
    try:
        res = subprocess.run(["node", str(NODE_HELPER), CORE_JS.as_uri(), LAB_JS.as_uri()],
                             input=json.dumps(req), capture_output=True, text=True, check=True)
        ans = json.loads(res.stdout)
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"SKIP  --vs-node: node failed ({exc})")
        return 0

    rep.add(ans.get("coreOk", False), "the helper's fill-order copy of the deposit loop equals the real rudyDemand bit-for-bit on every run")
    rep.add(ans.get("probes", {}).get("drag", {}).get("literalsFound") is True,
            "the drag clamp literals 11.5 / 7.5 are present in platform/assets/interactive-congestion-lab.js as written")

    bad = []
    for inst, a in zip(matching, ans["instances"]):
        g = GOLDENS[inst["stem"]]
        for name, want in g["runs"].items():
            arun = next(r for r in a["runs"] if r["name"] == name)
            if arun["demand"] != want["demand"]:
                bad.append(f"{inst['stem']}/{name}:demand")
            if arun["congestion"] != want["congestion"]:
                bad.append(f"{inst['stem']}/{name}:cong")
            if arun["overflow"]["perCell"] != want["overflow"]["perCell"] or arun["overflow"]["total"] != want["overflow"]["total"] \
               or arun["overflow"]["max"] != want["overflow"]["max"] or arun["overflow"]["count"] != want["overflow"]["count"]:
                bad.append(f"{inst['stem']}/{name}:overflow")
            if [arun["hottest"]["i"], arun["hottest"]["j"], arun["hottest"]["v"]] != want["hottest"]:
                bad.append(f"{inst['stem']}/{name}:hottest")
            for ev, wev in zip(arun["events"], want["events"]):
                if ev["pins"] != wev["pins"] or ev["tiles"] != wev["tiles"] or ev["bbox"] != wev["bbox"] \
                   or ev["hpwl"] != wev["hpwl"] or ev["share"] != wev["share"]:
                    bad.append(f"{inst['stem']}/{name}:event{wev['net']}")
            if arun["net_hpwl"] != want["net_hpwl"] or arun["hpwl"] != want["hpwl"]:
                bad.append(f"{inst['stem']}/{name}:hpwl")
        for name in inst["placements"]:
            for (c, tot, mx, cnt), asw in zip(g["sweep"]["perRun"][name], a["sweep"][name]):
                if asw["capacity"] != c or asw["overflow"]["total"] != tot or asw["overflow"]["max"] != mx or asw["overflow"]["count"] != cnt:
                    bad.append(f"{inst['stem']}/{name}:sweep cap {c:g}")
        if "feedback" in g:
            afb = a["feedback"]
            fb = g["feedback"]
            if afb["to"] != fb["to"] or afb["overflowBefore"] != fb["overflowBefore"] or afb["overflowAfter"] != fb["overflowAfter"]:
                bad.append(f"{inst['stem']}:feedback")
    rep.add(not bad, "--vs-node: JS (platform/assets/congestion-core.js) and Python agree BIT-FOR-BIT per cell "
                     "(demand, congestion, overflow perCell/total/max/count, hottest, events, HPWL, sweep, feedback)",
            f"differs: {bad[:12]}")

    if "tiny_cong" in [i["stem"] for i in matching]:
        p = ans["probes"]
        g = GOLDENS["tiny_cong"]["probes"]
        rep.add([p["hottest_tie"]["i"], p["hottest_tie"]["j"], p["hottest_tie"]["v"]] == g["hottest_tie"]["want"]
                and [p["hottest_zeros"]["i"], p["hottest_zeros"]["j"], p["hottest_zeros"]["v"]] == g["hottest_zeros"]["want"],
                "--vs-node: hottest probes (R2 tie -> first max (0,1); zeros -> (0,0,0)) equal in JS and Python")
        rep.add([[c[0], c[1], [p["cell_gcell"][k]["i"], p["cell_gcell"][k]["j"]]] for k, c in enumerate(g["cell_gcell"])]
                == g["cell_gcell"], "--vs-node: cellGcell clamp probes equal (R6)")
        rep.add([[d[0], d[1], [p["drag"]["probes"][k]["x"], p["drag"]["probes"][k]["y"]]] for k, d in enumerate(g["drag_clamp"])] == g["drag_clamp"],
                "--vs-node: drag clamp probes equal (11.5/7.5 as written in interactive-congestion-lab.js)")
        for tag in ("fb_clamp_x", "fb_clamp_y"):
            got = [p[tag]["x"], p[tag]["y"]]
            rep.add(got == g[tag]["want"],
                    f"--vs-node: feedback clamp probe {tag}: F -> ({got[0]:g},{got[1]:g}) (chip-1 = 11/7 as written)")
    return rep.close()


# ---------------- --json (the lesson replay file, UPGRADE_NOTES.md §0.4) ----------------
def build_json(inst):
    data = inst["data"]
    cap = float(data["capacity"])
    nx, ny, cw, ch = geom(data)
    out = {
        "instance": inst["stem"],
        "demandFn": "rudy",
        "chip": {"W": data["chip"]["W"], "H": data["chip"]["H"]},
        "gcell": {"nx": nx, "ny": ny, "cellW": cw, "cellH": ch},
        "capacity": cap,
        "cells": [{"id": c["id"], "width": c.get("width", 1), "height": c.get("height", 1)} for c in data["cells"]],
        "nets": inst["nets"],
        "rules": {
            "R1": "checks use abs tol 1e-9; display 2 decimals round-half-even; --json floats rounded to 12 significant digits",
            "R2": "hottest: scan i outer, j inner, strict >; first max in row-major order wins",
            "R3": "RUDY: nets in file order; tiles = bbox-corner GCells filled i-outer/j-inner; share = hpwl / max(1, #tiles); demand accumulates in that order",
            "R4": "feedback: neighbours (+1,0),(-1,0),(0,+1),(0,-1), strict <; midpoint toward target tile centre",
            "R5": "heat: t = clamp(cong / maxC, 0, 1), maxC = max cong (0 -> t = 0); oversubscribed (>1) is NOT a colour boundary",
            "R6": "cellGcell: i = clamp(floor(x/cellW), 0, nx-1), same for j",
            "R7": "overflow: perCell = max(0, demand - capacity); count = #cells with > 0 (strict); total in scan order",
        },
        "clamps": {
            "drag": {"x": [0, 11.5], "y": [0, 7.5],
                     "source": "platform/assets/interactive-congestion-lab.js moveSelectedTo (hard-coded 11.5/7.5 = CHIP-0.5)"},
            "feedback": {"x": [0, float(data["chip"]["W"]) - 1], "y": [0, float(data["chip"]["H"]) - 1],
                         "source": "platform/assets/congestion-core.js placementFeedbackLite (chip-1 = 11/7)"},
            "note": "two different in-chip clamp rules, kept as written and tested as-is, not unified",
        },
        "heatPalette": {
            "mode": "relative-to-max",
            "rule": "t = clamp(cong / maxC, 0, 1); maxC = max cong (0 -> t = 0)",
            "stops": PAPER_STOPS,
            "interp": "segment i = min(2, floor(3u)), f = 3u - i, RGB lerped between stops; alpha = 0.15 + 0.7u",
            "screen": "linear rgb(40+200u, 180-140u, 80-40u), alpha 0.55",
        },
        "runs": [],
    }
    for name, pos in inst["placements"].items():
        events, dem = deposit_events(pos, data)
        cong = congestion_map(dem, cap)
        ov = overflow_metrics(dem, cap)
        h = hottest(cong)
        t, max_c = heat_t(cong)
        out["runs"].append({
            "name": name,
            "positions": clone_positions(pos),
            "capacity": cap,
            "events": events,  # ordered per-net deposit events; each carries demandAfter (the accumulated demand)
            "demand": dem,
            "congestion": cong,
            "overflow": {"perCell": ov["perCell"], "total": ov["total"], "max": ov["max"], "count": ov["count"]},
            "hottest": {"i": h[0], "j": h[1], "v": h[2]},
            "heat": {"mode": "relative-to-max", "maxC": max_c, "t": t},
        })
    if "congested_seed" in inst["placements"]:
        pos = inst["placements"]["congested_seed"]
        dem = rudy_demand(pos, data)
        before = overflow_metrics(dem, cap)
        to = placement_feedback_lite(pos, data)
        dem_a = rudy_demand(to, data)
        after = overflow_metrics(dem_a, cap)
        cong_a = congestion_map(dem_a, cap)
        h_a = hottest(cong_a)
        out["feedback"] = {
            "from": "congested_seed",
            "to": clone_positions(to),
            "demandAfter": dem_a,
            "overflowBefore": {"total": before["total"], "max": before["max"], "count": before["count"]},
            "overflowAfter": {"total": after["total"], "max": after["max"], "count": after["count"]},
            "hottestAfter": {"i": h_a[0], "j": h_a[1], "v": h_a[2]},
        }
    out["capacitySweep"] = {
        "capacities": inst["sweep"],
        "runs": [{
            "name": name,
            "capacity": c,
            "congestion": congestion_map(dem, c),
            "overflow": {k: overflow_metrics(dem, c)[k] for k in ("perCell", "total", "max", "count")},
            "hottest": (lambda hh: {"i": hh[0], "j": hh[1], "v": hh[2]})(hottest(congestion_map(dem, c))),
            "heat": {"maxC": heat_t(congestion_map(dem, c))[1], "t": heat_t(congestion_map(dem, c))[0]},
        } for name, pos in inst["placements"].items() for dem in [rudy_demand(pos, data)] for c in inst["sweep"]],
    }
    return sig12(out)


# ---------------- --show ----------------
def f2(x):
    return f"{x:.2f}"


def show_matrix(m):
    return "  " + " | ".join(" ".join(f2(v) for v in col) for col in m)


def show_instance(inst):
    data = inst["data"]
    cap = float(data["capacity"])
    print(f"\n===== {inst['stem']} ({inst['path'].name}) — chip {data['chip']['W']}x{data['chip']['H']}, "
          f"GCell {geom(data)[0]}x{geom(data)[1]} of {geom(data)[2]}x{geom(data)[3]}, capacity {cap:g} =====")
    print("nets:", inst["nets"])
    for name, pos in inst["placements"].items():
        events, dem = deposit_events(pos, data)
        cong = congestion_map(dem, cap)
        ov = overflow_metrics(dem, cap)
        h = hottest(cong)
        t, max_c = heat_t(cong)
        print(f"\n--- run '{name}' (capacity {cap:g}) ---")
        print("positions:", {k: (v["x"], v["y"]) for k, v in pos.items()})
        print("deposit events (R3 fill order):")
        for e in events:
            print(f"  net {e['net']} {e['pins']}: bbox {e['bbox']}, hpwl {e['hpwl']:g}, "
                  f"tiles {e['tiles']}, share {e['share']:.6f}")
        print("demand:      ", show_matrix(dem))
        print("congestion:  ", show_matrix(cong))
        print("overflow:    ", show_matrix(ov["perCell"]), f" total {ov['total']:.6f} max {ov['max']:.6f} count {ov['count']}")
        print(f"hottest (R2): ({h[0]},{h[1]}) @ {h[2]:.6f}   heat t (R5, maxC {max_c:.6f}):", show_matrix(t))
        print("hpwl:", sum(hpwl(n, pos) for n in inst["nets"]), " per-net:", [hpwl(n, pos) for n in inst["nets"]])
        for c in inst["sweep"]:
            o = overflow_metrics(dem, c)
            print(f"  capacity {c:g}: overflow total {o['total']:.6f}, max {o['max']:.6f}, count {o['count']}")
    if "congested_seed" in inst["placements"]:
        pos = inst["placements"]["congested_seed"]
        dem = rudy_demand(pos, data)
        before = overflow_metrics(dem, cap)
        to = placement_feedback_lite(pos, data)
        dem_a = rudy_demand(to, data)
        after = overflow_metrics(dem_a, cap)
        h_a = hottest(congestion_map(dem_a, cap))
        print(f"\n--- feedback from congested_seed (R4, feedback clamp [0,{float(data['chip']['W'])-1:g}]x[0,{float(data['chip']['H'])-1:g}]) ---")
        print("to:", {k: (v["x"], v["y"]) for k, v in to.items()})
        print("demand after:", show_matrix(dem_a), f" overflow {before['total']:.6f}/{before['max']:.6f}/{before['count']} -> "
              f"{after['total']:.6f}/{after['max']:.6f}/{after['count']}, hottest after ({h_a[0]},{h_a[1]}) @ {h_a[2]:.6f}")
    print("\n--- probes ---")
    print("R2 tie  [[1,2],[0,0],[0,0],[2,0]] ->", hottest([[1, 2], [0, 0], [0, 0], [2, 0]]), "(first max in row-major wins)")
    print("R2 zeros ->", hottest(zeros(4, 2)))
    print("R6 cellGcell: (12,8) ->", cell_gcell(12, 8, *geom(data)[:4]), " (-1,-1) ->", cell_gcell(-1, -1, *geom(data)[:4]))
    print("DRAG clamp (as written, [0,11.5]x[0,7.5]): (20,-3) ->", drag_clamp(20, -3), " (11.7,7.6) ->", drag_clamp(11.7, 7.6))
    if inst["stem"] == "tiny_cong":
        for tag, f in (("fb_clamp_x", (15, 2.5)), ("fb_clamp_y", (4.5, 20))):
            p = clone_positions(inst["placements"]["congested_seed"])
            p["F"] = {"x": f[0], "y": f[1]}
            out = placement_feedback_lite(p, data)
            print(f"FEEDBACK clamp (as written, chip-1): F {f} -> ({out['F']['x']:g},{out['F']['y']:g})")
        data_rev = dict(data)
        data_rev["nets"] = list(reversed(inst["nets"]))
        dem_rev = rudy_demand(inst["placements"]["spread"], data_rev)
        ov_rev = overflow_metrics(dem_rev, cap)
        h_rev = hottest(congestion_map(dem_rev, cap))
        print(f"reversed nets on spread: demand within 1e-9 of forward, count {ov_rev['count']}, "
              f"hottest ({h_rev[0]},{h_rev[1]}) @ {h_rev[2]!r}, total {ov_rev['total']!r} (last-ulp ok, R1)")


def show_rules():
    print("""RULES (written exactly)
  R1 rounding: checks use abs tol 1e-9; display 2 decimals round-half-even; --json rounds floats to 12 significant
     digits. JS total += v and Python sum() differ in the last ulp -> the checker loops explicitly (bit-equality).
  R2 hottest: scan i outer, j inner, strict >; FIRST max in row-major order wins; all-zeros -> (0,0,0).
  R3 RUDY fill order: nets in file order; per net tiles = bbox-corner GCells (clamped, min/max) filled i-outer/j-inner;
     share = hpwl / max(1, #tiles); demand accumulates in that order.
  R4 feedback: neighbours (+1,0),(-1,0),(0,+1),(0,-1) strict <; first strictly-smaller overflow wins, else stay;
     move = midpoint toward that tile centre, clamped by the FEEDBACK clamp [0,chip-1] = [0,11]x[0,7].
  R5 heat: t = clamp(cong/maxC, 0, 1), maxC = current max cong (0 -> t=0); >1 is NOT a colour boundary.
     Paper palette stops u=0,1/3,2/3,1 -> #ffffff,#0f6b5c,#b45309,#9f1239; alpha 0.15+0.7u.
  R6 cellGcell: i = clamp(floor(x/cellW), 0, nx-1), same for j (out-of-chip -> edge GCell).
  R7 overflow: perCell = max(0, demand-capacity); count = #cells > 0 STRICT; max init 0; total in scan order.
CLAMPS (two rules, as written, not unified):
  DRAG     [0,11.5]x[0,7.5]  hard-coded in interactive-congestion-lab.js moveSelectedTo (CHIP-0.5).
  FEEDBACK [0,11]x[0,7]      chip-1 in congestion-core.js placementFeedbackLite.
DETERMINISM: no PRNG anywhere — positions come from the instance file; JS and Python agree bit-for-bit per cell (--vs-node).""")


# ---------------- --impl ----------------
IMPL_NAMES = ["cell_gcell", "net_bbox", "hpwl", "deposit_events", "rudy_demand",
              "congestion_map", "overflow_metrics", "hottest", "placement_feedback_lite"]


def load_impl(path):
    spec = importlib.util.spec_from_file_location("learner_cong", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {n: getattr(mod, n, None) for n in IMPL_NAMES}


# ---------------- main ----------------
def main() -> int:
    ap = argparse.ArgumentParser(description="Golden self-check for the congestion heat map (see the module docstring).")
    ap.add_argument("--show", action="store_true", help="print the rules and every table")
    ap.add_argument("--instance", metavar="FILE", help="check only this examples/*.json (default: all of them)")
    ap.add_argument("--impl", metavar="FILE", help="check the functions in FILE (see the docstring for the names)")
    ap.add_argument("--vs-node", action="store_true", help="compare bit-for-bit with platform/assets/congestion-core.js")
    ap.add_argument("--json", action="store_true", help="print the lesson replay JSON (UPGRADE_NOTES.md section 0.4)")
    ap.add_argument("--dump-goldens", action="store_true", help="print the GOLDENS block computed by the reference")
    args = ap.parse_args()

    files = [Path(args.instance)] if args.instance else instance_files()
    insts = [load_instance(f) for f in files]
    if args.instance and not Path(args.instance).exists():
        ap.error(f"no such instance file: {args.instance}")

    if args.dump_goldens:
        import pprint
        block = {i["stem"]: compute_golden(i) for i in insts}
        print("GOLDENS = " + pprint.pformat(block, width=110, sort_dicts=False))
        return 0

    if args.vs_node:
        return vs_node(insts)

    if args.json:
        inst = insts[0] if len(insts) == 1 else next(i for i in insts if i["stem"] == "tiny_cong")
        sys.stdout.write(json.dumps(build_json(inst), indent=1) + "\n")
        return 0

    if args.show:
        show_rules()
        for inst in insts:
            show_instance(inst)

    if args.impl:
        fns = load_impl(args.impl)
        name = args.impl
    else:
        fns = REF_FNS
        name = "reference"
    print(f"checking {name} against the pinned goldens (tol 1e-9, R1)")
    rep = Report()
    for inst in insts:
        check_instance(rep, fns, inst, args.show)
        if not args.impl:
            common_crosscheck(rep, inst)
    return rep.close()


if __name__ == "__main__":
    sys.exit(main())
