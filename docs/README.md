# Module 02-05: Congestion heat map

**Module id:** `module02-05-congestion-map`  
**Kind:** `lab` · Primary lab: `congestion-map` · **ref**

[← Probabilistic](../module02-03-probabilistic-demand/README.md) · [Course README](../README.md) · [Overflow →](../module02-07-overflow-metrics/README.md)

## Outcomes

After this module you can: **build a congestion heat map as demand/capacity per GCell, name the hottest tile with a
written tie-break, and read the overflow metrics (total / max / count) — including how capacity and one cell move
flip them.**

## Two tracks (pick one or both)

### Track A — Implement (hands-on)

1. Open [EXAMPLES.md](EXAMPLES.md); the answer key is `examples/congestion_map_check.py` and the instances are
   `examples/*.json` (`tiny_cong.json` plus three small instances that each flip one result).
2. Implement the nine API functions (same signatures as `common/solvers.py`) and check them:

   ```bash
   # from this module folder — standard library only
   python3 examples/congestion_map_check.py                  # all PASS (every examples/*.json)
   python3 examples/congestion_map_check.py --show           # the written rules R1–R7 and every golden table
   python3 examples/congestion_map_check.py --impl my_cong.py  # YOUR functions (SKIP for missing ones)
   python3 examples/congestion_map_check.py --vs-node        # bit-for-bit vs platform/assets/congestion-core.js
   python3 examples/congestion_map_check.py --json           # the replay file for the animated lessons
   ```

   The module is fully deterministic (no PRNG anywhere): Python and JavaScript agree **bit-for-bit per cell**.
   `examples/wrong/tie_last_wins.py` is a port that breaks one written rule and must FAIL.
3. Complete [CHECKLIST.md](CHECKLIST.md).
4. Optional self-check: `./scripts/module.sh 02-05 --check` (from course root).

### Track B — Browser lab (online)

1. Local: [http://127.0.0.1:8080/tools/congestion-map/](http://127.0.0.1:8080/tools/congestion-map/)
2. Live: [https://universal-verification-methodology.github.io/learning/tools/congestion-map/](https://universal-verification-methodology.github.io/learning/tools/congestion-map/)
3. Tools shelf: open `congestion-map` from the platform tools index
4. Load the **starter congestion** instance, run the estimator, inspect overflow metrics; move cells (the drag
   clamps at x = 11.5, y = 7.5) and watch the hottest tile move.
5. Check off Track B items in [CHECKLIST.md](CHECKLIST.md).

> Concept labs teach congestion literacy on a tiny GCell grid — not production global routers.

## Media

| Artifact | Path |
|----------|------|
| Transcript | [transcript.md](transcript.md) |
| Outline | [outline.yaml](outline.yaml) |
| Slides | [slides.pptx](slides.pptx) · [slides.pdf](slides.pdf) |
| Video | [video.mp4](video.mp4) |
| Quiz | [quiz.json](quiz.json) |

## Files

```
module02-05-congestion-map/
├── README.md
├── CHECKLIST.md
├── EXAMPLES.md            ← goal, rules R1–R7, golden tables, starter prompts
├── quiz.json              ← object format: {id, title, items[{id,type,prompt,choices,answer,explain}]}
├── transcript.md
├── outline.yaml
├── examples/
│   ├── congestion_map_check.py   ← golden self-check (--show/--impl/--vs-node/--json)
│   ├── cong_node.mjs             ← --vs-node helper (imports platform/assets/congestion-core.js)
│   ├── tiny_cong.json            ← 4×2 grid, both placements
│   ├── cap_one.json              ← capacity 2→1: no tile flips, ratios double
│   ├── boundary_move.json        ← one cell across a GCell boundary: count 1→2
│   ├── cap_below_one.json        ← capacity below 1: count 0→2
│   └── wrong/tie_last_wins.py    ← must FAIL on the R2 tie probe
└── assets/               ← _demo.sh, steps/, lab-starter.png, STEPS.md
```
