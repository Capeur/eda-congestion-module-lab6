# Part 2 — RUDY's even split (slides 6–11)

Storyboard: `lessons/part-2/storyboard.json` (one file, EN + FR; scene `placement`, v5.1 heat-grid overlay).
Written from `../tools/lab06-notes/LESSON_PLANS.md` "Part 2" with the v5.1 additions: the seed run's six deposit
events replay on `@ab8`/`@each8`/`@big8`/`@ef8` (`deposit: 1 → 4 → 5 → "all"`), the run switches to `spread` at
`@corners9` and the spread events replay on `@stretches9`/`@eleven10`/`@appears11` (`1 → 5 → "all"`); the heat
grid is on from the start (filled by `build_lesson.py --data` from the checker's `--json`).

## Inputs

| Input | Value |
|---|---|
| Transcript EN | `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/transcript.md` slides 6-11 |
| Transcript FR | `i18n/fr/module02-05-congestion-map/transcript.md` slides 6-11 |
| Transcript ZH (subtitles) | `i18n/zh/module02-05-congestion-map/transcript.md` slides 6-11 |
| Golden data | `.cache/congestion-check.json` = `congestion_map_check.py --json` regenerated read-only from the teacher clone, **byte-identical** to `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/data/congestion-check.json` (`cmp` clean); checker itself: 140 PASS, 0 FAIL, 0 SKIP |
| Plan | `../tools/lab06-notes/LESSON_PLANS.md` Part 2 (run switch at `corners9`, nets/netlabels windows keyed to `ab8`/`each8`/`big8`/`ef8`/`stretches9`/`eleven10`/`ef10`/`appears11`, overlays, card, claims, chapters, pause after `ef8`) |
| Style reference | `lessons/part-1/` (storyboard + README), `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/` |

Sentence split (lessonlib, `--repo` = teacher clone): Part 2 is **24 sentences, per slide 4 4 5 3 4 4**, identical
in EN, FR and ZH.

## What the storyboard does (per slide)

- S6 headline "RUDY: split evenly" + sub on `@answer6`; term RUDY from `@rudy6`; tags "bounding box" / "wirelength =
  width + height" from `@bounding6`/`@wirelength6`; `netlabels` from `@wirelength6` (per-net wirelength, follows the
  run: seed 1,1,1,1,2,1 → spread 7,7,4,4,11,1).
- S7 headline "One share per tile"; eq `wirelength / tile count = share` from `@share7`; tags "one third for three
  tiles" / "fixed order…" from `@third7`/`@order7`.
- S8 headline "The seed builds to seven"; `hpwl` counter 7.0 from `@build8`; `demand` counter from `@ab8` follows the
  deposit replay 1→2→3→4→6→7 while `nets` windows show net 0 (`@ab8`), nets 1-3 (`@each8`), net 4 (`@big8`), net 5
  (`@ef8`, `only: true`); `highlight` `["t1,0"]` from `@ab8`; tags "demand 1/4/6/7"; pause 1.2 s after `@ef8`.
- S9 `run: "spread"` at `@corners9` (hpwl counter 34.0); `nets [0]` at `@stretches9` (deposit 1 on spread), tags
  "wirelength 7 over 3 tiles" / "share = 7/3, about 2.33".
- S10 `nets [4]` at `@eleven10` (deposit 5), `nets [5]` at `@ef10`; tags "11 over 6 tiles = 11/6, about 1.83" /
  "1 over 2 tiles = 0.5 each" / "rightmost column stays empty".
- S11 `nets` all at `@appears11` (deposit "all", demand counter 34); tags "row zero: 6.17, 4.67, 6.67" /
  "row one: 6.17, 4.17, 6.17"; card at `slide:11:end+0.3` with `dim: 0.12` (options carry `correct`).
- Claims: 17 — seed run-level (start 7, demand 7), seed per-net hpwl 1,1,1,1,2,1 and all six seed deposit events
  (bbox/hpwl/share/tiles/demandAfter 1..7, integers → exact at 12 digits), spread run-level (start 34, demand 34,
  hottest (2,0) 3.33333333333), spread placement hpwl 34, and the boundary try (A at (6.5,2): hpwl 11.5, ovtotal 7.5,
  ovcount 2, hottest (1,0) 3.625). Every number from `.cache/congestion-check.json`.
- Anchors: 22, all verified with `lessonlib.find_anchor_sentence` in EN and FR (0 missing) before writing.
- Deviation from LESSON_PLANS.md (v5.1): the plan's single `hpwl` counter from `@build8` to `end` is split into four
  sequential counter windows (hpwl → demand → hpwl → demand) so the counter widget never shows two windows at once
  and the `demand` counter follows each deposit replay; the `heat` show window is on from `start` (the plan predates
  the v5.1 heat grid, which repaints per deposit event).
- Deviation (checker limitation): **no event claims on the `spread` run** — `check_lesson.py --data` compares an event
  claim's `demandAfter` matrix with exact list equality while the engine recomputes raw floats (7/3 = 2.3333333333333335
  vs the file's 12-digit 2.33333333333), so any spread event claim reports DIFFER; the seed events are integers and
  compare exactly (as in Part 1). The spread's spoken numbers are still pinned by the run-level claim (34 / 34 /
  hottest (2,0) 3.33333333333), the raw-placement claim (hpwl 34), the engine's 12-event replay check ("all equal",
  1e-9) and `facts_check.py` upstream. Per-net raw-placement claims (`"net": k`) are likewise not file-comparable
  (the file side compares the claim's `hpwl` with the placement total), so the spread's per-net wirelengths
  (7, 11, 1) are not separate claims either.

## Commands (from the site repo; P=~/eda-venv/bin/python, SK=$HOME/.vibe/skills/lesson-animator)

```bash
export PYTHONDONTWRITEBYTECODE=1
P=$HOME/eda-venv/bin/python; SK=$HOME/.vibe/skills/lesson-animator
T=../eda-learning-lab6-cg; M=module02-05-congestion-map; B=build/lessons/part-2; SB=lessons/part-2/storyboard.json
# golden data (regenerate read-only, never hand-edit):
( cd $T/courses/learn_congestion/$M && $P -B examples/congestion_map_check.py --json > $OLDPWD/.cache/congestion-check.json )
cmp .cache/congestion-check.json $SK/examples/lab06-congestion-demo/data/congestion-check.json   # identical
# draft (silent) first — the gate before any voice work:
$P -B $SK/scripts/draft_timing.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 6-11 --lang en \
   --storyboard $SB --repo $T --out-audio $B/draft-en.m4a --out-timing $B/timing-en-draft.json
$P -B $SK/scripts/draft_timing.py --transcript i18n/fr/$M/transcript.md --slides 6-11 --lang fr \
   --storyboard $SB --repo $T --out-audio $B/draft-fr.m4a --out-timing $B/timing-fr-draft.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en-draft.json --audio $B/draft-en.m4a \
   --lang en --out $B/draft-en --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr-draft.json --audio $B/draft-fr.m4a \
   --lang fr --out $B/draft-fr --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/check_lesson.py $B/draft-en/index.html $B/draft-fr/index.html \
   --data .cache/congestion-check.json --sheets $B/check-draft
# voices (every voice shell runs with LD_LIBRARY_PATH unset):
unset LD_LIBRARY_PATH
$P $SK/scripts/voice_build.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 6-11 --lang en \
   --voice en-US-AndrewMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-en.m4a --out-timing $B/timing-en.json
$P $SK/scripts/voice_build.py --transcript i18n/fr/$M/transcript.md --slides 6-11 --lang fr \
   --voice fr-FR-RemyMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-fr.m4a --out-timing $B/timing-fr.json
$P $SK/scripts/subs_build.py --transcript i18n/zh/$M/transcript.md --slides 6-11 --lang zh \
   --against $B/timing-en.json --out $B/subs-zh.json
# the real pages, then the players (whole 5-part shell, now 2 parts built):
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en.json --audio $B/lesson-en.m4a --lang en \
   --out docs/lessons/part-2 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs fr=$B/timing-fr.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr.json --audio $B/lesson-fr.m4a --lang fr \
   --out docs/fr/lessons/part-2 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs en=$B/timing-en.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/check_lesson.py docs/lessons/part-2/index.html docs/fr/lessons/part-2/index.html \
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

## Gate results (2026-11-24, this session; verbatim in `build/lessons/part-2/gates-check.txt` and `gates-site.txt`)

Draft gate (silent `draft_timing.py`, both languages, `check_lesson.py --data`): **0 errors, 0 warnings** on both
pages; claims 17/17; 2 runs / 12 deposit events replayed all equal; `--data`: 52 claim values compared at 12
significant digits, all equal (both languages). Draft lengths EN 115.1 s / FR 141.2 s, 24 sentences each, question at
112.8 s (EN) / 138.9 s (FR). Both contact sheets reviewed (`check-draft/sheet-{en,fr}.png`).

Voices (built in-session, every voice shell with `LD_LIBRARY_PATH` unset): EN `en-US-AndrewMultilingualNeural`
24 sentences **133.3 s**; FR `fr-FR-RemyMultilingualNeural` 24 sentences **133.5 s** (no retries needed); ZH subtitles
via `subs_build.py` against the EN timing (24 sentences).

Final `check_lesson.py` on `docs/lessons/part-2` + `docs/fr/lessons/part-2` with `--data`: **0 errors, 0 warnings** both
languages; claims 17/17; 12 deposit events all equal; 52 claim values at 12 significant digits all equal; EN 133.3 s /
FR 133.5 s, question at 130.6 s (EN) / 130.9 s (FR). Voiced contact sheets reviewed (`check/sheet-{en,fr}.png`).

Players rebuilt both languages: `docs/lessons/index.html` and `docs/fr/lessons/index.html` — "2 part(s), 4.4 min /
4.3 min in all"; parts 3–5 stay not-built (the tests count "2 of 5").

Site gates after `build_site.py --repo ../eda-learning-lab6-cg` (served at 127.0.0.1:8090 via `serve.py docs 8090`):
`tools/test_site.py --teacher ../eda-learning-lab6-cg` → **[en] 60 checks, 0 failed / [fr] 60, 0 failed / [static] 12,
0 failed — 132 checks, 0 failed** (includes the player checks: part list 2 of 5 with titles and lengths, `#part-2`,
language link with `#part-2`, and per part page: no console error, `errors` empty, `dataDiffer` = 0, subtitles menu
with the other language + 中文, Sounds button, audio 200). `tools/test_lab_site.py --teacher ../eda-learning-lab6-cg` →
**[en] 56 ok, 0 FAIL / [fr] 56 ok, 0 FAIL — 112 ok, 0 FAIL in all**.

Click-through Part 2 in EN and FR once at 127.0.0.1:8090 (Playwright): EN player `#part-2` loads
`part-2/index.html`; language link `../fr/lessons/index.html#part-2`; EN part-2 page `errors: []`, audio
`lesson-en.m4a`, subtitles menu Off/English/Français/中文 — at t=45 s the caption over the voice reads EN "Now watch
the seed map build net by net", FR "Regardez maintenant la carte de la graine se construire, réseau par réseau.",
ZH "现在看种子地图一个线网一个线网地构建起来。"; Sounds button toggles `aria-pressed` true→false→true. FR player
`#part-2&s=14` loads `part-2/index.html?s=14` (place kept; FR language link carries `#part-2&s=14`), audio
`lesson-fr.m4a`, seeks to t=76.1, captions at the kept place in FR/EN/ZH, subtitles menu Aucun/Français/English/中文,
`dataDiffer` = 0; no page errors.
