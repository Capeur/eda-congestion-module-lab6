# Part 4 — No, the total went up (slides 17–23)

Storyboard: `lessons/part-4/storyboard.json` (one file, EN + FR; scene `placement`, v5.1 heat-grid overlay).
Written from `../tools/lab06-notes/LESSON_PLANS.md` "Part 4" with the v5.1 additions: the heat grid is on from
`start` (filled by `build_lesson.py --data` from the checker's `--json`) and always shows the **current run's
final map** — no `deposit` timeline keys in this part, so `initial.deposit: "all"` stands and the map follows the
`run` switch (`spread` → `congested_seed` at `@capone21`).

## Inputs

| Input | Value |
|---|---|
| Transcript EN | `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/transcript.md` slides 17-23 |
| Transcript FR | `i18n/fr/module02-05-congestion-map/transcript.md` slides 17-23 |
| Transcript ZH (subtitles) | `i18n/zh/module02-05-congestion-map/transcript.md` slides 17-23 |
| Golden data | `.cache/congestion-check.json` = `congestion_map_check.py --json` regenerated read-only from the teacher clone, **byte-identical** to `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/data/congestion-check.json` (`cmp` clean); checker itself: 140 PASS, 0 FAIL, 0 SKIP |
| Plan | `../tools/lab06-notes/LESSON_PLANS.md` Part 4 (run switch at `capone21`, nets/netlabels/counter from `start`, overlays, card, claims, chapters, pauses after `largest18` and `falls22`) |
| Style reference | `lessons/part-1/`, `lessons/part-2/`, `lessons/part-3/` (storyboard + README), `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/` |

Sentence split (lessonlib, `--repo` = teacher clone): Part 4 is **27 sentences, per slide 5 5 4 3 4 4 2**, identical
in EN, FR and ZH.

## What the storyboard does (per slide)

- S17 headline "Peak is not total" (sub keyed to `@no17`); `compare` card from `@peak17` to `slide:18` with `dim: 0.12` (the dim key sits on `@peak17`, not `@no17`, so it is not within 0.6 s of `initial` — the checker warns otherwise; the compare also starts at `@peak17` so the floor is already dimmed when the card's text is fully shown). Rows: peak `3.50 → 3.33` fell (good), total overflow `5 → 22` rose (bad), count `1 → 6` rose (bad). `t2,0` ring from `@no17`.
- S18 headline "The spread map in numbers"; tags "row zero: 3.08, 2.33, 3.33" / "row one: 3.08, 2.08, 3.08" / "6 of 8 tiles oversubscribed" / "largest overflow 4.67 at column two row zero" from `@rowzero18`/`@rowone18`/`@six18`/`@largest18` at `x: 44, y: 40`; pause 1.0 s after `@largest18`. Counters: ovcount then ovmax follow these words.
- S19 headline "Overflow's exact rule"; tags "overflow = demand − capacity, floored at zero" / "count only strictly above zero" / "demand = capacity → exactly zero" / "demand 0.5 at capacity 0.5 counts as zero" from `@floored19`/`@strictly19`/`@equal19`/`@aszero19`; counter ovtotal (22).
- S20 headline "The price in wirelength"; `thumbs` from `@cooled20` to `slide:21` (ends at `slide:21`, not `slide:22` as in the plan, so the S21 tags have the right half free) at `x: 46, y: 50`: seed thumb `seed: 7`, spread thumb `spread: 34`; tag "the wires grew longer: 7 → 34" at `x: 3, y: 74` from `@seven20`.
- S21 headline "Raising the capacity"; tags "capacity 5: count 6 → 4" / "the two tiles of column one fall back under the limit" / "seed at capacity 1: ratio 7, still count 1" from `@capfive21`/`@colone21`/`@capone21` at `x: 44, y: 40` (moved from the plan's bottom band: three items there run off the stage); `run: "congested_seed"` at `@capone21` — the heat map, netlabels and counters switch to the seed (wirelength 7.0, `t1,0` ring).
- S22 headline "One feedback pass"; tags "demand splits: 1.5 and 2" / "congestion 0.75 and exactly 1" / "total overflow 5 → 0, count → 0" from `@onefive22`/`@splits22`/`@falls22` at `x: 44, y: 40`; pause 1.2 s after `@falls22`; counter ovtotal shows the seed's 5 from `@splits22`.
- S23 headline "Is zero overflow healthy?" (sub keyed to `@guess23`); card at `slide:23:end+0.3` with `dim: 0.12` (options carry `correct`).
- `nets` and `netlabels` windows from `start` to `end` (all six boxes; per-net wirelengths follow the run: spread 7,7,4,4,11,1 → seed 1,1,1,1,2,1).
- Counter windows (one at a time, split like Part 3): hpwl `start`→`@rowzero18` (34.0), ovcount `@rowzero18`→`@largest18` (6), ovmax `@largest18`→`@floored19` (4.67), ovtotal `@floored19`→`@capone21` (22), hpwl `@capone21`→`@splits22` (7.0), ovtotal `@splits22`→`end` (5).
- Claims: 5 — spread run-level (start 34, demand 34, hottest (2,0) 3.33333333333, ovtotal 22, ovmax 4.66666666667, ovcount 6), seed run-level (start 7, demand 7, hottest (1,0) 3.5, ovtotal 5, ovmax 5, ovcount 1), spread raw placement (literal positions, hpwl 34), seed raw placement (literal positions, hpwl 7), and the **feedback placement** (literal `feedback.to` positions, hpwl 3.5, demand 3.5, hottest (2,0) 1, ovtotal 0, ovmax 0, ovcount 0). Every number from `.cache/congestion-check.json`.
- Anchors: 22, all verified with `lessonlib.find_anchor_sentence` in EN and FR (0 missing) before writing.
- Deviations from LESSON_PLANS.md, all recorded here: (a) v5.1 — the plan's single `hpwl` counter from `start` to `end` is split into six sequential windows (listed above) so the counter widget never shows two windows at once and the overflow metrics of S18/S19/S22 are visible as counters; (b) v5.1 — `highlight` windows ring the hottest tile (`t2,0` on the spread, then `t1,0` on the seed after the run switch); (c) layout — S21/S22 tags at `x: 44, y: 40` (the plan's bottom band `x: 3, y: 74` runs off the stage with three items), thumbs at `x: 46, y: 50` ending at `slide:21`, the compare card starting at `@peak17` together with `dim: 0.12`; (d) claims — `"positions": "start"` means the **first `--data` run** (congested_seed), not `initial.run`, so the spread's wirelength is pinned by a literal-positions claim; and, per the Part 2/3 design note, **no deposit-event or per-net claims** (the file side compares an event's `demandAfter` with exact list equality, which bites on the spread's 7/3 floats) — everything is pinned by the run-level and raw-placement claims, which `--data` compares at 12 significant digits. The capacity-sweep numbers spoken on S21 (spread at capacity 5: count 6→4, the two column-one tiles 4.67/4.17 fall under the limit; seed at capacity 1: ratio 7, count 1) have no engine claim form (the heat block's capacity is fixed at 2) — they are overlay text only, pinned upstream by `../tools/lab06-notes/facts_check.py` (65 PASS) against the `--json` `capacitySweep` block; the feedback pass's after-map (demand 1.5/2.0, cong 0.75/1, hottest (2,0) 1, overflow 5/5/1 → 0/0/0) is pinned by the raw-placement claim on `feedback.to`.

## Commands (from the site repo; P=~/eda-venv/bin/python, SK=$HOME/.vibe/skills/lesson-animator)

```bash
export PYTHONDONTWRITEBYTECODE=1
P=$HOME/eda-venv/bin/python; SK=$HOME/.vibe/skills/lesson-animator
T=../eda-learning-lab6-cg; M=module02-05-congestion-map; B=build/lessons/part-4; SB=lessons/part-4/storyboard.json
# golden data (regenerate read-only, never hand-edit):
( cd $T/courses/learn_congestion/$M && $P -B examples/congestion_map_check.py --json > $OLDPWD/.cache/congestion-check.json )
cmp .cache/congestion-check.json $SK/examples/lab06-congestion-demo/data/congestion-check.json   # identical
# draft (silent) first — the gate before any voice work:
$P -B $SK/scripts/draft_timing.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 17-23 --lang en \
   --storyboard $SB --repo $T --out-audio $B/draft-en.m4a --out-timing $B/timing-en-draft.json
$P -B $SK/scripts/draft_timing.py --transcript i18n/fr/$M/transcript.md --slides 17-23 --lang fr \
   --storyboard $SB --repo $T --out-audio $B/draft-fr.m4a --out-timing $B/timing-fr-draft.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en-draft.json --audio $B/draft-en.m4a \
   --lang en --out $B/draft-en --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr-draft.json --audio $B/draft-fr.m4a \
   --lang fr --out $B/draft-fr --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/check_lesson.py $B/draft-en/index.html $B/draft-fr/index.html \
   --data .cache/congestion-check.json --sheets $B/check-draft
# voices (every voice shell runs with LD_LIBRARY_PATH unset):
unset LD_LIBRARY_PATH
$P $SK/scripts/voice_build.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 17-23 --lang en \
   --voice en-US-AndrewMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-en.m4a --out-timing $B/timing-en.json
$P $SK/scripts/voice_build.py --transcript i18n/fr/$M/transcript.md --slides 17-23 --lang fr \
   --voice fr-FR-RemyMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-fr.m4a --out-timing $B/timing-fr.json
$P $SK/scripts/subs_build.py --transcript i18n/zh/$M/transcript.md --slides 17-23 --lang zh \
   --against $B/timing-en.json --out $B/subs-zh.json
# the real pages, then the players (whole 5-part shell, now 4 parts built):
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en.json --audio $B/lesson-en.m4a --lang en \
   --out docs/lessons/part-4 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs fr=$B/timing-fr.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr.json --audio $B/lesson-fr.m4a --lang fr \
   --out docs/fr/lessons/part-4 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs en=$B/timing-en.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/check_lesson.py docs/lessons/part-4/index.html docs/fr/lessons/part-4/index.html \
   --data .cache/congestion-check.json --sheets $B/check
$P -B $SK/scripts/build_player.py --lessons docs/lessons --lang en --heading "Congestion heat map" \
   --eyebrow "Lab 06 · animated lessons" --other fr=../fr/lessons/index.html --back ../index.html#lessons \
   --next-url ../tools/congestion-map/index.html --next-label "Open the browser lab" \
   --storage-key lab6-lessons --titles build/titles-en.json
$P -B $SK/scripts/build_player.py --lessons docs/fr/lessons --lang fr --heading "Carte de congestion" \
   --eyebrow "Lab 06 · leçons animées" --other en=../../lessons/index.html --back ../index.html#lessons \
   --next-url ../tools/congestion-map/index.html --next-label "Ouvrir le labo dans le navigateur" \
   --storage-key lab6-lessons --titles build/titles-fr.json
# site + tests (restart serve.py after each build_site.py, docs/ is recreated):
$P -B build_site.py --repo $T
( setsid nohup $P -B $SK/scripts/serve.py docs 8090 & ) ; sleep 2
$P -B tools/test_site.py --teacher $T ; $P -B tools/test_lab_site.py --teacher $T
```

## Gate results (2026-11-24, this session; verbatim in `build/lessons/part-4/gates-draft.txt`, `gates-check.txt`, `gates-site.txt`, `clickthrough.txt`)

Draft gate (silent `draft_timing.py`, both languages, `check_lesson.py --data`): **0 errors, 0 warnings** on both
pages; claims 5/5; 2 runs / 12 deposit events replayed all equal; `--data`: 20 claim values compared at 12
significant digits, all equal (both languages). Draft lengths EN 123.0 s / FR 146.3 s, 27 sentences each, question at
120.7 s (EN) / 144.0 s (FR). Both contact sheets reviewed (`check-draft/sheet-{en,fr}.png`). (Three layout fixes
during gating: dim + compare both keyed to `@peak17` — a dim key at `@no17` is within 0.6 s of `initial` and the
compare card covered undimmed cells; S21/S22 tags moved from the bottom band to `x: 44, y: 40`; thumbs end at
`slide:21` to clear the S21 tags; the short S23 tag dropped.)

Voices (built in-session, every voice shell with `LD_LIBRARY_PATH` unset; no failed sentence, no retry): EN
`en-US-AndrewMultilingualNeural` 27 sentences **146.6 s** (RC 0); FR `fr-FR-RemyMultilingualNeural` 27 sentences
**139.4 s** (RC 0). ZH subtitles via `subs_build.py` against the EN timing (27 sentences).

Final `check_lesson.py` on `docs/lessons/part-4` + `docs/fr/lessons/part-4` with `--data`: **0 errors, 0 warnings**
both languages; claims 5/5; 12 deposit events all equal; 20 claim values at 12 significant digits all equal; EN
146.6 s / FR 139.4 s, question at 143.9 s (EN) / 136.7 s (FR). Voiced contact sheets reviewed (`check/sheet-{en,fr}.png`):
spread map with the `t2,0` ring and the ovcount/ovmax/ovtotal counters, then the seed map with `t1,0` and
wirelength 7.0 after the run switch at `@capone21`, the thumbs (seed 7 / spread 34), and the card.

Players rebuilt both languages: `docs/lessons/index.html` and `docs/fr/lessons/index.html` — "4 part(s), 8.4 min in
all" (EN) / "4 part(s), 8.3 min in all" (FR); part 5 stays not-built (the tests count "4 of 5").

Site gates after `build_site.py --repo ../eda-learning-lab6-cg` (served at 127.0.0.1:8090 via `serve.py docs 8090`):
`tools/test_site.py --teacher ../eda-learning-lab6-cg` → **[en] 72 checks, 0 failed / [fr] 72, 0 failed / [static] 12,
0 failed — 156 checks, 0 failed** (includes the player checks: part list 4 of 5 with titles and lengths, `#part-4`,
language link with `#part-4`, and per part page × language: no console error, `errors` empty, `dataDiffer` = 0,
subtitles menu with the other language + 中文, Sounds button, audio 200). `tools/test_lab_site.py --teacher
../eda-learning-lab6-cg` → **[en] 56 ok, 0 FAIL / [fr] 56 ok, 0 FAIL — 112 ok, 0 FAIL in all**.

Click-through Part 4 in EN and FR once at 127.0.0.1:8090 (Playwright): EN player `#part-4` loads
`part-4/index.html`, audio `lesson-en.m4a` (200), `errors: []`, `dataDiffer` = 0, duration 146.6 s; at t≈18 s the
caption over the voice reads EN "Peak and total are different measures of one map", switching the subtitles menu
to Français shows "Le pic et le total sont deux mesures différentes d'une même carte.", to 中文 shows
"峰值和总量是同一张地图的两种不同度量。" (menu Off/English/Français/中文); the Sounds button toggles `aria-pressed`
true→false. Paused at t = 23.1 s, the EN language link carries the place
(`../fr/lessons/index.html#part-4&s=5`); the FR player at `#part-4&s=4` loads `part-4/index.html?s=4`, audio
`lesson-fr.m4a`, seeks to t = 17.31 (sentence 4's start in the FR timing is 17.30 — place kept), `errors: []`,
`dataDiffer` = 0, captions at the kept place in FR with subs=fr ("Le pic et le total sont deux mesures différentes
d'une même carte"), in EN with subs=en, and in ZH with subs=zh (menu Aucun/Français/English/中文), Sons button,
language link back `../../lessons/index.html#part-4&s=4`; no page errors.
