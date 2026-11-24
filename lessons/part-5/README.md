# Part 5 — Cooled, not cold (slides 24–28)

Storyboard: `lessons/part-5/storyboard.json` (one file, EN + FR; scene `placement`, v5.1 heat-grid overlay).
Written from `../tools/lab06-notes/LESSON_PLANS.md` "Part 5" with the v5.1 additions. This part closes the lab: it
opens on the **feedback placement** (`run: "after"`), switches back to the **seed** on slide 26 (the browser-lab
slide), and ends on the last pause-and-guess card plus the hand-off (the player's next button opens
`../tools/congestion-map/index.html`; the quiz sits on the site page).

The heat grid is on from `start` (filled by `build_lesson.py --data` from the checker's `--json`); there are no
`deposit` timeline keys in this part, so `initial.deposit: "all"` stands and the map follows the `run` switch
(`after` → `congested_seed` at `slide:26`).

**The `after` run** (the feedback placement) is pinned in the storyboard's `placement.data.runs.after` — the
checker's `--json` carries it in the `feedback` block, not in `runs`, and the engine only paints a heat map for
runs that carry `events`. The entry was generated with the checker's own functions
(`deposit_events` / `rudy_demand` / `congestion_map` / `overflow_metrics` / `hottest` / `heat_t` run on
`feedback.to` against the golden file) and asserted equal to the file's `feedback.demandAfter` /
`overflowAfter` / `hottestAfter` before writing; the golden file itself is never edited. The engine replays its
6 deposit events like the file's runs (18 events checked in all, all equal), and `check_lesson.py --data` pins
the same placement a second time through the raw-placement claim at 12 significant digits.

## Inputs

| Input | Value |
|---|---|
| Transcript EN | `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/transcript.md` slides 24-28 |
| Transcript FR | `i18n/fr/module02-05-congestion-map/transcript.md` slides 24-28 |
| Transcript ZH (subtitles) | `i18n/zh/module02-05-congestion-map/transcript.md` slides 24-28 |
| Golden data | `.cache/congestion-check.json` = `congestion_map_check.py --json` regenerated read-only from the teacher clone, **byte-identical** to `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/data/congestion-check.json` (`cmp` clean); checker itself: 140 PASS, 0 FAIL, 0 SKIP |
| Plan | `../tools/lab06-notes/LESSON_PLANS.md` Part 5 (run `after` at start, run switch at `slide:26`, nets from `start`, netlabels from `@browser26`, counter from `@lights26`, vocab on S25, card on S28 that answers its own question, claims, chapters, pause after `cooled24`) |
| Style reference | `lessons/part-1/` … `lessons/part-4/` (storyboard + README), `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/` |

Sentence split (lessonlib, `--repo` = teacher clone): Part 5 is **22 sentences, per slide 4 6 4 5 3**, identical
in EN, FR and ZH.

## What the storyboard does (per slide)

- S24 headline "Cooled, not cold" (sub keyed to `@afterpass24`); tags "count 0, total overflow 0" /
  "hottest: column two row zero, exactly 1" / "right at capacity, not below it" / "cooled is not cold" from
  `@afterpass24`/`@hottest24`/`@capacity24`/`@cooled24` at `x: 44, y: 40`; pause 1.2 s after `@cooled24`;
  `t2,0` ring from `@hottest24`. Counters on the after map: ovcount `@afterpass24`→`@hottest24` (0),
  ovtotal `@hottest24`→`@capacity24` (0), hottestTile `@capacity24`→`@drag26` ("2,0 1").
- S25 headline "Remember"; `vocab` at `x: 44, y: 40` — Congestion / Oversubscribed / RUDY / Argmax / Overflow /
  Peak vs total, each keyed to its word (`@congestion25` … `@peak25`).
- S26 headline "Your turn in the browser"; `run: "congested_seed"` at `slide:26` — the heat map, netlabels and
  counters switch to the seed (wirelength 7.0, `t1,0` ring, hottestTile "1,0 3.5"); netlabels from `@browser26`;
  tags "seed lights one tile at 3.5" / "drag cell A across the boundary" / "run feedback: total overflow falls
  to 0" from `@lights26`/`@drag26`/`@runfeedback26` at `x: 44, y: 40`; hpwl counter from `@drag26` to `end` (7.0).
- S27 headline "Your turn in Python"; tags "divide a demand matrix by capacity" / "hottest with the written
  tie-break" / "golden seed: (1,0) at 3.5" / "golden spread: (2,0) at 3.33" from `@divide27`/`@tiebreak27`/
  `@goldseed27`/`@goldspread27` at `x: 44, y: 40`.
- S28 headline "One last question" (sub keyed to `@guess28`); `dim: 0.12` at `slide:28:end+0.2`; the card at
  `slide:28:end+0.3` asks "peak fell — celebrate?" and answers itself (the correct option's reply carries
  peak 3.5→3.33, total 5→22, count 1→6, wires 7→34).
- `nets` window from `start` to `end` (all six boxes of the shown run); chapters `start` "Cooled, not cold" ·
  `slide:25` "Remember" · `slide:26` "Your turn".
- Claims: 6 — run-level heat claims on `after` (start 3.5, demand 3.5, hottest (2,0) v 1, ovtotal/ovmax/ovcount
  0), `congested_seed` (7, 7, (1,0) 3.5, 5/5/1) and `spread` (34, 34, (2,0) 3.33333333333, 22/4.66666666667/6),
  plus the three raw placements (seed hpwl 7, spread hpwl 34, `feedback.to` hpwl 3.5 with the same heat claim).
  Every number from `.cache/congestion-check.json`. Per the Part 2/3 design note, **no deposit-event or
  per-net claims** (the file side compares an event's `demandAfter` with exact list equality, which bites on the
  spread's 7/3 floats) — everything is pinned by the run-level and raw-placement claims, compared at 12
  significant digits.
- Anchors: 19, all verified with `lessonlib.find_anchor_sentence` in EN and FR (0 missing) before writing.
- Deviations from LESSON_PLANS.md, all recorded here: (a) v5.1 — the plan's single `hpwl` counter from
  `@lights26` is preceded by three heat-counter windows on S24 (ovcount / ovtotal / hottestTile, listed above)
  so the slide's numbers are on stage as counters too, split like Part 4 so the counter widget never shows two
  windows at once; the hottestTile window runs to `@drag26` so that at `@lights26` it reads "1,0 3.5" exactly as
  spoken, and the hpwl window follows from `@drag26`; (b) v5.1 — `highlight` windows ring the hottest tile
  (`t2,0` on the after map, then `t1,0` on the seed after the run switch at `slide:26`); (c) the `after` run is
  pinned in `placement.data.runs` (see above) so the engine can paint its heat map; (d) layout — the S24 tags
  and the S25 vocab sit at `x: 44, y: 40` (not the plan's higher band): the counter widget's box reaches ~33–37 %
  of the stage height on the right, and at `y ≤ 36` the long FR rows overlapped it (2 warnings in the first draft
  gate); the vocab rows were shortened so they do not wrap off the stage in FR.

## Commands (from the site repo; P=~/eda-venv/bin/python, SK=$HOME/.vibe/skills/lesson-animator)

```bash
export PYTHONDONTWRITEBYTECODE=1
P=$HOME/eda-venv/bin/python; SK=$HOME/.vibe/skills/lesson-animator
T=../eda-learning-lab6-cg; M=module02-05-congestion-map; B=build/lessons/part-5; SB=lessons/part-5/storyboard.json
# golden data (regenerate read-only, never hand-edit):
( cd $T/courses/learn_congestion/$M && $P -B examples/congestion_map_check.py --json > $OLDPWD/.cache/congestion-check.json )
cmp .cache/congestion-check.json $SK/examples/lab06-congestion-demo/data/congestion-check.json   # identical
# draft (silent) first — the gate before any voice work:
$P -B $SK/scripts/draft_timing.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 24-28 --lang en \
   --storyboard $SB --repo $T --out-audio $B/draft-en.m4a --out-timing $B/timing-en-draft.json
$P -B $SK/scripts/draft_timing.py --transcript i18n/fr/$M/transcript.md --slides 24-28 --lang fr \
   --storyboard $SB --repo $T --out-audio $B/draft-fr.m4a --out-timing $B/timing-fr-draft.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-{en,fr}-draft.json --audio $B/draft-{en,fr}.m4a \
   --lang en|fr --out $B/draft-{en,fr} --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/check_lesson.py $B/draft-en/index.html $B/draft-fr/index.html \
   --data .cache/congestion-check.json --sheets $B/check-draft
# voices (every voice shell runs with LD_LIBRARY_PATH unset):
unset LD_LIBRARY_PATH
$P $SK/scripts/voice_build.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 24-28 --lang en \
   --voice en-US-AndrewMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-en.m4a --out-timing $B/timing-en.json
$P $SK/scripts/voice_build.py --transcript i18n/fr/$M/transcript.md --slides 24-28 --lang fr \
   --voice fr-FR-RemyMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-fr.m4a --out-timing $B/timing-fr.json
$P $SK/scripts/subs_build.py --transcript i18n/zh/$M/transcript.md --slides 24-28 --lang zh \
   --against $B/timing-en.json --out $B/subs-zh.json
# the real pages, then the players (whole 5-part shell, now 5 parts built):
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en.json --audio $B/lesson-en.m4a --lang en \
   --out docs/lessons/part-5 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs fr=$B/timing-fr.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr.json --audio $B/lesson-fr.m4a --lang fr \
   --out docs/fr/lessons/part-5 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs en=$B/timing-en.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/check_lesson.py docs/lessons/part-5/index.html docs/fr/lessons/part-5/index.html \
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

## Gate results (2026-11-24, this session; verbatim in `build/lessons/part-5/gates-draft.txt`, `gates-check.txt`, `gates-site.txt`, `gates-lab.txt`, `clickthrough.txt`)

Golden data: `.cache/congestion-check.json` regenerated from the teacher clone, `cmp` **byte-identical** with
`ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/data/congestion-check.json`; the checker
itself prints 140 PASS, 0 FAIL, 0 SKIP.

Draft gate (silent `draft_timing.py`, both languages, `check_lesson.py --data`): **0 errors, 0 warnings** on both
pages after two layout fixes (S24 tags `y:24→40`; S25 vocab `y:20→40` with shortened rows — the counter
widget's box reaches ~33–37 % of the stage height on the right and the first draft had 4 text-over-counter
warnings); claims 6/6; 3 runs / 18 deposit events replayed all equal; `--data`: 20 claim values compared at 12
significant digits, all equal (both languages). Draft lengths EN 91.5 s / FR 114.5 s, 22 sentences each,
question at 89.2 s (EN) / 112.2 s (FR). Both contact sheets reviewed (`check-draft/sheet-{en,fr}.png`).

Voices (built in-session, every voice shell with `LD_LIBRARY_PATH` unset): EN `en-US-AndrewMultilingualNeural`
22 sentences **108.3 s** — the flaky edge-tts `NoAudioReceived` hit sentences 9, 13 and 18 on single runs; the
same command was rerun (cached sentences skipped) until RC 0, audio and timing files never edited. FR
`fr-FR-RemyMultilingualNeural` 22 sentences **110.9 s** (RC 0 on the first run). ZH subtitles via
`subs_build.py` against the EN timing (22 sentences lined up).

Final `check_lesson.py` on `docs/lessons/part-5` + `docs/fr/lessons/part-5` with `--data`: **0 errors, 0 warnings**
both languages; claims 6/6; 18 deposit events all equal; 20 claim values at 12 significant digits all equal; EN
108.3 s / FR 110.9 s, question at 105.6 s (EN) / 108.3 s (FR). Voiced contact sheets reviewed
(`check/sheet-{en,fr}.png`): the after map (tiles (1,0)/(2,0) painted, counters 0 / 0 / "2,0 1"), then the seed
map with `t1,0` and "1,0 3.5" after the run switch at `slide:26`, wirelength 7.0 / 7,0, and the card over a
dimmed floor.

Players rebuilt both languages: `docs/lessons/index.html` and `docs/fr/lessons/index.html` — **"5 part(s), 10.2
min in all"** (EN and FR).

Site gates after `build_site.py --repo ../eda-learning-lab6-cg` (served at 127.0.0.1:8090 via `serve.py docs
8090`; sentence check clean: 28 slides, EN 122, FR 122, ZH 122):
`tools/test_site.py --teacher ../eda-learning-lab6-cg` → **[en] 78 checks, 0 failed / [fr] 78, 0 failed /
[static] 12, 0 failed — 168 checks, 0 failed** (the player checks now see 5 of 5 parts with titles and lengths,
`#part-5`, the language link with `#part-5`, and per part page × language: no console error, `errors` empty,
`dataDiffer` = 0, subtitles menu with the other language + 中文, Sounds button, audio 200). One earlier run had
a single FAIL — `net::ERR_ABORTED` on the FR part-5 iframe when the test's `goto`+`reload` raced the frame load;
the rerun is clean and the check is the test's own navigation race, not the page. `tools/test_lab_site.py
--teacher ../eda-learning-lab6-cg` → **[en] 56 ok, 0 FAIL / [fr] 56 ok, 0 FAIL — 112 ok, 0 FAIL in all**.

Click-through Part 5 in EN and FR once at 127.0.0.1:8090 (Playwright): EN player `#part-5` loads
`part-5/index.html`, audio `lesson-en.m4a` (200), `errors: []`, `dataDiffer` = 0 (3 runs checked), duration
108.3 s; at t = 20 s the caption over the voice reads EN "Congestion is demand divided by capacity, per tile",
the subtitles menu (Off/English/Français/中文) shows "La congestion est la demande divisée par la capacité, par
tuile." with subs=fr and "拥塞度是每格的需求除以容量。" with subs=zh; the Sounds button toggles `aria-pressed`
true→false. Paused at t = 23.1 s, the EN language link carries the place
(`../fr/lessons/index.html#part-5&s=4`); the FR player at `#part-5&s=4` loads `part-5/index.html?s=4`, audio
`lesson-fr.m4a`, seeks to t = 17.84 s (sentence 4's start in the FR timing is 17.83 — place kept), `errors: []`,
`dataDiffer` = 0, captions at the kept place in FR with subs=fr, in EN with subs=en
("Congestion is demand divided by capacity, per tile.") and in ZH with subs=zh (menu Aucun/Français/English/中文),
language link back `../../lessons/index.html#part-5&s=4`, Sons button present, no page errors in either language.
