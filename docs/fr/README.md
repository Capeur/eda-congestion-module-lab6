# Module 02-05 : Carte de congestion

**Module id:** `module02-05-congestion-map`  
**Kind:** `lab` · Lab principal : `congestion-map` · **ref**

[← Probabiliste](../module02-03-probabilistic-demand/README.md) · [README du cours](../README.md) · [Débordement →](../module02-07-overflow-metrics/README.md)

## Objectifs

Après ce module vous pouvez : **construire une carte de chaleur de congestion comme demande/capacité par GCell, nommer la tuile la
plus chaude avec un départage écrit, et lire les métriques de débordement (total / max / compte) — y compris comment la capacité
et le déplacement d'une cellule les font basculer.**

## Deux parcours (choisissez-en un ou les deux)

### Parcours A — Implémentation (pratique)

1. Ouvrez [EXAMPLES.md](EXAMPLES.md) ; le corrigé est `examples/congestion_map_check.py` et les instances sont
   `examples/*.json` (`tiny_cong.json` plus trois petites instances qui font chacune basculer un résultat).
2. Implémentez les neuf fonctions de l'API (mêmes signatures que `common/solvers.py`) et vérifiez-les :

   ```bash
   # depuis le dossier de ce module — bibliothèque standard uniquement
   python3 examples/congestion_map_check.py                  # tout PASS (chaque examples/*.json)
   python3 examples/congestion_map_check.py --show           # les règles écrites R1–R7 et chaque table de référence
   python3 examples/congestion_map_check.py --impl my_cong.py  # VOS fonctions (SKIP pour celles qui manquent)
   python3 examples/congestion_map_check.py --vs-node        # bit à bit contre platform/assets/congestion-core.js
   python3 examples/congestion_map_check.py --json           # le fichier de relecture des leçons animées
   ```

   Le module est entièrement déterministe (aucun PRNG) : Python et JavaScript s'accordent **bit à bit par cellule**.
   `examples/wrong/tie_last_wins.py` est un port qui casse une règle écrite et doit FAIL.
3. Cochez [CHECKLIST.md](CHECKLIST.md).
4. Auto-vérification optionnelle : `./scripts/module.sh 02-05 --check` (depuis la racine du cours).

### Parcours B — Lab navigateur (en ligne)

1. Local : [http://127.0.0.1:8080/tools/congestion-map/](http://127.0.0.1:8080/tools/congestion-map/)
2. En ligne : [https://universal-verification-methodology.github.io/learning/tools/congestion-map/](https://universal-verification-methodology.github.io/learning/tools/congestion-map/)
3. Étagère d'outils : ouvrez `congestion-map` depuis l'index des outils de la plateforme
4. Chargez l'instance **de départ**, lancez l'estimateur, inspectez les métriques de débordement ; déplacez des cellules (la limite
   de glisser est à x = 11.5, y = 7.5) et regardez la tuile la plus chaude se déplacer.
5. Cochez les items du parcours B dans [CHECKLIST.md](CHECKLIST.md).

> Les labs de concepts enseignent la culture de la congestion sur une petite grille de GCells — pas des routeurs globaux de production.

## Média

| Artefact | Chemin |
|----------|--------|
| Transcription | [transcript.md](transcript.md) |
| Plan | [outline.yaml](outline.yaml) |
| Diapositives | [slides.pptx](slides.pptx) · [slides.pdf](slides.pdf) |
| Vidéo | [video.mp4](video.mp4) |
| Quiz | [quiz.json](quiz.json) |

## Fichiers

```
module02-05-congestion-map/
├── README.md
├── CHECKLIST.md
├── EXAMPLES.md            ← objectif, règles R1–R7, tables de référence, questions de départ
├── quiz.json              ← format objet : {id, title, items[{id,type,prompt,choices,answer,explain}]}
├── transcript.md
├── outline.yaml
├── examples/
│   ├── congestion_map_check.py   ← auto-vérification (--show/--impl/--vs-node/--json)
│   ├── cong_node.mjs             ← aide --vs-node (importe platform/assets/congestion-core.js)
│   ├── tiny_cong.json            ← grille 4×2, deux placements
│   ├── cap_one.json              ← capacité 2→1 : aucune tuile ne bascule, les ratios doublent
│   ├── boundary_move.json        ← une cellule à travers une frontière de GCell : compte 1→2
│   ├── cap_below_one.json        ← capacité sous 1 : compte 0→2
│   └── wrong/tie_last_wins.py    ← doit FAIL sur la sonde R2
└── assets/               ← _demo.sh, steps/, lab-starter.png, STEPS.md
```
