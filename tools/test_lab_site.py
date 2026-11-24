#!/usr/bin/env python3
"""Browser test of the BUILT site's lab (congestion heat map, Lab 06), in English and French.

It is the course's own platform/tools/congestion-map/tests/test_lab_playwright.py (same learner actions, same cases:
every challenge passes when solved with the real controls, and never on page load, from the preset seed, from the
reveal, from one Run feedback click alone, from a wrong map, or after an edit that cancels a method button's credit;
the colour checks: the heat tiles are painted with R5 (t = clamp(cong/maxC), paper palette) and oversubscription is
not a colour boundary — after one feedback pass no tile is oversubscribed yet the hottest tile still paints crimson;
the script's numbers on the page: seed hottest (1,0) @ 3.50, A dragged across x=6 -> total 7.50 count 2, one feedback
click -> total 0.00 count 0 hottest (2,0) @ 1.00) run against docs/ and docs/fr/. The actions use element ids where
they exist (#lab-chal-sel, #lab-chal-start, #lab-chal-check, #lab-status, #lab-starter, #cm-in-*, canvas) and the
button labels per language from the LANGS table (cell buttons A-F and the arrows are language-neutral); the metrics
readout lines (selected:, HPWL:, overflow total:, hottest:, capacity:) are program output and stay English in both
languages. The LANGS table also holds the PASS word and the English snippets that must NOT be left over in the French
lab.

    python3 ~/.vibe/skills/lesson-animator/scripts/serve.py docs 8090      # from this repo's root, in another shell
    python3 tools/test_lab_site.py [--base http://127.0.0.1:8090] [--lang en|fr|both] [--teacher ../eda-learning-lab6-cg] [--headed]

Needs: pip install playwright pillow && python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--base", default="http://127.0.0.1:8090")
ap.add_argument("--lang", choices=["en", "fr", "both"], default="both")
ap.add_argument("--teacher", default=HERE.parent / "eda-learning-lab6-cg", type=Path)
ap.add_argument("--headed", action="store_true")
args = ap.parse_args()
BASE = args.base.rstrip("/")

# what the page says in each language
LANGS = {
    "en": {"prefix": "", "html_lang": "en", "status_pass": "PASS",
           "run_feedback": "Run feedback", "reveal": "Reveal golden (study)",
           "leftover": []},
    "fr": {"prefix": "fr/", "html_lang": "fr", "status_pass": "RÉUSSI",
           "run_feedback": "Lancer la rétroaction", "reveal": "Révéler le golden (étude)",
           "leftover": ["Skip to content", "Interactive tool", "Pick a challenge", "Reset workspace", "Show hint", "Hide hint",
                        "Next challenge", "Stop checking", "Run feedback", "Reveal golden", "Hide golden", "Challenges",
                        "Load starter example", "Idle", "Not yet", "Starter loaded", "Challenge armed", "Load a challenge",
                        "Graph", "Reference / metrics", "Hint:", "Type your answers", "view:", "Your workspace",
                        "what you built", "hottest tile", "its congestion", "congestion at tile", "R2 rule picks",
                        "total overflow after the pass", "your placement", "revealed spread", "editing after a method button",
                        "PASS", "cleared", "Read the hottest tile", "own matrix", "Drag A across", "Build a tie",
                        "Cool the peak", "Cooler:", "Move the hotspot", "bounded together", "read the cooled map"]},
}

# ---------------- learner actions (element ids; button labels per language) ----------------
SEED = {"A": (4, 2), "B": (5, 2), "C": (4, 3), "D": (5, 3), "E": (4.5, 2.5), "F": (5.5, 2.5)}
TIE = {"A": (2, 2), "B": (4, 2), "C": (2, 6), "D": (4, 6), "E": (3, 4), "F": (3, 4)}
JOINT = {"A": (5, 2), "B": (7, 2), "C": (5, 3), "D": (7, 3), "E": (5.5, 2.5), "F": (6.5, 2.5)}
EDGE = {"A": (1, 1), "B": (8, 1), "C": (1, 5), "D": (8, 5), "E": (1, 3), "F": (2, 3)}


def btn(pg, T, text):
    pg.locator(f'#lab-root button:text-is("{text}")').first.click()


def chip_to_client(pg, x, y):
    return pg.evaluate(
        """([x, y]) => {
          const c = document.querySelector("#lab-root canvas");
          const d = c.__draw;
          const r = c.getBoundingClientRect();
          const s = d.toScreen(x, y);
          return [r.left + s.sx, r.top + s.sy];
        }""",
        [x, y],
    )


def click_chip(pg, x, y):
    cx, cy = chip_to_client(pg, x, y)
    pg.mouse.click(cx, cy)


def select_cell(pg, T, cid):
    btn(pg, T, cid)


def nudge(pg, T, arrow, times):
    for _ in range(times):
        btn(pg, T, arrow)


def move_cell_exact(pg, T, cid, target):
    sx, sy = SEED[cid]
    tx, ty = target
    select_cell(pg, T, cid)
    dx = round((tx - sx) / 0.5)
    dy = round((ty - sy) / 0.5)
    if dx > 0:
        nudge(pg, T, "→", dx)
    elif dx < 0:
        nudge(pg, T, "←", -dx)
    if dy > 0:
        nudge(pg, T, "↑", dy)
    elif dy < 0:
        nudge(pg, T, "↓", -dy)


def place_all(pg, T, placement):
    for cid, target in placement.items():
        move_cell_exact(pg, T, cid, target)


def drag_a_to(pg, T, x, y):
    select_cell(pg, T, "A")
    click_chip(pg, x, y)


def fill(pg, field, value):
    pg.fill(f"#cm-in-{field}", value)


def type_answers(**kw):
    def act(pg, T):
        for f, v in kw.items():
            fill(pg, f, v)
    return act


def seq(*acts):
    def act(pg, T):
        for a in acts:
            a(pg, T)
    return act


nothing = lambda pg, T: None  # noqa: E731


def make_reveal(T):
    def act(pg, _T):
        btn(pg, _T, T["reveal"])
    return act


def make_feedback(T):
    def act(pg, _T):
        btn(pg, _T, T["run_feedback"])
    return act


def run_challenge(pg, T, cid, act):
    pg.select_option("#lab-chal-sel", cid)
    pg.click("#lab-chal-start")
    act(pg, T)
    pg.click("#lab-chal-check")
    return pg.inner_text("#lab-status").strip() == T["status_pass"]


# ---------------- cases: challenge -> [(label, actions, expected PASS?)] ----------------

def cases_for(T):
    reveal = make_reveal(T)
    feedback = make_feedback(T)
    return {
        "read-hot": [
            ("type 1,0 and 3.5 on the seed", type_answers(hotTile="1,0", hotVal="3.5"), True),
            ("page load (no typing)", nothing, False),
            ("wrong tile 2,0 @ 3.33", type_answers(hotTile="2,0", hotVal="3.33"), False),
            ("reveal, then seed values", seq(reveal, type_answers(hotTile="1,0", hotVal="3.5")), False),
            ("one Run feedback click, no typing", feedback, False),
        ],
        "own-matrix": [
            ("type 3.5 and 0 on the seed", type_answers(tile10="3.5", tile20="0"), True),
            ("page load (no typing)", nothing, False),
            ("wrong map: A dragged to (6.5,2), seed values typed",
             seq(lambda pg, T: drag_a_to(pg, T, 6.5, 2), type_answers(tile10="3.5", tile20="0")), False),
            ("reveal, then seed values", seq(reveal, type_answers(tile10="3.5", tile20="0")), False),
        ],
        "boundary-drag": [
            ("drag A to (6.5,2) via canvas click", lambda pg, T: drag_a_to(pg, T, 6.5, 2), True),
            ("nudge A to (6.5,2) exactly", lambda pg, T: move_cell_exact(pg, T, "A", (6.5, 2)), True),
            ("page load", nothing, False),
            ("wrong drag A to (6.9,2)", lambda pg, T: drag_a_to(pg, T, 6.9, 2), False),
            ("reveal", reveal, False),
            ("one Run feedback click", feedback, False),
        ],
        "tie-break": [
            ("symmetric placement, type 0,0", seq(lambda pg, T: place_all(pg, T, TIE), type_answers(tieTile="0,0")), True),
            ("page load", nothing, False),
            ("symmetric placement, wrong pick 1,1", seq(lambda pg, T: place_all(pg, T, TIE), type_answers(tieTile="1,1")), False),
            ("seed (no tie), type 1,0", type_answers(tieTile="1,0"), False),
            ("reveal + type 0,0", seq(reveal, type_answers(tieTile="0,0")), False),
            ("one Run feedback click", feedback, False),
        ],
        "cool-max": [
            ("joint placement by nudges", lambda pg, T: place_all(pg, T, JOINT), True),
            ("page load", nothing, False),
            ("reveal (peak 3.33)", reveal, False),
            ("one Run feedback click (method)", feedback, False),
        ],
        "cool-2": [
            ("joint placement (peak 2.5, total 6)", lambda pg, T: place_all(pg, T, JOINT), True),
            ("page load", nothing, False),
            ("reveal (total 22)", reveal, False),
            ("one Run feedback click", feedback, False),
        ],
        "edge-hot": [
            ("edge placement by nudges", lambda pg, T: place_all(pg, T, EDGE), True),
            ("page load", nothing, False),
            ("reveal (hottest i=2)", reveal, False),
            ("one Run feedback click", feedback, False),
        ],
        "joint-bound": [
            ("joint placement (2.5 / 6 / HPWL 10)", lambda pg, T: place_all(pg, T, JOINT), True),
            ("page load", nothing, False),
            ("reveal (total 22)", reveal, False),
            ("one Run feedback click (HPWL 3.5, method)", feedback, False),
        ],
        "feedback-cooled": [
            ("Run feedback once, type 0 / 2,0 / 1", seq(make_feedback(T), type_answers(fbTotal="0", fbTile="2,0", fbVal="1")), True),
            ("ONE Run feedback click, no typing — must NOT pass", make_feedback(T), False),
            ("Run feedback, then edit A (credit cancelled), correct typing",
             seq(make_feedback(T), lambda pg, T: move_cell_exact(pg, T, "A", (4.5, 2)), type_answers(fbTotal="0", fbTile="2,0", fbVal="1")), False),
            ("Run feedback, wrong typing", seq(make_feedback(T), type_answers(fbTotal="0", fbTile="1,0", fbVal="0.75")), False),
            ("page load", nothing, False),
            ("reveal", reveal, False),
        ],
    }


# ---------------- colour checks (R5) ----------------

def tile_colour(pg, i, j):
    return pg.evaluate(
        """async ([i, j]) => {
          const M = await import("./congestion-map-lab-model.js");
          const c = document.querySelector("#lab-root canvas");
          const d = c.__draw;
          const k = c.width / c.clientWidth;
          const ctx = c.getContext("2d");
          const counts = {};
          for (let a = 1; a <= 6; a++) for (let b = 1; b <= 4; b++) {
            const s = d.toScreen(i * 3 + (a / 7) * 3, j * 4 + (b / 5) * 4);
            const dd = ctx.getImageData(Math.round(s.sx * k), Math.round(s.sy * k), 1, 1).data;
            const key = dd[0] + "," + dd[1] + "," + dd[2];
            counts[key] = (counts[key] || 0) + 1;
          }
          const mode = Object.entries(counts).sort((x, y) => y[1] - x[1])[0][0].split(",").map(Number);
          const cong = d.cong;
          let maxC = 0; for (const col of cong) for (const v of col) if (v > maxC) maxC = v;
          const t = maxC > 0 ? Math.max(0, Math.min(1, cong[i][j] / maxC)) : 0;
          const hc = M.heatColor(t);
          const expected = [hc.r, hc.g, hc.b].map((ch) => Math.round(hc.a * ch + (1 - hc.a) * 255));
          return { mode, expected, t };
        }""",
        [i, j],
    )


def near(a, b, tol=3):
    return len(a) == len(b) and all(abs(x - y) <= tol for x, y in zip(a, b))


rows = []


def run_lang(b, lang: str, T: dict) -> None:
    url = f"{BASE}/{T['prefix']}tools/congestion-map/index.html"
    pg = b.new_page(viewport={"width": 1400, "height": 3000})
    errors = []
    pg.on("console", lambda m: m.type == "error" and errors.append(m.text))
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.on("requestfailed", lambda r: errors.append(f"request failed {r.url}"))
    pg.on("response", lambda r: r.status >= 400 and errors.append(f"HTTP {r.status}: {r.url}"))
    pg.on("request", lambda r: not r.url.startswith((BASE, "data:", "blob:")) and errors.append(f"external: {r.url}"))
    pg.goto(url, wait_until="networkidle")
    pg.add_style_tag(content="html{scroll-behavior:auto!important}")
    pg.wait_for_selector("#lab-root canvas")

    def row(cid, kind, label, ok):
        rows.append((lang, cid, kind, label, bool(ok)))

    row("page", "page", "html lang attribute", pg.get_attribute("html", "lang") == T["html_lang"])
    ids = pg.eval_on_selector_all("#lab-chal-sel option", "os => os.map(o => o.value)")
    CASES = cases_for(T)
    row("page", "page", "9 challenges in the menu", len(ids) == 9 and sorted(ids) == sorted(CASES))
    row("page", "page", "Check is off until Start (page load)", pg.is_disabled("#lab-chal-check"))
    row("page", "page", "page load shows the seed: hottest (1,0) @ 3.50",
        "hottest: (1,0) @ 3.50" in pg.inner_text(".metrics-body"))

    # ---- colour checks on the seed (page load) ----
    c10 = tile_colour(pg, 1, 0)
    c00 = tile_colour(pg, 0, 0)
    row("(colour)", "colour", "seed: tile (1,0) t=1 crimson, tile (0,0) t=0 white",
        near(c10["mode"], c10["expected"]) and near(c00["mode"], c00["expected"]) and c10["t"] == 1.0 and c00["t"] == 0.0)
    row("(colour)", "colour", "seed tile (1,0) ~ #9f1239@0.85 over white (173,54,87)", near(c10["mode"], [173, 54, 87], tol=4))

    # ---- S26: drag A across the boundary x=6 -> count 2, total overflow 7.5 ----
    pg.select_option("#lab-chal-sel", "boundary-drag")
    pg.click("#lab-chal-start")
    move_cell_exact(pg, T, "A", (6.5, 2))
    m = pg.inner_text(".metrics-body")
    row("(numbers)", "S26", "A at (6.5,2) across x=6: total 7.50, count 2, hottest (1,0) shown",
        "overflow total: 7.50" in m and "count: 2" in m and "hottest: (1,0)" in m)

    # ---- one Run feedback click: numbers + colours + the must-NOT-pass case ----
    pg.select_option("#lab-chal-sel", "feedback-cooled")
    pg.click("#lab-chal-start")
    btn(pg, T, T["run_feedback"])
    m = pg.inner_text(".metrics-body")
    row("(numbers)", "S27", "one feedback click: total 0.00, count 0, hottest (2,0) @ 1.00 shown",
        "overflow total: 0.00" in m and "count: 0" in m and "hottest: (2,0) @ 1.00" in m)
    c20 = tile_colour(pg, 2, 0)
    row("(colour)", "colour", "after feedback: count 0 but tile (2,0) still crimson (t = cong/maxC, not capacity)",
        near(c20["mode"], c20["expected"]) and c20["t"] == 1.0 and near(c20["mode"], [173, 54, 87], tol=4))
    pg.click("#lab-chal-check")
    row("feedback-cooled", "negative", "ONE Run feedback click then Check (no typing) — must NOT pass",
        pg.inner_text("#lab-status").strip() != T["status_pass"])

    # ---- per-challenge cases ----
    for cid, cases in CASES.items():
        for label, act, want in cases:
            got = run_challenge(pg, T, cid, act)
            row(cid, "positive" if want else "negative", label, got == want)

    # ---- the starter reset stops checking instead of passing anything ----
    pg.select_option("#lab-chal-sel", "cool-max")
    pg.click("#lab-chal-start")
    pg.click("#lab-starter")  # "Reset workspace" / "Réinitialiser l'espace de travail"
    row("(all)", "negative", "Reset workspace preset (seed) — Check disabled, nothing passes",
        pg.is_disabled("#lab-chal-check") and "hottest: (1,0) @ 3.50" in pg.inner_text(".metrics-body"))

    # ---- leftover English in the French lab (page in its states: seed, a feedback run, the Check line, a challenge) ----
    pg.select_option("#lab-chal-sel", "feedback-cooled")
    pg.click("#lab-chal-start")
    btn(pg, T, T["run_feedback"])
    type_answers(fbTotal="0", fbTile="2,0", fbVal="1")(pg, T)
    pg.click("#lab-chal-check")
    page_text = pg.inner_text("body")
    left = [w for w in T["leftover"] if w in page_text]
    row("page", "page", ("no English left in the French lab" if lang == "fr" else "the English lab shows its English text")
        + (f" (left: {left})" if left else ""),
        (not left) if lang == "fr" else ("Challenges" in page_text and "PASS" in page_text))
    row("page", "page", "no console error, no failed request, no HTTP error, 0 external requests", not errors)
    if errors:
        for e in errors[:5]:
            print("  error:", e)
    pg.close()


with sync_playwright() as p:
    b = p.chromium.launch(headless=not args.headed)
    for lang in (["en", "fr"] if args.lang == "both" else [args.lang]):
        run_lang(b, lang, LANGS[lang])
    b.close()

fails = 0
for lang, cid, kind, label, good in rows:
    print(f"{lang:3} {'ok  ' if good else 'FAIL'}  {cid:<16} {kind:<9} {label}")
    fails += not good
for lang in sorted({r[0] for r in rows}):
    mine = [r for r in rows if r[0] == lang]
    bad = sum(1 for r in mine if not r[4])
    print(f"\n[{lang}] {len(mine) - bad} ok, {bad} FAIL  ({sum(1 for r in mine if r[2] == 'positive')} positive, "
          f"{sum(1 for r in mine if r[2] == 'negative')} negative, the rest page, colour and numbers)")
print(f"\n{len(rows) - fails} ok, {fails} FAIL in all")
sys.exit(1 if fails else 0)
