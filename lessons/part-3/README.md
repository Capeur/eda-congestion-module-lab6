# Part 3 — The hottest tile (slides 12–16)

Storyboard: `lessons/part-3/storyboard.json` (one file, EN + FR; scene `placement`, v5.1 heat-grid overlay).
Written from `../tools/lab06-notes/LESSON_PLANS.md` "Part 3" with the v5.1 additions: the heat grid is on from
`start` (filled by `build_lesson.py --data` from the checker's `--json`) and always shows the **current run's
final map** — no `deposit` timeline keys in this part, so `initial.deposit: "all"` stands and the map follows the
`run` switch (`spread` → `congested_seed` at `@seedmap15`).

## Inputs

| Input | Value |
|---|---|
| Transcript EN | `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/transcript.md` slides 12-16 |
| Transcript FR | `i18n/fr/module02-05-congestion-map/transcript.md` slides 12-16 |
| Transcript ZH (subtitles) | `i18n/zh/module02-05-congestion-map/transcript.md` slides 12-16 |
| Golden data | `.cache/congestion-check.json` = `congestion_map_check.py --json` regenerated read-only from the teacher clone, **byte-identical** to `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/data/congestion-check.json` (`cmp` clean); checker itself: 140 PASS, 0 FAIL, 0 SKIP |
| Plan | `../tools/lab06-notes/LESSON_PLANS.md` Part 3 (run switch at `seedmap15`, nets/netlabels/counter windows from `start`, overlays, card, claims, chapters, pause after `reaches14`) |
| Style reference | `lessons/part-1/`, `lessons/part-2/` (storyboard + README), `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/` |

Sentence split (lessonlib, `--repo` = teacher clone): Part 3 is **22 sentences, per slide 3 6 6 4 3**, identical
in EN, FR and ZH.

## What the storyboard does (per slide)

- S12 headline "The hottest tile"; tags "column two, row zero, congestion 3.33" / "scan every tile, keep the
  largest" from `@hottest12`/`@scan12`; term Argmax from `@argmax12`; `hottestTile` counter "2,0 3.33" from
  `@hottest12` with the `t2,0` ring on the spread map.
- S13 headline "A tie must be written down"; tags "scan column by column, then row by row" / "strictly greater
  wins" / "first maximum in scan order wins" from `@colcol13`/`@strictly13`/`@firstmax13`.
- S14 headline "A tie example"; tags "column zero holds 1 and 2" / "column three holds 2 and 0" / "two tiles tie
  at 2: (0,1) and (3,0)" / "scan reaches column zero first: (0,1) wins" from `@colzero14`/`@colthree14`/`@tieat14`/
  `@reaches14`; pause 1.2 s after `@reaches14`.
- S15 `run: "congested_seed"` at `@seedmap15` (wirelength counter follows to 7.0, heat map switches to the seed,
  ring moves to `t1,0`); tags "only tile (1,0) is nonzero, 3.5" / "argmax: column one, row zero, 3.5" from
  `@seedmap15`/`@argmax15`; `hottestTile` counter "1,0 3.5" from `@argmax15`.
- S16 headline "Why the rule is on paper"; tag "the checker's goldens need it" from `@goldens16`; card at
  `slide:16:end+0.3` with `dim: 0.12` (options carry `correct`).
- `nets` and `netlabels` windows from `start` to `end` (all six boxes; per-net wirelengths follow the run: spread
  7,7,4,4,11,1 → seed 1,1,1,1,2,1).
- Claims: 4 — spread run-level (start 34, demand 34, hottest (2,0) 3.33333333333, ovtotal 22, ovmax
  4.66666666667, ovcount 6), seed run-level (start 7, demand 7, hottest (1,0) 3.5, ovtotal 5, ovmax 5, ovcount 1),
  spread raw placement (literal positions, hpwl 34), seed raw placement (literal positions, hpwl 7 + demand 7 /
  hottest (1,0) 3.5 / ovtotal 5 / ovmax 5 / ovcount 1). Every number from `.cache/congestion-check.json`.
- Anchors: 13, all verified with `lessonlib.find_anchor_sentence` in EN and FR (0 missing) before writing.
- Deviations from LESSON_PLANS.md, all recorded here: (a) v5.1 — the plan's single `hpwl` counter from `start` to
  `end` is split into four sequential windows (hpwl `start`→`@hottest12`, `hottestTile` `@hottest12`→`@seedmap15`,
  hpwl `@seedmap15`→`@argmax15`, `hottestTile` `@argmax15`→`end`) so the counter widget never shows two windows at
  once and the argmax is visible as a counter; (b) v5.1 — `highlight` windows ring the hottest tile
  (`t2,0` then `t1,0`); (c) layout — the tag/tags overlays sit at `x: 44, y: 40` (not `y: 24` as in Part 2) because
  the `hottestTile` counter widget is taller (label wraps) and reached down to y≈33 % at `y: 24`; (d) claims —
  `"positions": "start"` means the **first `--data` run** (congested_seed), not `initial.run`, so the spread's
  wirelength is pinned by a literal-positions claim instead; and, per the Part 2 design note, **no deposit-event
  or per-net claims** (the file side compares an event's `demandAfter` with exact list equality, which bites on the
  spread's 7/3 floats) — everything is pinned by the run-level and raw-placement claims, which `--data` compares
  at 12 significant digits. The S14 tie probe (matrix [[1,2],[0,0],[0,0],[2,0]] → (0,1) wins) has no engine claim
  form; it stays pinned upstream by `../tools/lab06-notes/facts_check.py` (65 PASS) against the checker's own
  `hottest()`.

## Commands (from the site repo; P=~/eda-venv/bin/python, SK=$HOME/.vibe/skills/lesson-animator)

```bash
export PYTHONDONTWRITEBYTECODE=1
P=$HOME/eda-venv/bin/python; SK=$HOME/.vibe/skills/lesson-animator
T=../eda-learning-lab6-cg; M=module02-05-congestion-map; B=build/lessons/part-3; SB=lessons/part-3/storyboard.json
# golden data (regenerate read-only, never hand-edit):
( cd $T/courses/learn_congestion/$M && $P -B examples/congestion_map_check.py --json > $OLDPWD/.cache/congestion-check.json )
cmp .cache/congestion-check.json $SK/examples/lab06-congestion-demo/data/congestion-check.json   # identical
# draft (silent) first — the gate before any voice work:
$P -B $SK/scripts/draft_timing.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 12-16 --lang en \
   --storyboard $SB --repo $T --out-audio $B/draft-en.m4a --out-timing $B/timing-en-draft.json
$P -B $SK/scripts/draft_timing.py --transcript i18n/fr/$M/transcript.md --slides 12-16 --lang fr \
   --storyboard $SB --repo $T --out-audio $B/draft-fr.m4a --out-timing $B/timing-fr-draft.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en-draft.json --audio $B/draft-en.m4a \
   --lang en --out $B/draft-en --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr-draft.json --audio $B/draft-fr.m4a \
   --lang fr --out $B/draft-fr --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/check_lesson.py $B/draft-en/index.html $B/draft-fr/index.html \
   --data .cache/congestion-check.json --sheets $B/check-draft
# voices (every voice shell runs with LD_LIBRARY_PATH unset):
unset LD_LIBRARY_PATH
$P $SK/scripts/voice_build.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 12-16 --lang en \
   --voice en-US-AndrewMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-en.m4a --out-timing $B/timing-en.json
$P $SK/scripts/voice_build.py --transcript i18n/fr/$M/transcript.md --slides 12-16 --lang fr \
   --voice fr-FR-RemyMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-fr.m4a --out-timing $B/timing-fr.json
$P $SK/scripts/subs_build.py --transcript i18n/zh/$M/transcript.md --slides 12-16 --lang zh \
   --against $B/timing-en.json --out $B/subs-zh.json
# the real pages, then the players (whole 5-part shell, now 3 parts built):
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en.json --audio $B/lesson-en.m4a --lang en \
   --out docs/lessons/part-3 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs fr=$B/timing-fr.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr.json --audio $B/lesson-fr.m4a --lang fr \
   --out docs/fr/lessons/part-3 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs en=$B/timing-en.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/check_lesson.py docs/lessons/part-3/index.html docs/fr/lessons/part-3/index.html \
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
( setsid nohup $P $SK/scripts/serve.py docs 8090 & ) ; sleep 2
$P -B tools/test_site.py --teacher $T ; $P -B tools/test_lab_site.py --teacher $T
```

## Gate results (2026-11-24, this session; verbatim in `build/lessons/part-3/gates-draft.txt`, `gates-check.txt`, `gates-site.txt`, `clickthrough.txt`)

Draft gate (silent `draft_timing.py`, both languages, `check_lesson.py --data`): **0 errors, 0 warnings** on both
pages; claims 4/4; 2 runs / 12 deposit events replayed all equal; `--data`: 19 claim values compared at 12
significant digits, all equal (both languages). Draft lengths EN 81.4 s / FR 102.5 s, 22 sentences each, question at
79.1 s (EN) / 100.2 s (FR). Both contact sheets reviewed (`check-draft/sheet-{en,fr}.png`): spread map painted with
the `t2,0` ring and "2,0 3.33" counter, then the seed map with `t1,0` and "1,0 3.5" after the run switch.

Voices (built in-session, every voice shell with `LD_LIBRARY_PATH` unset; no failed sentence, no retry): EN
`en-US-AndrewMultilingualNeural` 22 sentences **96.1 s** (RC 0); FR `fr-FR-RemyMultilingualNeural` 22 sentences
**99.0 s** (RC 0). ZH subtitles via `subs_build.py` against the EN timing (22 sentences).

Final `check_lesson.py` on `docs/lessons/part-3` + `docs/fr/lessons/part-3` with `--data`: **0 errors, 0 warnings**
both languages; claims 4/4; 12 deposit events all equal; 19 claim values at 12 significant digits all equal; EN
96.1 s / FR 99.0 s, question at 93.4 s (EN) / 96.4 s (FR). Voiced contact sheets reviewed (`check/sheet-{en,fr}.png`).

Players rebuilt both languages: `docs/lessons/index.html` and `docs/fr/lessons/index.html` — "3 part(s), 6.0 min in
all"; parts 4–5 stay not-built (the tests count "3 of 5").

Site gates after `build_site.py --repo ../eda-learning-lab6-cg` (served at 127.0.0.1:8090 via `serve.py docs 8090`):
`tools/test_site.py --teacher ../eda-learning-lab6-cg` → **[en] 66 checks, 0 failed / [fr] 66, 0 failed / [static] 12,
0 failed — 144 checks, 0 failed** (includes the player checks: part list 3 of 5 with titles and lengths, `#part-3`,
language link with `#part-3`, and per part page × language: no console error, `errors` empty, `dataDiffer` = 0,
subtitles menu with the other language + 中文, Sounds button, audio 200). `tools/test_lab_site.py --teacher
../eda-learning-lab6-cg` → **[en] 56 ok, 0 FAIL / [fr] 56 ok, 0 FAIL — 112 ok, 0 FAIL in all**.

Click-through Part 3 in EN and FR once at 127.0.0.1:8090 (Playwright): EN player `#part-3` loads
`part-3/index.html`, audio `lesson-en.m4a` (200), `errors: []`, `dataDiffer` = 0, duration 96.1 s; at t≈20 s the
caption over the voice reads EN "If code picks either one two correct programs can disagree", switching the
subtitles menu to Français shows "Si le code choisit l'une ou l'autre, deux programmes corrects peuvent diverger.",
to 中文 shows "如果代码随便选一个，两个正确的程序就会给出不同结果。" (menu Off/English/Français/中文); the Sounds
button toggles `aria-pressed` true→false. Paused at t = 22.6 s, the EN language link carries the place
(`../fr/lessons/index.html#part-3&s=4`); the FR player at that link loads `part-3/index.html?s=4`, audio
`lesson-fr.m4a`, seeks to t = 18.73 (sentence 4's start in the FR timing — place kept), `errors: []`,
`dataDiffer` = 0, captions at the kept place in FR and in EN with subs=en (menu Aucun/Français/English/中文), Sons
button, language link back `../../lessons/index.html#part-3&s=4`; no page errors.
