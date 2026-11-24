#!/usr/bin/env python3
"""Check built lesson pages and save a contact sheet per page.

  python3 check_lesson.py build/en/index.html build/fr/index.html --sheets build/check
  python3 check_lesson.py build/demo/index.html --data examples/lab06-congestion-demo/data/congestion-check.json
      # with --data: every claim that names a run / deposit event / raw placement is ALSO compared with the
      # congestion checker's --json file at 12-significant-digit precision (rule R1), and an all-equal line is printed

Errors (exit code 1): storyboard anchors that do not resolve, claims that the lab rules contradict,
windows that end before they start, page errors, --data claims that differ from the file.
Warnings (exit 1 only with --strict):
  - a move cut short: two keys of one track closer than the move takes (pose 1.1 s, camera 1.3 s, ...)
  - text on screen for less than --min-text seconds
  - text over text, or text over a node or a block (sampled every 0.5 s and after every key)
  - a frame slower than 8 ms of script on a CPU slowed 6x
Needs: pip install playwright pillow; python3 -m playwright install chromium
"""
from __future__ import annotations

import argparse
import asyncio
import json
import math
import sys
from pathlib import Path


def overlap(a, b) -> float:
    w = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
    h = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
    return max(0.0, w) * max(0.0, h)


def sig12(x):
    """R1: round a float to 12 significant digits, exactly like the checker's --json."""
    if isinstance(x, float):
        if x == 0.0 or not math.isfinite(x):
            return x
        return float(f"{x:.12g}")
    return x


def equal12(got, want) -> bool:
    """Equal at 12-significant-digit precision: the two floats rounded to 12 sig digits are exactly equal."""
    if isinstance(got, bool) or isinstance(want, bool):
        return got == want
    if isinstance(got, (int, float)) and isinstance(want, (int, float)):
        return sig12(float(got)) == sig12(float(want))
    return got == want


def load_congestion_files(paths):
    """The congestion checker's --json files given with --data: {run name: (file, run)} + the file list.
    SA trace files (moves_list) are skipped: the engine already verifies those move by move."""
    runs, files = {}, []
    for p in paths:
        d = json.loads(p.read_text(encoding="utf-8"))
        if not ("gcell" in d and isinstance(d.get("runs"), list)):
            continue
        files.append((p, d))
        for r in d["runs"]:
            runs[r["name"]] = (p, d, r)
    return runs, files


def hpwl_py(nets, pos) -> float:
    s = 0.0
    for net in nets:
        xs = [float(pos[c]["x"]) for c in net if c in pos]
        ys = [float(pos[c]["y"]) for c in net if c in pos]
        if xs:
            s += (max(xs) - min(xs)) + (max(ys) - min(ys))
    return s


def rudy_py(nets, pos, g):
    """R3/R6 in Python, for raw-placement claims compared with the file."""
    def gcell(x, y):
        return (max(0, min(g["nx"] - 1, math.floor(x / g["cellW"]))), max(0, min(g["ny"] - 1, math.floor(y / g["cellH"]))))
    demand = [[0.0] * g["ny"] for _ in range(g["nx"])]
    for net in nets:
        xs = [float(pos[c]["x"]) for c in net if c in pos]
        ys = [float(pos[c]["y"]) for c in net if c in pos]
        if not xs:
            continue
        b = (min(xs), min(ys), max(xs), max(ys))
        wl = (b[2] - b[0]) + (b[3] - b[1])
        i0, j0 = gcell(b[0], b[1])
        i1, j1 = gcell(b[2], b[3])
        tiles = [(i, j) for i in range(min(i0, i1), max(i0, i1) + 1) for j in range(min(j0, j1), max(j0, j1) + 1)]
        share = wl / max(1, len(tiles))
        for i, j in tiles:
            demand[i][j] += share
    return demand


def compare_claims_with_files(claims, runs, files):
    """Every claim that names a run / a deposit event / a raw placement is compared with the checker's --json at
    12-significant-digit precision. Returns (problems, n_compared)."""
    probs, n = [], 0
    for c in claims:
        cl, got = c["claim"], c["got"]
        if not isinstance(got, dict):
            continue
        entry = runs.get(got.get("run")) if got.get("run") else None
        if cl.get("event") is not None and entry:
            p, f, run = entry
            ev = run["events"][cl["event"]]
            want = {"net": ev["net"], "pins": ev["pins"], "bbox": ev["bbox"], "hpwl": ev["hpwl"],
                    "share": ev["share"], "tiles": ev["tiles"], "demandAfter": ev["demandAfter"]}
            for k, w in want.items():
                if k in got:
                    n += 1
                    if not equal12(got[k], w):
                        probs.append(f"claim event {cl['event']} of run {got['run']}: {k} = {got[k]!r}, file {p.name} says {w!r}")
        elif entry:
            p, f, run = entry
            total_hpwl = 0.0
            for e in run["events"]:
                total_hpwl += e["hpwl"]
            demand_total = 0.0
            for col in run["demand"]:
                for v in col:
                    demand_total += v
            want = {"start": total_hpwl, "demand": demand_total, "hottest": run["hottest"],
                    "ovtotal": run["overflow"]["total"], "ovmax": run["overflow"]["max"], "ovcount": run["overflow"]["count"]}
            for k, w in want.items():
                if k in cl and k in got:
                    n += 1
                    if k == "hottest":
                        ok = got.get("hottest") and all(equal12(got["hottest"][q], w[q]) for q in ("i", "j", "v"))
                    else:
                        ok = equal12(got[k], w)
                    if not ok:
                        probs.append(f"claim of run {got['run']}: {k} = {got.get(k)!r}, file {p.name} says {w!r}")
        elif isinstance(cl.get("positions"), dict) and files:
            p, f = files[0]
            pos = cl["positions"]
            g = f["gcell"]
            want = {"hpwl": hpwl_py(f["nets"], pos)}
            if any(k in cl for k in ("demand", "hottest", "ovtotal", "ovmax", "ovcount")):
                dem = rudy_py(f["nets"], pos, g)
                cap = float(f["capacity"])
                per = [[max(0.0, d - cap) for d in col] for col in dem]
                total, mx, count = 0.0, 0.0, 0
                for col in per:
                    for v in col:
                        total += v
                        if v > mx:
                            mx = v
                        if v > 0:
                            count += 1
                cong = [[d / cap for d in col] for col in dem]
                hot = {"i": 0, "j": 0, "v": -1.0}
                for i, col in enumerate(cong):
                    for j, v in enumerate(col):
                        if v > hot["v"]:
                            hot = {"i": i, "j": j, "v": v}
                dt = 0.0
                for col in dem:
                    for v in col:
                        dt += v
                want.update({"demand": dt, "hottest": hot, "ovtotal": total, "ovmax": mx, "ovcount": count})
            for k, w in want.items():
                if k in cl and k in got:
                    n += 1
                    if k == "hottest":
                        ok = got.get("hottest") and all(equal12(got["hottest"][q], w[q]) for q in ("i", "j", "v"))
                    else:
                        ok = equal12(got[k], w)
                    if not ok:
                        probs.append(f"claim positions {json.dumps(pos)}: {k} = {got.get(k)!r}, file {p.name} says {w!r}")
    return probs, n


async def check_page(pw, page_path: Path, sheets: Path | None, min_text: float, perf: bool, data_paths: list[Path] | None = None) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    b = await pw.chromium.launch()
    pg = await b.new_page(viewport={"width": 1280, "height": 1000})
    page_errors = []
    pg.on("pageerror", lambda e: page_errors.append(str(e)))
    await pg.goto(page_path.resolve().as_uri())
    await pg.wait_for_function("window.__lesson !== undefined", timeout=10000)
    await pg.wait_for_timeout(300)
    L = await pg.evaluate("""() => { const x = window.__lesson; return { errors: x.errors, claims: x.claims, tracks: x.tracks,
        move: x.moveSeconds, overlays: x.overlays, duration: x.duration, lang: x.lang, sentences: x.sentences, question: x.question }; }""")
    errs += [f"{e}" for e in L["errors"]]
    errs += [f"page error: {e}" for e in page_errors]
    ok_claims = sum(1 for c in L["claims"] if c["ok"])
    print(f"  claims: {ok_claims}/{len(L['claims'])} match the lab rules")
    fp = await pg.evaluate("window.__lesson.floorplan ? [window.__lesson.floorplan.dataChecked, window.__lesson.floorplan.dataDiffer] : null")
    if fp is not None:
        n, bad = fp
        tail = " (none given: build with --data)" if n == 0 else (", all equal" if bad == 0 else f", {bad} DIFFER (see errors)")
        print(f"  floorplan: {n} tree(s) from the lab checker re-packed by the engine{tail}")

    pl = await pg.evaluate("window.__lesson.placement ? (({dataChecked, dataDiffer, dataMoves, dataEvents, seedsChecked, seedsDiffer}) => ({dataChecked, dataDiffer, dataMoves, dataEvents, seedsChecked, seedsDiffer}))(window.__lesson.placement) : null")
    if pl is not None:
        tail = " (none given: build with --data)" if pl["dataChecked"] == 0 else (", all equal" if pl["dataDiffer"] == 0 else f", {pl['dataDiffer']} DIFFER (see errors)")
        print(f"  placement: {pl['dataChecked']} run(s), {pl['dataMoves']} move(s) of the lab checker replayed by the engine{tail}")
        if pl.get("dataEvents"):
            tail = ", all equal" if pl["dataDiffer"] == 0 else f", {pl['dataDiffer']} DIFFER (see errors)"
            print(f"  placement: {pl['dataEvents']} deposit event(s) of the lab checker replayed by the engine{tail}")
        if pl["seedsChecked"]:
            print(f"  placement: {pl['seedsChecked']} seed(s) compared with the checker, {pl['seedsDiffer']} differ")

    # v5.1 --data: compare every run / event / raw-placement claim with the checker's --json at 12 sig digits
    if data_paths:
        runs, files = load_congestion_files(data_paths)
        if runs:
            probs, n_cmp = compare_claims_with_files(L["claims"], runs, files)
            names = ", ".join(p.name for p, _ in files)
            n_runs = len(runs)
            n_ev = sum(len(r["events"]) for _, _, r in runs.values())
            tail = "all equal" if not probs else f"{len(probs)} DIFFER (see errors)"
            print(f"  --data {names}: {n_runs} run(s), {n_ev} deposit event(s) in the file; {n_cmp} claim value(s) compared at 12 significant digits: {tail}")
            errs += probs

    # 1. moves cut short
    for name, keys in L["tracks"].items():
        need = L["move"].get(name, 1.0)
        for (t0, r0), (t1, r1) in zip(keys, keys[1:]):
            if 0 < t1 - t0 < need * 0.9:
                warns.append(f"{name}: '{r1}' at {t1:.2f}s starts {t1 - t0:.2f}s after '{r0}' (the move takes {need}s): "
                             f"add a pause after that sentence, or move one key")
    # 2. short text
    for o in L["overlays"]:
        if o["b"] < 1e8 and o["b"] - o["a"] < min_text:
            warns.append(f"text '{o['label']}' is on screen {o['b'] - o['a']:.2f}s (from {o['a']:.2f}s); keep it at least {min_text}s")
    # 3. overlaps
    times = set()
    for o in L["overlays"]:
        end = min(o["b"], L["duration"])
        for t in (o["a"] + 0.6, (o["a"] + end) / 2, end - 0.4):
            if o["a"] < t < end:
                times.add(round(t, 2))
    for keys in L["tracks"].values():
        for t, _ in keys:
            times.add(round(t + 1.4, 2))
    t = 0.0
    while t < L["duration"]:
        times.add(round(t, 2)); t += 0.5
    seen = set()
    for t in sorted(times):
        if t > L["duration"]:
            continue
        bx = await pg.evaluate(f"(() => {{ window.__lesson.render({t}); return window.__lesson.boxes(); }})()")
        boxes = bx["boxes"]
        texts = [x for x in boxes if x["kind"] == "overlay"]
        nodes = [x for x in boxes if x["kind"] == "node"]
        for i, a in enumerate(texts):
            if a["x"] < -2 or a["y"] < -2 or a["x"] + a["w"] > bx["stage"]["w"] + 2 or a["y"] + a["h"] > bx["stage"]["h"] + 2:
                k = ("out", a["label"])
                if k not in seen:
                    seen.add(k); warns.append(f"{t:6.2f}s text '{a['label']}' runs off the stage")
            for c in texts[i + 1:]:
                ov = overlap(a, c)
                if ov > 0.04 * min(a["w"] * a["h"], c["w"] * c["h"]):
                    k = ("tt", a["label"], c["label"])
                    if k not in seen:
                        seen.add(k); warns.append(f"{t:6.2f}s text over text: '{a['label']}' and '{c['label']}'")
            for n in nodes:
                if overlap(a, n) > 0.15 * n["w"] * n["h"]:
                    k = ("tn", a["label"], n["label"])
                    if k not in seen:
                        seen.add(k); warns.append(f"{t:6.2f}s text '{a['label']}' covers node {n['label']}")
    # 4. speed on a slow machine
    if perf:
        cdp = await pg.context.new_cdp_session(pg)
        await cdp.send("Emulation.setCPUThrottlingRate", {"rate": 6})
        r = await pg.evaluate("""() => { const L = window.__lesson, T = [];
            for (let t = 0; t < L.duration; t += 0.25) { const a = performance.now(); L.render(t); T.push(performance.now() - a); }
            T.sort((x, y) => x - y); return { med: T[T.length >> 1], p95: T[Math.floor(T.length * 0.95)], max: T[T.length - 1] }; }""")
        await cdp.send("Emulation.setCPUThrottlingRate", {"rate": 1})
        print(f"  speed (CPU slowed 6x): script per frame median {r['med']:.2f} ms, 95% under {r['p95']:.2f} ms, worst {r['max']:.2f} ms")
        if r["p95"] > 8:
            warns.append(f"slow frames on a slow CPU: 95% of frames under {r['p95']:.1f} ms (aim for 8 ms)")
    # 5. contact sheet
    if sheets:
        from PIL import Image, ImageDraw
        sheets.mkdir(parents=True, exist_ok=True)
        pick = sorted({round(o["a"] + 0.9, 2) for o in L["overlays"] if o["a"] + 0.9 < min(o["b"], L["duration"])})
        if len(pick) > 32:
            step = len(pick) / 32
            pick = [pick[int(i * step)] for i in range(32)]
        stage = await pg.query_selector(".stage")
        await pg.evaluate("window.__lesson.setRecording(true)")  # no colour fades: each shot shows the settled picture
        ims = []
        for t in pick:
            await pg.evaluate(f"window.__lesson.render({t})")
            await pg.wait_for_timeout(60)
            f = sheets / f"_{L['lang']}_{t:07.2f}.png"
            await stage.screenshot(path=str(f))
            im = Image.open(f).convert("RGB"); im = im.resize((im.width // 2, im.height // 2))
            ImageDraw.Draw(im).text((8, im.height - 18), f"{t:.1f}s", fill=(220, 0, 0))
            ims.append(im); f.unlink()
        if ims:
            w, h = ims[0].size; cols = 4; rows = (len(ims) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w, rows * h), "white")
            for i, im in enumerate(ims):
                sheet.paste(im, ((i % cols) * w, (i // cols) * h))
            out = sheets / f"sheet-{L['lang']}.png"
            sheet.save(out)
            print(f"  contact sheet: {out} ({len(ims)} frames, one just after each text appears)")
    await b.close()
    print(f"  {L['lang']}: {L['duration']:.1f} s, {len(L['sentences'])} sentences, {len(L['overlays'])} texts, question at "
          f"{L['question']:.1f}s" if L["question"] is not None else "")
    return errs, warns


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pages", nargs="+", type=Path)
    ap.add_argument("--sheets", type=Path, help="folder for the contact sheets")
    ap.add_argument("--min-text", type=float, default=2.0)
    ap.add_argument("--no-perf", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warnings also fail")
    ap.add_argument("--data", type=Path, nargs="*", default=[], help="the checker --json file(s) the pages were built with (--data of build_lesson.py): congestion --json files are compared claim by claim at 12 significant digits")
    a = ap.parse_args()
    from playwright.async_api import async_playwright
    total_e = total_w = 0
    async with async_playwright() as pw:
        for p in a.pages:
            print(f"== {p}")
            e, w = await check_page(pw, p, a.sheets, a.min_text, not a.no_perf, a.data)
            for x in e:
                print(f"  ERROR   {x}")
            for x in w:
                print(f"  warning {x}")
            if not e and not w:
                print("  no problems")
            total_e += len(e); total_w += len(w)
    print(f"\n{total_e} error(s), {total_w} warning(s)")
    return 1 if total_e or (a.strict and total_w) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
