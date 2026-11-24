# Exemples — Carte de congestion

Parcours A (implémentation). L'instance est `examples/tiny_cong.json` (puce 12×8, GCells 4×2 de 3×4, capacité 2, cellules A–F,
réseaux A–B, C–D, A–C, B–D, A–B–C–D, E–F). Le corrigé est `examples/congestion_map_check.py` ; chaque nombre ci-dessous a été
imprimé par ce vérificateur (`python3 examples/congestion_map_check.py --show`, `--json`). Lancez-le depuis le dossier de ce module ;
il n'a besoin que de la bibliothèque standard de Python (`--vs-node` demande aussi `node`). Le module est **entièrement
déterministe** — les positions viennent du fichier d'instance, rien ne tire de nombre aléatoire — donc il n'y a pas de PRNG et
Python et JavaScript s'accordent **bit à bit par cellule** (`--vs-node`).

## Objectif

Construire une **carte de chaleur de congestion** : par GCell, `congestion = demande / capacité`, plus les métriques de
débordement (`max(0, demande − capacité)` par tuile, et total / max / compte sur la grille). Les valeurs au-dessus de 1 sont
sursaturées. La carte permet de désigner la tuile la plus chaude sans lire de flottants ; les métriques donnent les nombres
exacts, régressables.

## Définitions

- **Grille de GCells** : `nx × ny` tuiles de `cellW × cellH` sur la puce. Ici 4×2 de 3×4 sur 12×8. `cellGcell(x, y)` =
  `clamp(floor(x/3), 0, 3)`, `clamp(floor(y/4), 0, 1)` — les coordonnées hors puce se calent dans la tuile du bord (R6) :
  (12, 8) → (3, 1), (−1, −1) → (0, 0).
- **Boîte englobante / HPWL du réseau** : boîte de ses broches ; HPWL = (max x − min x) + (max y − min y).
- **Demande RUDY** (R3, l'ordre de remplissage) : les réseaux dans l'ordre du fichier ; un réseau dépose `part = HPWL / max(1, #tuiles)`
  dans chaque GCell que sa boîte touche, tuiles remplies **i externe / j interne** ; la demande s'accumule dans cet ordre (l'ordre
  des flottants compte au dernier ulp).
- **Congestion** = demande / capacité. **Débordement** (R7) = `max(0, demande − capacité)` par tuile ; `compte` = nombre de tuiles
  avec débordement **strictement > 0** ; `total` sommé dans l'ordre de balayage ; `max` initialisé à 0.
- **Plus chaude** (R2) = argmax de la congestion, balayage i externe / j interne, strictement `>` : le **premier** maximum dans
  l'ordre ligne par ligne gagne ; tout à zéro → (0, 0, 0). Sonde : `[[1,2],[0,0],[0,0],[2,0]]` → (0, 1).
- **Couleur de chaleur** (R5) : `t = clamp(cong / maxC, 0, 1)` avec `maxC` = le max de congestion de la carte **courante** —
  **relatif au max courant, pas à la capacité** ; la sursaturation (> 1) n'est pas une frontière de couleur. Palette papier :
  bornes u = 0, 1/3, 2/3, 1 → `#ffffff, #0f6b5c, #b45309, #9f1239`, alpha 0.15 + 0.7u.
- **Arrondi** (R1) : les vérifications comparent les flottants bruts avec une tolérance de 1e-9 ; affichage à 2 décimales,
  arrondi demi-pair ; `--json` arrondit à 12 chiffres significatifs. `total += v` en JS et `sum()` en Python peuvent différer au
  dernier ulp, donc le vérificateur accumule `total` avec une boucle explicite (c'est pourquoi le total brut dispersé vaut
  22.000000000000004 en JS).

## Les deux règles de limite dans la puce (gardées telles quelles, non unifiées)

- **Limite de glisser** (déplacer les cellules dans le lab navigateur) : x ∈ [0, 11.5], y ∈ [0, 7.5] — les littéraux codés en dur dans
  `platform/assets/interactive-congestion-lab.js` `moveSelectedTo` (CHIP − 0.5). Sonde : (20, −3) → (11.5, 0).
- **Limite de rétroaction** (`placementFeedbackLite`) : x ∈ [0, chip−1] = [0, 11], y ∈ [0, chip−1] = [0, 7]. Sondes : avec
  F en (15, 2.5) la rétroaction le déplace à (11, 4.25) ; avec F en (4.5, 20) à (6, 7).

Ce sont deux règles différentes (11.5/7.5 vs 11/7) ; le vérificateur les teste telles quelles.

## API (ce que cherche `--impl`)

`positions` est `{cell: {"x": .., "y": ..}}`, `data` est le dictionnaire d'instance chargé depuis un fichier `examples/*.json`.
Mêmes signatures que `common/solvers.py`, pour comparer votre fichier avec celui du cours. Les fonctions que vous n'avez pas
encore écrites sont signalées SKIP ; ne changez jamais les positions, réseaux ou données qu'on vous donne.

```python
def cell_gcell(x, y, nx, ny, cell_w, cell_h)   -> (i, j)
def net_bbox(net, positions)                   -> (x0, y0, x1, y1)
def hpwl(net, positions)                       -> float
def deposit_events(positions, data)            -> [{net, pins, bbox, hpwl, tiles, share}, ...]  # ordre de remplissage
def rudy_demand(positions, data)               -> demand[i][j]
def congestion_map(demand, capacity)           -> cong[i][j]
def overflow_metrics(demand, capacity)         -> {"perCell", "total", "max", "count"}
def hottest(cong)                              -> (i, j, v)
def placement_feedback_lite(positions, data)   -> new positions
```

## Pseudocode

```text
ENTRÉE : positions, instance (puce, grille de GCells, capacité, réseaux)
pour chaque réseau, dans l'ordre des réseaux :   # R3
  bbox  = min/max des positions de ses broches
  wl    = (max x - min x) + (max y - min y)       # HPWL
  tiles = GCells des coins du bbox, calées, remplies i externe / j interne
  part  = wl / max(1, #tiles)
  pour chaque tuile (i, j) dans cet ordre : demande[i][j] += part
cong[i][j]     = demande[i][j] / capacité
débord[i][j]   = max(0, demande[i][j] - capacité)  # R7 ; compte = #tuiles avec > 0 (strict)
pluschaude     = argmax cong, balayage i externe / j interne, strictement >  # R2 : premier max ligne par ligne
chaleur t[i][j] = clamp(cong[i][j] / maxC, 0, 1)    # R5 : relatif au max courant, pas à la capacité
SORTIE : demande, congestion, débordement (perCell/total/max/compte), pluschaude, chaleur t
```

## Référence 1 — la graine encombrée (capacité 2)

Les six cellules sont dans la GCell (1,0) ; chaque réseau y dépose (ordre de remplissage R3) :

| réseau | broches | bbox | HPWL | tuiles | part |
|---|---|---|---|---|---|
| 0 | A, B | [4, 2, 5, 2] | 1 | (1,0) | 1 |
| 1 | C, D | [4, 3, 5, 3] | 1 | (1,0) | 1 |
| 2 | A, C | [4, 2, 4, 3] | 1 | (1,0) | 1 |
| 3 | B, D | [5, 2, 5, 3] | 1 | (1,0) | 1 |
| 4 | A, B, C, D | [4, 2, 5, 3] | 2 | (1,0) | 2 |
| 5 | E, F | [4.5, 2.5, 5.5, 2.5] | 1 | (1,0) | 1 |

| quantité | valeur | pourquoi c'est important |
|---|---|---|
| demande | (1,0) = **7**, toutes les autres tuiles 0 | 1+1+1+1+2+1 |
| congestion | (1,0) = **3.50** | 7 / 2 |
| débordement | perCell (1,0) = **5** ; total **5**, max **5**, compte **1** | max(0, 7−2) ; compte strict > 0 |
| plus chaude (R2) | **(1,0) @ 3.50** | le centre s'allume en premier |
| HPWL | par réseau [1, 1, 1, 1, 2, 1], total **7** | placement compact, fils courts |
| chaleur t (R5) | (1,0) = 1.00, le reste 0 | maxC = 3.5 |

## Référence 2 — le placement dispersé (capacité 2)

| réseau | broches | bbox | HPWL | tuiles (ordre de remplissage) | part |
|---|---|---|---|---|---|
| 0 | A, B | [1, 1, 8, 1] | 7 | (0,0), (1,0), (2,0) | 7/3 = 2.3333 |
| 1 | C, D | [1, 5, 8, 5] | 7 | (0,1), (1,1), (2,1) | 2.3333 |
| 2 | A, C | [1, 1, 1, 5] | 4 | (0,0), (0,1) | 2 |
| 3 | B, D | [8, 1, 8, 5] | 4 | (2,0), (2,1) | 2 |
| 4 | A, B, C, D | [1, 1, 8, 5] | 11 | (0,0), (0,1), (1,0), (1,1), (2,0), (2,1) | 11/6 = 1.8333 |
| 5 | E, F | [5, 3, 6, 3] | 1 | (1,0), (2,0) | 0.5 |

| quantité | valeur | pourquoi c'est important |
|---|---|---|
| demande | 6.17 6.17 \| 4.67 4.17 \| 6.67 6.17 \| 0 0 (colonnes i = 0..3) | RUDY réparti sur les tuiles du bbox |
| congestion | 3.08 3.08 \| 2.33 2.08 \| 3.33 3.08 \| 0 0 | demande / 2 |
| débordement | total **22**, max **4.67**, compte **6** | total brut JS 22.000000000000004 (R1) |
| plus chaude (R2) | **(2,0) @ 3.33** | premier max dans l'ordre ligne par ligne |
| HPWL | par réseau [7, 7, 4, 4, 11, 1], total **34** | fils longs |
| chaleur t (R5) | 0.93 0.93 \| 0.70 0.62 \| 1.00 0.93 \| 0 0 | maxC = 3.33 |

**Pic contre total** : la dispersion abaisse la congestion de pic (3.50 → 3.33) mais augmente le débordement total (5 → 22) et le
compte de sursaturées (1 → 6). Lisez les deux nombres, pas seulement la tuile la plus chaude.

## Référence 3 — balayage de capacité (les deux placements, RUDY)

| capacité | total / max / compte dispersé | total / max / compte graine |
|---|---|---|
| 1 | 28.00 / 5.67 / **6** | 6 / 6 / **1** |
| 2 | 22.00 / 4.67 / 6 | 5 / 5 / 1 |
| 3 | 16.00 / 3.67 / 6 | 4 / 4 / 1 |
| 4 | 10.00 / 2.67 / 6 | 3 / 3 / 1 |
| 5 | 5.17 / 1.67 / **4** | 2 / 2 / 1 |
| 8 | 0 / 0 / **0** | 0 / 0 / **0** |

Deux réponses vérifiées qui étaient posées vaguement :

- **Capacité 2 → 1 : aucune tuile ne bascule sursaturée.** Chaque tuile au-dessus de la capacité 2 l'est encore au-dessus de 1, les
  tuiles à zéro restent à zéro : le compte reste 6 sur la dispersion et 1 sur la graine ; seuls les ratios doublent (plus chaude
  dispersée 3.33 → 6.67). Voir `examples/cap_one.json` (même instance à capacité 1, balayage [2, 1, 5, 8]).
- **Capacité 2 → 5 sur la dispersion est la bascule visible : compte 6 → 4.** Les tuiles (1,0) (demande 4.67) et (1,1) (demande 4.17)
  sont au-dessus de 2 mais pas au-dessus de 5, donc elles sortent ; total 22 → 5.17.

## Référence 4 — une passe de rétroaction sur la graine (R4 + limite de rétroaction)

Les voisins sont essayés (+1,0), (−1,0), (0,+1), (0,−1), strictement `<` ; la cellule avance au milieu vers le centre de la tuile
choisie, calée dans [0, 11]×[0, 7] (la limite de rétroaction, pas la limite de glisser).

| quantité | avant | après |
|---|---|---|
| positions | A(4,2) B(5,2) C(4,3) D(5,3) E(4.5,2.5) F(5.5,2.5) | A(5.75,2) B(6.25,2) C(5.75,2.5) D(6.25,2.5) E(6,2.25) F(6.5,2.25) |
| demande | (1,0) = 7 | (1,0) = 1.5, (2,0) = 2.0 |
| débordement total / max / compte | 5 / 5 / 1 | **0 / 0 / 0** |
| plus chaude | (1,0) @ 3.5 | (2,0) @ **exactement 1.0** |

## Trois petites instances qui font chacune basculer un résultat

| fichier | ce qui change | la bascule (tout vient du vérificateur) |
|---|---|---|
| `examples/cap_one.json` | petite instance à **capacité 1** (le cas 2→1) | aucune tuile ne bascule ; les ratios doublent ; le compte est inchangé (6 dispersé / 1 graine). Balayage [2, 1, 5, 8] |
| `examples/boundary_move.json` | cellule A de la graine déplacée (4,2) → (6.5,2), à travers la frontière de GCell x = 6 | les réseaux touchant A déposent maintenant dans deux tuiles : compte de débordement **1 → 2**, total 5 → 7.5, HPWL 7 → 11.5, plus chaude (1,0) @ 3.625 |
| `examples/cap_below_one.json` | grille 2×1, **capacité 0.4** (sous 1) | le réseau A–B traverse la frontière x = 3 : part 0.5 par tuile ; à capacité 1 compte 0, à 0.5 débordement exactement 0 (strict > 0, R7), à 0.4 compte **0 → 2** (congestion 1.25) |

Lancez l'une d'elles avec `python3 examples/congestion_map_check.py --instance examples/boundary_move.json --show`.

## Sondes (règles épinglées par le vérificateur)

- R2 ex aequo : `hottest([[1,2],[0,0],[0,0],[2,0]])` = **(0,1)** — premier max dans l'ordre ligne par ligne, pas le dernier ; tout à zéro → (0,0,0).
- R6 limite : `cellGcell(12, 8)` = (3,1), `cellGcell(-1, -1)` = (0,0).
- Limite de glisser : (20, −3) → **(11.5, 0)**, (11.7, 7.6) → (11.5, 7.5).
- Limite de rétroaction : F (15, 2.5) → **(11, 4.25)** ; F (4.5, 20) → (6, 7).
- Entrée inversée : réseaux inversés sur la dispersion donnent les mêmes tuiles par réseau, demande à 1e-9 près (différences de
  dernier ulp permises, R1), même compte 6 et même plus chaude (2,0) ; le dictionnaire de positions dans l'ordre inverse des clés
  donne la même rétroaction.

## Essayez ceci

```bash
python3 examples/congestion_map_check.py                     # tout PASS (chaque examples/*.json)
python3 examples/congestion_map_check.py --show              # les règles écrites R1–R7 et chaque table de référence
python3 examples/congestion_map_check.py --instance examples/cap_one.json --show
python3 examples/congestion_map_check.py --impl my_cong.py   # VOS fonctions (SKIP pour celles qui manquent)
python3 examples/congestion_map_check.py --impl examples/wrong/tie_last_wins.py   # FAIL volontairement (règle R2)
python3 examples/congestion_map_check.py --vs-node           # JS et Python s'accordent bit à bit par cellule
python3 examples/congestion_map_check.py --json > lesson.json  # le fichier de relecture des leçons animées
```

`examples/wrong/tie_last_wins.py` est un port fidèle en apparence qui casse une règle écrite (`>=` au lieu de `>` dans
`hottest`) : il doit FAIL sur la sonde d'ex aequo avec `got [3, 0, 2.0]`.

## Questions de départ (demandez pourquoi)

1. Chargez `placement` et `congested_seed` depuis `examples/tiny_cong.json` ; imprimez les matrices 4×2 de demande et de congestion
   avec deux décimales. Quelle tuile est la plus chaude sur chacune, et pourquoi (R2) ?
2. Lancez les événements de dépôt du vérificateur pour le placement dispersé. Pourquoi le réseau A–B (HPWL 7) donne-t-il 2.3333 à
   chacune de (0,0), (1,0), (2,0) au lieu de tout mettre dans une tuile ?
3. Comparez dispersé et graine sur le **pic et le total** de débordement. Pourquoi la dispersion abaisse-t-elle le pic (3.50 → 3.33)
   mais augmente-t-elle le total (5 → 22) ?
4. Passez la capacité de 2.0 à 1.0 (voir `examples/cap_one.json`) : quelles GCells basculent sursaturées ? Vérifiez maintenant la
   réponse vérifiée : **aucune** — le compte reste 6 sur la dispersion et 1 sur la graine, seuls les ratios doublent. Puis montez la
   capacité à 5 sur le placement dispersé : le compte tombe de 6 → 4 parce que les tuiles (1,0) et (1,1) repassent sous la capacité.
   Pourquoi 2→1 ne fait rien basculer tandis que 2→5 fait sortir deux tuiles ?
5. Déplacez une cellule à travers une frontière de GCell (`examples/boundary_move.json` : A de (4,2) à (6.5,2)). Quelles listes de
   tuiles des réseaux changent, et pourquoi le compte de débordement bascule-t-il de 1 → 2 ?
6. Lancez une passe de rétroaction sur la graine. Pourquoi le débordement total atteint-il exactement 0, et pourquoi la nouvelle
   plus chaude (2,0) à congestion exactement 1.0 est-elle encore peinte avec la couleur du haut (R5) ?
7. Écrivez une phrase : pourquoi une carte de congestion appartient-elle **avant** le routage global détaillé ?

## Livrables attendus

- Un fichier avec les neuf fonctions de l'API et un run `--impl` propre (aucun FAIL)
- Les tables demande / congestion / débordement / plus chaude pour les deux placements de `examples/tiny_cong.json`
- Une phrase pour chacune des questions 3, 4, 5 et 7
