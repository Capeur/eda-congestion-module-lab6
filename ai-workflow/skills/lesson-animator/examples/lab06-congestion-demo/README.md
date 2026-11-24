# Example: placement scene heat-grid overlay, Lab 06 (congestion map), engine demo, EN

**This is a demo of the engine, not a lesson of the lab.** One short part (one slide, 10 sentences, ~33 s with draft
timing): the six seed deposit events of the congestion checker paint the GCell heat grid tile by tile, the `demand`
counter follows (1, 2, 3, 4, 6, 7 on the seed), and the final hottest tile (1,0) = 3.5 is ringed. In the try-it
panel, dragging cell A to (6.5, 2) — across the GCell boundary x = 6 — shows wirelength 11.5 with **overflow 7.5
over 2 tiles** (the `boundary_move` case), next to the wirelength.

New in engine v5.1 (all of it exercised here):

- `placement.heat` (from `--data`, or pinned by the storyboard): the GCell lattice `nx, ny, cellW, cellH` drawn as
  per-axis grid lines on the floor, one tile per GCell painted with the `--json` heat palette (paper stops
  `#ffffff, #0f6b5c, #b45309, #9f1239`, alpha 0.15 + 0.7u), `capacity`, and `maxC` from the file
  (R5: `t = clamp(cong/maxC, 0, 1)` — oversubscription is not a colour boundary).
- the `deposit` timeline key replays the run's ordered deposit events: each event repaints the tiles from its
  `demandAfter`, accumulating to exactly the `--json` final maps.
- counter metrics `demand`, `ovtotal`, `ovmax`, `ovcount`, `hottestTile` follow the replay.
- `highlight` accepts tile ids `"t{i},{j}"` alongside cell ids.
- the try-it readout gains the total overflow + oversubscribed count (R7, strict > 0) beside the wirelength.
- cells draw at their `--json` widths (`placement.sizes`: 2 for A–D, 1 for E–F).

Data (`data/congestion-check.json`): the Lab 06 checker's `--json`, generated READ-ONLY from the teacher clone:

```bash
cd ../eda-learning-lab6-cg && PYTHONDONTWRITEBYTECODE=1 python3 -B \
  courses/learn_congestion/module02-05-congestion-map/examples/congestion_map_check.py --json \
  > <this folder>/data/congestion-check.json     # instance tiny_cong: runs congested_seed + spread, 6 events each
```

## Commands (from a site repo; P=~/eda-venv/bin/python, SK=this skill)
```bash
export PYTHONDONTWRITEBYTECODE=1
P=$HOME/eda-venv/bin/python; SK=<this skill>; EX=$SK/examples/lab06-congestion-demo
$P $SK/scripts/draft_timing.py --transcript $EX/transcript-en.md --slides 1-1 --lang en --storyboard $EX/storyboard.json \
    --out-audio build/lab06-demo/draft-en.m4a --out-timing build/lab06-demo/timing-en.json
$P $SK/scripts/build_lesson.py --storyboard $EX/storyboard.json --timing build/lab06-demo/timing-en.json \
    --audio build/lab06-demo/draft-en.m4a --lang en --out build/lab06-demo/en --fonts site_src/fonts \
    --storage-key lab06-lesson-speed --data $EX/data/congestion-check.json
$P $SK/scripts/check_lesson.py build/lab06-demo/en/index.html --data $EX/data/congestion-check.json --sheets build/lab06-demo/check
```
The audio is silent (draft timing). For a voice, replace `draft_timing.py` with `voice_build.py --voice ... --rate=-4%`.

## Results (2026-11-23, draft timing)
- Claims 8/8; 2 static congestion runs, 12 deposit events replayed by the engine: all equal; `--data`: 52 claim
  values compared with the file at 12 significant digits: all equal. 0 errors, 0 warnings.
- Replay probed in Chromium: deposit count 0→6 in event order, demand counter 1, 2, 3, 4, 6, 7, hottest-tile counter
  "1,0 3.5" with the `t1,0` ring from the "hottest" word; tiles painted with the paper palette (u relative to the
  file's maxC 3.5).
- Try-it panel: dragging A to (6.5, 2) gives "wirelength 11.5 (lesson: 7.0); overflow 7.5 over 2 tile(s)" — the
  boundary_move numbers, computed live with the file's capacity and the R7 strict > 0 rule.
- Cells A–D draw 2× wide, E–F 1× (placement.sizes from the `--json` cells).
- Regression: `examples/lab07-placement-demo/` rebuilt with this engine: 9/9 claims, 3 runs / 420 moves all equal,
  200 seeds 0 differ, 0 errors, 0 warnings (EN and FR) — the heat code is a no-op without a `heat` block.
