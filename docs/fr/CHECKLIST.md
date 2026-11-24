# Checklist — Carte de congestion

## Parcours A — Implémentation (`examples/congestion_map_check.py`)

- [ ] **Le ratio** : sur la graine encombrée, la GCell (1,0) a une demande de 7 et une congestion de **3.50** (7 / capacité 2) ; au-dessus de 1, c'est sursaturé
- [ ] **Ordre de remplissage RUDY (R3)** : réseaux dans l'ordre du fichier, tuiles i externe / j interne, part = HPWL / max(1, #tuiles) — sur le placement dispersé le réseau A–B (HPWL 7) donne 2.3333 à chacune de (0,0), (1,0), (2,0)
- [ ] **Départage de la plus chaude (R2)** : balayage i externe / j interne, strictement `>` — `[[1,2],[0,0],[0,0],[2,0]]` → **(0,1)**, tout à zéro → (0,0,0) ; plus chaude dispersée **(2,0) @ 3.33**, plus chaude graine **(1,0) @ 3.50**
- [ ] **Débordement (R7)** : perCell = max(0, demande − capacité) ; le compte est strictement `> 0` — graine : total/max/compte **5/5/1** ; dispersé : **22/4.67/6** (total brut JS 22.000000000000004, R1)
- [ ] **Pic contre total** : la dispersion abaisse le pic (3.50 → 3.33) mais augmente le total (5 → 22) et le compte (1 → 6) ; HPWL 7 → 34
- [ ] **Bascules de capacité** : 2→1 ne fait basculer **aucune** tuile (compte 6→6 dispersé, 1→1 graine ; les ratios doublent) ; 2→5 sur la dispersion fait tomber le compte **6→4** — les tuiles (1,0) et (1,1) sortent
- [ ] **Une cellule à travers une frontière** (`examples/boundary_move.json`) : A (4,2)→(6.5,2) fait basculer le compte 1→2, total 5→7.5
- [ ] **Capacité sous 1** (`examples/cap_below_one.json`) : les tuiles à part 0.5 passent à capacité 1, débordement exactement 0 à 0.5 (compte strict), compte 2 à 0.4
- [ ] **Les deux limites telles qu'écrites** : glisser [0, 11.5]×[0, 7.5] (lab interactif), rétroaction [0, 11]×[0, 7] (chip−1) — sondes F (15,2.5)→(11,4.25), F (4.5,20)→(6,7)
- [ ] **La chaleur est relative au max courant (R5)** : t = clamp(cong / maxC, 0, 1) ; après une passe de rétroaction la tuile la plus chaude (2,0) @ exactement 1.0 peint encore la couleur du haut de la palette
- [ ] **Rétroaction (R4)** : une passe sur la graine annule le débordement (5/5/1 → 0/0/0), voisins (+1,0), (−1,0), (0,+1), (0,−1) strictement `<`
- [ ] Entrées inversées : réseaux inversés → mêmes tuiles par réseau, demande à 1e-9 près, même compte et même plus chaude ; dictionnaire de positions inversé → même rétroaction
- [ ] J'ai lancé `examples/wrong/tie_last_wins.py` avec `--impl` et vu le FAIL sur la sonde R2 (`got [3, 0, 2.0]`)
- [ ] `python3 examples/congestion_map_check.py` imprime tout PASS ; `--impl my_cong.py` n'imprime aucun FAIL ; `--vs-node` s'accorde bit à bit par cellule ; `--json` émet le fichier de relecture des leçons

## Parcours B — Lab navigateur (`congestion-map`)

- [ ] J'ai ouvert le lab (local ou en ligne) et chargé l'instance de départ
- [ ] J'ai lu la légende de chaleur : les couleurs sont relatives au max courant (R5), ce sont les métriques qui portent les nombres exacts
- [ ] J'ai déplacé des cellules (la limite de glisser est à 11.5 / 7.5) et regardé la tuile la plus chaude se déplacer ; j'ai lancé Vérifier sur les défis
- [ ] J'ai lancé une passe de rétroaction et vu le total de débordement de la graine passer de 5 → 0

## Terminé quand

- [ ] Je peux reproduire les résultats de référence sur papier ou en code **ou** j'ai fini les défis du navigateur (les deux de préférence)
