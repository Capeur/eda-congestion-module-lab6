# AGENTS.md — how to work in this repo (Lab 06, Stage 5 done, Stage 5b and Stage 6 next)

You are the coding agent for `eda-congestion-module-lab6`: a bilingual (EN/FR) lessons-only
GitHub Pages site for Lab 06 (congestion heat map) of the eda-learning course.
The site is built (Stage 5); the remaining work is **Stage 5b** (five animated lessons) and
**Stage 6** (hand-off). A remote orchestrator (Mistral Vibe chat) reviews every step:
report outputs verbatim, never skip a check.

## Where everything is (all inside this repo unless noted)

| What | Path |
|---|---|
| Lesson plans, one section per part | `../tools/lab06-notes/LESSON_PLANS.md` (authoritative for storyboards) |
| Stage record, commands, expected numbers | `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/UPGRADE_NOTES.md` |
| Lesson engine skill (scripts + format reference + examples) | `~/.vibe/skills/lesson-animator` (v5.1: heat-grid overlay + generic `--data`) |
| Storyboard format (read before writing any storyboard) | `~/.vibe/skills/lesson-animator/reference/storyboard.md` |
| Validated example storyboards | `ai-workflow/skills/lesson-animator/examples/lab06-congestion-demo/` |
| Transcripts | EN: teacher clone `../eda-learning-lab6-cg/courses/learn_congestion/module02-05-congestion-map/transcript.md`; FR: `i18n/fr/module02-05-congestion-map/transcript.md`; ZH (subtitles only): `i18n/zh/module02-05-congestion-map/transcript.md` |
| Checker `--json` replay data (do not regenerate) | teacher clone `.../examples/congestion_map_check.py --json` (+ `--instance examples/boundary_move.json --json`) |
| Build / tests | `build_site.py`, `tools/test_site.py`, `tools/test_lab_site.py`, `tools/check_sentences.py` |

Environment: use `~/eda-venv/bin/python` (call it `P`), `export PYTHONDONTWRITEBYTECODE=1`, always `python3 -B`.

## Hard rules

1. **Never modify the teacher's clone** (`../eda-learning-lab6-cg`). Read from it only; the only allowed write is
   appending the stage report to the module's `UPGRADE_NOTES.md`.
2. **Never commit or push in either repo**: the user (David) commits after the orchestrator verifies.
3. **Never edit or re-run the checker to change numbers**; every number in a storyboard comes from the checker's
   `--json` or from `UPGRADE_NOTES.md`.
4. **One storyboard per part, both languages in it** (each anchor has `en` and `fr`; `word#1` = second occurrence).
   Anchors are searched only inside their slide.
5. **Follow `LESSON_PLANS.md` exactly** for timeline, show windows, headlines, claims, pauses, chapters and the card.
6. **Run the checker before showing anything** (`check_lesson.py`, 0 errors, 0 warnings) and look at the contact
   sheets of both languages. Draft timing first (`draft_timing.py`): 0 errors, 0 warnings before anything else.
7. Voices (`voice_build.py`) need edge-tts over the VPN; if a network step stalls for a minute, stop, ask for a VPN
   switch, rerun (finished sentences are cached).
8. Storage keys: `lab6-lesson-speed` (lesson pages), `lab6-lessons` (players). Players: `--back ../index.html#lessons`,
   `--next-url ../tools/congestion-map/index.html`. Commit `lessons/*/storyboard.json` + `README.md` +
   `docs/lessons` + `docs/fr/lessons`; `build/` and `.cache/` stay ignored.
9. Rebuild with `~/eda-venv/bin/python build_site.py --repo ../eda-learning-lab6-cg`, restart
   `python3 ~/.vibe/skills/lesson-animator/scripts/serve.py docs 8090`, run both tests, read **both** language lines.

## Known open items (do not silently change)

- The ZH transcript is machine translation; a native reader must check it before publishing.
- The module's old slides, audio, video, frames and step PNGs in the teacher clone are stale against the new transcript
  (teacher list, Stage 6); do not run the course generators or the capture scripts on the module.
