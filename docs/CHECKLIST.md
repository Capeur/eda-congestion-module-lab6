# Checklist — Congestion heat map

## Track A — Implement (`examples/congestion_map_check.py`)

- [ ] **The ratio**: on the congested seed, GCell (1,0) has demand 7 and congestion **3.50** (7 / capacity 2); values above 1 are oversubscribed
- [ ] **RUDY fill order (R3)**: nets in file order, tiles i-outer / j-inner, share = HPWL / max(1, #tiles) — on the spread placement net A–B (HPWL 7) gives 2.3333 to each of (0,0), (1,0), (2,0)
- [ ] **Hottest tie-break (R2)**: scan i outer / j inner, strict `>` — `[[1,2],[0,0],[0,0],[2,0]]` → **(0,1)**, all-zeros → (0,0,0); spread hottest is **(2,0) @ 3.33**, seed hottest **(1,0) @ 3.50**
- [ ] **Overflow (R7)**: perCell = max(0, demand − capacity); count is strict `> 0` — seed: total/max/count **5/5/1**; spread: **22/4.67/6** (raw JS total 22.000000000000004, R1)
- [ ] **Peak vs total**: spreading lowers the peak (3.50 → 3.33) but raises total overflow (5 → 22) and count (1 → 6); HPWL 7 → 34
- [ ] **Capacity flips**: 2→1 flips **no** tile (count 6→6 spread, 1→1 seed; ratios double); 2→5 on spread flips count **6→4** — tiles (1,0) and (1,1) drop out
- [ ] **One cell across a boundary** (`examples/boundary_move.json`): A (4,2)→(6.5,2) flips overflow count 1→2, total 5→7.5
- [ ] **Capacity below 1** (`examples/cap_below_one.json`): share 0.5 tiles are fine at capacity 1, overflow exactly 0 at 0.5 (strict count), count 2 at 0.4
- [ ] **The two clamps as written**: drag [0, 11.5]×[0, 7.5] (interactive lab), feedback [0, 11]×[0, 7] (chip−1) — probes F (15,2.5)→(11,4.25), F (4.5,20)→(6,7)
- [ ] **Heat is relative to the current max (R5)**: t = clamp(cong / maxC, 0, 1); after one feedback pass the hottest tile (2,0) @ exactly 1.0 still paints the top palette colour
- [ ] **Feedback (R4)**: one pass on the seed zeroes the overflow (5/5/1 → 0/0/0), neighbours (+1,0), (−1,0), (0,+1), (0,−1) strict `<`
- [ ] Reversed inputs: nets reversed → same tiles per net, demand within 1e-9, same count/hottest; positions dict reversed → identical feedback
- [ ] Ran `examples/wrong/tie_last_wins.py` with `--impl` and saw it FAIL on the R2 tie probe (`got [3, 0, 2.0]`)
- [ ] `python3 examples/congestion_map_check.py` prints all PASS; `--impl my_cong.py` prints no FAIL; `--vs-node` agrees bit-for-bit per cell; `--json` emits the lesson replay file

## Track B — Browser lab (`congestion-map`)

- [ ] Opened the lab (local or live) and loaded the starter congestion instance
- [ ] Read the heat legend: colours are relative to the current max (R5), the metrics carry the exact numbers
- [ ] Moved cells (drag clamps at 11.5 / 7.5) and watched the hottest tile move; ran Check on the challenges
- [ ] Ran one feedback pass and saw the seed's overflow total go 5 → 0

## Done when

- [ ] I can reproduce the goldens on paper/code **or** I finished the browser challenges (preferably both)
