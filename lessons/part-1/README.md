# Part 1 — A crowded chip lights up (slides 1–5)

Storyboard: `lessons/part-1/storyboard.json` (one file, EN + FR; scene `placement`, v5.1 heat-grid overlay).
Written from `../tools/lab06-notes/LESSON_PLANS.md` "Part 1" with the v5.1 additions from the Stage 5b work
order: the GCell heat grid is painted from the checker's `--json` (via `build_lesson.py --data`), and the seed
run's six deposit events replay on `@seven5` (`deposit: "all"`).

## Inputs

| Input | Value |
|---|---|
| Transcript EN | `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/transcript.md` slides 1-5 |
| Transcript FR | `i18n/fr/module02-05-congestion-map/transcript.md` slides 1-5 |
| Transcript ZH (subtitles) | `i18n/zh/module02-05-congestion-map/transcript.md` slides 1-5 |
| Golden data | `.cache/congestion-check.json` = `congestion_map_check.py --json` regenerated read-only from the teacher clone, **byte-identical** to `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/data/congestion-check.json` (`cmp` clean); checker itself: 140 PASS, 0 FAIL |
| Plan | `../tools/lab06-notes/LESSON_PLANS.md` Part 1 (show windows, overlays, card, claims, chapters, pause after `three5`) |
| Style reference | `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/` |

## What the storyboard does (per slide)

- S1 headline "Why a heat map?"; S2 chip + cells, `nets` boxes from `@cells2`, term Net; S3 GCell grid
  (`show: heat` from `@gcells3`), term GCell, tag "each tile 3 by 4"; S4 the ratio: headline + eq
  `demand / capacity = congestion`, term Congestion, tag "above one: oversubscribed"; S5 the seed map:
  netlabels, wirelength counter (7.0), then `deposit: "all"` at `@seven5` replays the six seed events while the
  `demand` counter counts 1→7, `hottestTile` counter "1,0 3.5" + `t1,0` ring at `@three5`, `ovtotal` counter 5
  at `@five5`; pause 1.2 s after `@three5`; card at `slide:5:end+0.3` with `dim: 0.12`.
- Claims: 14 (positions/start hpwl 7, per-net hpwl 1,1,1,1,2,1, run-level heat claim demand 7 / hottest (1,0) 3.5 /
  ovtotal 5 / ovmax 5 / ovcount 1, and all six deposit events with bbox/hpwl/share/tiles/demandAfter) — every
  number from `.cache/congestion-check.json`.
- Anchors: 15, all verified with `lessonlib.find_anchor_sentence` in EN and FR (0 missing) before writing.
- Deviation from LESSON_PLANS.md (v5.1 work order): the plan's single `hpwl` counter from `@seven5` to `end`
  is split into the wirelength counter at `@seed5`→`@seven5` plus the heat counters (`demand`, `hottestTile`,
  `ovtotal`) that follow the deposit replay, so the counter widget never shows two windows at once.

## Commands (from the site repo; P=~/eda-venv/bin/python, SK=ai-workflow/skills/lesson-animator)

```bash
export PYTHONDONTWRITEBYTECODE=1
P=$HOME/eda-venv/bin/python; SK=ai-workflow/skills/lesson-animator
T=../eda-learning-lab6-cg; M=module02-05-congestion-map; B=build/lessons/part-1; SB=lessons/part-1/storyboard.json
# golden data (regenerate read-only, never hand-edit):
( cd $T/courses/learn_congestion/$M && $P -B examples/congestion_map_check.py --json > $OLDPWD/.cache/congestion-check.json )
cmp .cache/congestion-check.json $SK/examples/lab06-congestion-demo/data/congestion-check.json   # identical
# draft (silent) timing first — the gate before any voice work:
$P -B $SK/scripts/draft_timing.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 1-5 --lang en \
   --storyboard $SB --repo $T --out-audio $B/draft-en.m4a --out-timing $B/timing-en-draft.json
$P -B $SK/scripts/draft_timing.py --transcript i18n/fr/$M/transcript.md --slides 1-5 --lang fr \
   --storyboard $SB --repo $T --out-audio $B/draft-fr.m4a --out-timing $B/timing-fr-draft.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en-draft.json --audio $B/draft-en.m4a \
   --lang en --out $B/draft-en --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr-draft.json --audio $B/draft-fr.m4a \
   --lang fr --out $B/draft-fr --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json
$P -B $SK/scripts/check_lesson.py $B/draft-en/index.html $B/draft-fr/index.html \
   --data .cache/congestion-check.json --sheets $B/check-draft
# voices (David records them between steps; VPN up):
$P -B $SK/scripts/voice_build.py --transcript $T/courses/learn_congestion/$M/transcript.md --slides 1-5 --lang en \
   --voice en-US-AndrewMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-en.m4a --out-timing $B/timing-en.json
$P -B $SK/scripts/voice_build.py --transcript i18n/fr/$M/transcript.md --slides 1-5 --lang fr \
   --voice fr-FR-RemyMultilingualNeural --rate=-4% --storyboard $SB --repo $T --workdir .cache/voice \
   --out-audio $B/lesson-fr.m4a --out-timing $B/timing-fr.json
# ZH subtitles against the EN timing, then the real pages:
$P -B $SK/scripts/subs_build.py --transcript i18n/zh/$M/transcript.md --slides 1-5 --lang zh \
   --against $B/timing-en.json --out $B/subs-zh.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-en.json --audio $B/lesson-en.m4a --lang en \
   --out docs/lessons/part-1 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs fr=$B/timing-fr.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/build_lesson.py --storyboard $SB --timing $B/timing-fr.json --audio $B/lesson-fr.m4a --lang fr \
   --out docs/fr/lessons/part-1 --fonts site_src/fonts --storage-key lab6-lesson-speed --data .cache/congestion-check.json \
   --subs en=$B/timing-en.json --subs zh=$B/subs-zh.json
$P -B $SK/scripts/check_lesson.py docs/lessons/part-1/index.html docs/fr/lessons/part-1/index.html \
   --data .cache/congestion-check.json --sheets $B/check
```

## Gate result (draft timing, 2026-11-24, this session)

```
check_lesson.py build/lessons/part-1/draft-en/index.html build/lessons/part-1/draft-fr/index.html \
  --data .cache/congestion-check.json --sheets build/lessons/part-1/check-draft
  en: claims 14/14; 2 run(s), 12 deposit event(s) replayed, all equal;
      --data: 48 claim value(s) compared at 12 significant digits: all equal; no problems
  fr: claims 14/14; 2 run(s), 12 deposit event(s) replayed, all equal;
      --data: 48 claim value(s) compared at 12 significant digits: all equal; no problems
  0 error(s), 0 warning(s)
```
Draft lengths (silent, estimated): EN 111.9 s, FR 132.6 s, 27 sentences each, question at 109.6 s (EN) /
130.3 s (FR). Contact sheets: `build/lessons/part-1/check-draft/sheet-{en,fr}.png` (both reviewed); a probe frame
at t=104 s shows tile (1,0) painted crimson with the `t1,0` ring, counter "1,0 3.5", tags demand 7 /
congestion 3.5.

Fixes during gating: question card on-screen time (tail 2.0 → 2.6 s) and three text overlaps (eq/term/tag/counter
positions moved, S4 headline `size: 3.6` for French room).

Voices: built 2026-11-24 in-session (`voice_build.py`, LD_LIBRARY_PATH unset in every voice shell):
EN `en-US-AndrewMultilingualNeural` 27 sentences 128.6 s; FR `fr-FR-RemyMultilingualNeural` 27 sentences
127.0 s (one FR sentence, slide 2 #6, hit a DNS failure after 3 attempts and was redone by rerunning the same
command — cached sentences were skipped); ZH subtitles via `subs_build.py` against the EN timing (27 sentences).
Final `check_lesson.py` on `docs/lessons/part-1` + `docs/fr/lessons/part-1` with `--data`: 0 errors, 0 warnings,
48 claim values all equal at 12 significant digits, both languages.
