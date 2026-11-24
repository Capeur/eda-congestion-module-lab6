"""French text for the Lab 06 browser lab (congestion heat map).

The lab has no separate strings module: every word it shows lives in platform/tools/congestion-map/index.html,
congestion-map.js and congestion-map-lab-model.js, plus the shared challenge chrome assets/clustering-ui.js. This table
holds exact (file, English snippet, French text) replacements applied to the French copy at build time; the build stops
if a snippet is not found, so a half-translated lab is never published.

Paths are relative to docs/fr/. Challenge ids, CSS classes, cell names (A-F), element ids and numbers stay as they are.
The metrics readout lines (selected:, HPWL:, overflow total:, hottest:, capacity:) are program output and stay in
English, like code and commands.

Vocabulary: puce (chip), cellule (cell), réseau (net), placement, GCell / tuile (tile), capacité (capacity), demande
(demand), congestion, sursaturée (oversubscribed), débordement (overflow), longueur de fil (HPWL, wirelength), boîte
englobante (bounding box), RUDY, plus chaude (hottest), argmax, règle de départage (tie-break), graine (seed),
placement dispersé (spread), rétroaction (feedback), golden (résultat de référence), révéler (reveal).
"""

LAB = "tools/congestion-map/"
UI = "assets/clustering-ui.js"
MODEL = LAB + "congestion-map-lab-model.js"
PAGE = LAB + "congestion-map.js"

STRINGS = [
    # ---------------- page (index.html) ----------------
    (LAB + "index.html", '<html lang="en">', '<html lang="fr">'),
    (LAB + "index.html", "<title>Congestion heat map — EDA Algorithms Platform</title>",
     "<title>Carte de congestion — EDA Algorithms Platform</title>"),
    (LAB + "index.html", ">Skip to content<", ">Aller au contenu<"),
    (LAB + "index.html", '<div class="eyebrow">Interactive tool</div>', '<div class="eyebrow">Outil interactif</div>'),
    (LAB + "index.html", "<h1>Congestion heat map</h1>", "<h1>Carte de congestion</h1>"),
    (LAB + "index.html",
     "Drag cells on the 4×2 GCell grid, paint demand/capacity per tile, and find the hottest tile under the written tie-break.",
     "Glissez les cellules sur la grille de GCells 4×2, peignez demande/capacité par tuile, et trouvez la tuile la plus chaude selon le départage écrit."),

    # ---------------- shared challenge chrome (clustering-ui.js) ----------------
    (UI, 'statusText: "Idle"', 'statusText: "En attente"'),
    (UI, '"Challenge armed — act, then Check"', '"Défi lancé : agissez, puis Vérifier"'),
    (UI, '"Starter loaded (reference)"', '"Exemple de départ chargé (référence)"'),
    (UI, '"Load a challenge with Start"', '"Lancez un défi avec Commencer"'),
    (UI, 'setStatus("pass", "PASS")', 'setStatus("pass", "RÉUSSI")'),
    (UI, '"Not yet — try again or show hint"', '"Pas encore : réessayez ou affichez l\'indice"'),
    (UI, '"Load starter example"', '"Charger l\'exemple de départ"'),
    (UI, "<h2>Challenges</h2>", "<h2>Défis</h2>"),
    (UI, "${challenges.length} cleared</span>", "${challenges.length} réussis</span>"),
    (UI, '<label for="lab-chal-sel">Pick one</label>', '<label for="lab-chal-sel">Choisir</label>'),
    (UI, '"Pick a challenge and click <strong>Start</strong>. The starter example above stays available as a reference — reload it anytime."',
     '"Choisissez un défi et cliquez sur <strong>Commencer</strong>. L\'exemple de départ reste disponible comme référence : rechargez-le quand vous voulez."'),
    (UI, "<strong>Hint:</strong>", "<strong>Indice :</strong>"),
    (UI, '"Restart" : "Start"', '"Recommencer" : "Commencer"'),
    (UI, '"Hide hint" : "Show hint"', '"Masquer l\'indice" : "Afficher l\'indice"'),
    (UI, '"disabled"}>Check</button>', '"disabled"}>Vérifier</button>'),
    (UI, ">Next challenge</button>", ">Défi suivant</button>"),
    (UI, ">Stop checking</button>", ">Arrêter le défi</button>"),
    (UI, 'el("h2", { text: "Graph" })', 'el("h2", { text: "Carte" })'),
    (UI, 'el("h2", { text: "Reference / metrics" })', 'el("h2", { text: "Métriques" })'),

    # ---------------- lab UI (congestion-map.js) ----------------
    (PAGE, 'btn("Run feedback", "btn-secondary"', 'btn("Lancer la rétroaction", "btn-secondary"'),
    (PAGE, 'state.revealed ? "Hide golden" : "Reveal golden (study)"',
     'state.revealed ? "Masquer le golden" : "Révéler le golden (étude)"'),
    (PAGE, '"view: revealed spread golden (study — never counts)"',
     '"vue : golden dispersé révélé (étude — ne compte jamais)"'),
    (PAGE, '"view: Run feedback result (unchanged since the button)"',
     '"vue : résultat de Lancer la rétroaction (inchangé depuis le bouton)"'),
    (PAGE, '`view: your edits of the ${M.methodLabel(state.base.method)} result (${moved ? moved.length : 0} cell(s) moved — its credit is cancelled)`',
     '`vue : vos éditions du résultat de ${M.methodLabel(state.base.method)} (${moved ? moved.length : 0} cellule(s) déplacée(s) — son crédit est annulé)`'),
    (PAGE, '"view: your placement (built by dragging)"', '"vue : votre placement (construit en glissant)"'),
    (PAGE, '"Type your answers — they must match YOUR map on screen:"',
     '"Tapez vos réponses — elles doivent correspondre à VOTRE carte à l\'écran :"'),
    (PAGE, 'starterButtonLabel: "Reset workspace"', 'starterButtonLabel: "Réinitialiser l\'espace de travail"'),
    (PAGE, '"Pick a challenge and click <strong>Start</strong>. Drag cells and type answers, then <strong>Check</strong>. The reveal is study-only: what it shows never counts."',
     '"Choisissez un défi et cliquez sur <strong>Commencer</strong>. Glissez les cellules et tapez vos réponses, puis <strong>Vérifier</strong>. La révélation est pour l\'étude seule : ce qu\'elle montre ne compte jamais."'),
    (PAGE, "<p><strong>Your workspace:</strong> click a cell to select it, click empty canvas to move it",
     "<p><strong>Votre espace de travail :</strong> cliquez une cellule pour la sélectionner, cliquez le canevas vide pour la déplacer"),
    (PAGE, "(nudge buttons move by 0.5). The heat map paints each GCell with",
     "(les boutons de poussée déplacent de 0.5). La carte de chaleur peint chaque GCell avec"),
    (PAGE, "<em>t = clamp(congestion / max congestion)</em> on the paper palette — the colour is relative to",
     "<em>t = clamp(congestion / max congestion)</em> sur la palette papier — la couleur est relative à"),
    (PAGE, "the current hottest tile, so oversubscribed is not a colour boundary.</p>",
     "la tuile la plus chaude courante, donc la sursaturation n'est pas une frontière de couleur.</p>"),
    (PAGE, "<p>Challenges check <em>what you built</em>: your own congestion matrix, your own hottest tile",
     "<p>Les défis vérifient <em>ce que vous avez construit</em> : votre propre matrice de congestion, votre propre tuile la plus chaude"),
    (PAGE, "under the written tie-break, and peak + total overflow + HPWL bounded together. Nothing passes on",
     "selon le départage écrit, et pic + débordement total + HPWL bornés ensemble. Rien ne passe au"),
    (PAGE, "page load, from the seed alone, from the reveal, or from one <em>Run feedback</em> click alone —",
     "chargement de la page, depuis la graine seule, depuis la révélation, ou depuis un seul clic sur <em>Lancer la rétroaction</em> —"),
    (PAGE, "and editing after a method button cancels that method's credit.</p>",
     "et éditer après un bouton de méthode annule le crédit de cette méthode.</p>"),

    # ---------------- lab UI docblock (congestion-map.js) ----------------
    (PAGE, " - “Run feedback” is a method button: its untouched result can earn credit, an edit after it",
     " - « Lancer la rétroaction » est un bouton de méthode : son résultat intact peut rapporter des points, une édition après"),
    (PAGE, "preset seed, from the reveal, or from one Run feedback click alone.",
     "la graine seule, depuis la révélation, ou depuis un seul clic sur Lancer la rétroaction."),
    # ---------------- lab model (congestion-map-lab-model.js) ----------------
    (MODEL, '"Run feedback"', '"Lancer la rétroaction"'),
    (MODEL, "selected ${id}", "sélectionnée ${id}"),
    (MODEL, " — edit after ${methodLabel(s.method)}: that method's credit is cancelled",
     " — édition après ${methodLabel(s.method)} : le crédit de cette méthode est annulé"),
    (MODEL, '"Run feedback: one pass pushing cells out of oversubscribed tiles."',
     '"Lancer la rétroaction : une passe qui pousse les cellules hors des tuiles sursaturées."'),
    (MODEL, '"Golden hidden; back to the congested seed."', '"Golden masqué ; retour à la graine encombrée."'),
    (MODEL, '"Revealed spread placement (study only — it never counts)."',
     '"Placement dispersé révélé (étude seule — il ne compte jamais)."'),
    (MODEL, '"Workspace reset to the congested seed."', '"Espace de travail réinitialisé à la graine encombrée."'),
    # field labels (longer keys first: "hottest tile (i,j) after the pass" contains "hottest tile (i,j)")
    (MODEL, '"hottest tile (i,j) after the pass"', '"tuile la plus chaude (i,j) après la passe"'),
    (MODEL, '"hottest tile (i,j)"', '"tuile la plus chaude (i,j)"'),
    (MODEL, '"its congestion"', '"sa congestion"'),
    (MODEL, '"congestion at tile (1,0)"', '"congestion de la tuile (1,0)"'),
    (MODEL, '"congestion at tile (2,0)"', '"congestion de la tuile (2,0)"'),
    (MODEL, '"tile the R2 rule picks (i,j)"', '"tuile choisie par la règle R2 (i,j)"'),
    (MODEL, '"total overflow after the pass"', '"débordement total après la passe"'),
    # model docblock
    (MODEL, "on page load, from the preset seed alone, from the reveal, or from one Run feedback click alone:",
     "au chargement de la page, depuis la graine seule, depuis la révélation, ou depuis un seul clic sur Lancer la rétroaction :"),
    # challenge levels
    (MODEL, 'level: "Intro"', 'level: "Initiation"'),
    (MODEL, 'level: "Practice"', 'level: "Exercice"'),
    (MODEL, 'level: "Challenge"', 'level: "Défi"'),
    # challenge 1 — read-hot
    (MODEL, 'title: "Read the hottest tile of your map"', 'title: "Lisez la tuile la plus chaude de votre carte"'),
    (MODEL, '"Type the hottest tile of YOUR current map as i,j and its congestion (2 decimals). Rule R2 decides: scan columns i outer, rows j inner, strict greater — the first maximum wins. The map must have a tile above 1."',
     '"Tapez la tuile la plus chaude de VOTRE carte courante en i,j et sa congestion (2 décimales). La règle R2 décide : balayage des colonnes i externe, des lignes j interne, strictement supérieur — le premier maximum gagne. La carte doit avoir une tuile au-dessus de 1."'),
    (MODEL, '"The seed lights tile (1,0) at 3.5. The typed numbers must match the map on screen, not a golden."',
     '"La graine allume la tuile (1,0) à 3.5. Les nombres tapés doivent correspondre à la carte à l\'écran, pas à une référence."'),
    # challenge 2 — own-matrix
    (MODEL, 'title: "Type two tiles of your own matrix"', 'title: "Tapez deux tuiles de votre propre matrice"'),
    (MODEL, '"Type the congestion (demand / capacity) of tile (1,0) and of tile (2,0) on YOUR current map, 2 decimals. Then move a cell and watch these change — the check always reads the map on screen."',
     '"Tapez la congestion (demande / capacité) des tuiles (1,0) et (2,0) sur VOTRE carte courante, à 2 décimales. Puis déplacez une cellule et regardez changer ces valeurs — la vérification lit toujours la carte à l\'écran."'),
    (MODEL, '"On the seed all demand sits in tile (1,0): 7 over capacity 2 = 3.5, and tile (2,0) is 0."',
     '"Sur la graine toute la demande est dans la tuile (1,0) : 7 sur capacité 2 = 3.5, et la tuile (2,0) vaut 0."'),
    # challenge 3 — boundary-drag
    (MODEL, 'title: "Drag A across the boundary x=6"', 'title: "Glissez A à travers la frontière x=6"'),
    (MODEL, '"Move cell A BY HAND (click A, then click the canvas at (6.5, 2)) across the GCell boundary x=6. The oversubscribed count must become 2 with total overflow 7.5 and the hottest tile still in column 1. No method button."',
     '"Déplacez la cellule A À LA MAIN (cliquez A, puis cliquez le canevas en (6.5, 2)) à travers la frontière de GCell x=6. Le compte de sursaturées doit devenir 2 avec un débordement total de 7.5 et la tuile la plus chaude toujours dans la colonne 1. Pas de bouton de méthode."'),
    (MODEL, '"With A at (6.5,2) the nets AB, AC and ABCD spill into tile (2,0) as well: count 2, total 7.5, hottest (1,0) at 3.625."',
     '"Avec A en (6.5,2), les réseaux AB, AC et ABCD débordent aussi dans la tuile (2,0) : compte 2, total 7.5, plus chaude (1,0) à 3.625."'),
    # challenge 4 — tie-break
    (MODEL, 'title: "Build a tie, name the R2 winner"', 'title: "Construisez un ex aequo, nommez le gagnant R2"'),
    (MODEL, '"Build BY HAND a placement where at least two tiles tie for the maximum congestion. Type the tile the written rule R2 picks: scan i (columns) outer, j (rows) inner, strict greater — the first maximum in that scan order wins."',
     '"Construisez À LA MAIN un placement où au moins deux tuiles sont à égalité pour la congestion maximale. Tapez la tuile choisie par la règle écrite R2 : balayage de i (colonnes) externe, j (lignes) interne, strictement supérieur — le premier maximum dans cet ordre de balayage gagne."'),
    (MODEL, '"Symmetric works: A(2,2) B(4,2) C(2,6) D(4,6) E(3,4) F(3,4) — all four tiles end at congestion 2.25, so R2 picks (0,0), not the last one."',
     '"Le symétrique marche : A(2,2) B(4,2) C(2,6) D(4,6) E(3,4) F(3,4) — les quatre tuiles finissent à congestion 2.25, donc R2 choisit (0,0), pas la dernière."'),
    # challenge 5 — cool-max
    (MODEL, 'title: "Cool the peak to 3 (by hand)"', 'title: "Refroidissez le pic à 3 (à la main)"'),
    (MODEL, '"Move cells BY HAND (no method button, no reveal) so the hottest tile of your map is at most 3.0 — and at least one tile must still be oversubscribed (count >= 1), so an empty map does not count."',
     '"Déplacez des cellules À LA MAIN (pas de bouton de méthode, pas de révélation) pour que la tuile la plus chaude de votre carte soit au plus 3.0 — et au moins une tuile doit rester sursaturée (compte >= 1), donc une carte vide ne compte pas."'),
    (MODEL, '"The seed is at 3.5. Spread the four big cells over both middle columns: A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) gives hottest 2.5."',
     '"La graine est à 3.5. Étalez les quatre grosses cellules sur les deux colonnes du milieu : A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) donne une plus chaude à 2.5."'),
    # challenge 6 — cool-2
    (MODEL, 'title: "Cooler: peak 2.5 and total overflow 6"', 'title: "Plus frais : pic 2.5 et débordement total 6"'),
    (MODEL, '"BY HAND: hottest tile at most 2.5, total overflow at most 6, and at least one tile still oversubscribed (count >= 1) so an empty map does not count. Spreading lowers the peak but raises the total — the bounds must hold on your map at once."',
     '"À LA MAIN : tuile la plus chaude au plus 2.5, débordement total au plus 6, et au moins une tuile encore sursaturée (compte >= 1) pour qu\'une carte vide ne compte pas. La dispersion abaisse le pic mais augmente le total — les bornes doivent tenir sur votre carte en même temps."'),
    (MODEL, '"The spread golden lowers the peak only to 3.33 and its total is 22. The placement A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) gives peak 2.5, total 6, count 2."',
     '"Le golden dispersé n\'abaisse le pic qu\'à 3.33 et son total vaut 22. Le placement A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) donne pic 2.5, total 6, compte 2."'),
    # challenge 7 — edge-hot
    (MODEL, 'title: "Move the hotspot to an edge column"', 'title: "Mettez le point chaud sur une colonne de bord"'),
    (MODEL, '"BY HAND: make the hottest tile of your map sit in an edge column (i=0 or i=3), still above 1, with total HPWL at least 8. No method button, no reveal."',
     '"À LA MAIN : que la tuile la plus chaude de votre carte soit dans une colonne de bord (i=0 ou i=3), toujours au-dessus de 1, avec un HPWL total d\'au moins 8. Pas de bouton de méthode, pas de révélation."'),
    (MODEL, '"Push E and F to the left edge next to the spread golden: A(1,1) B(8,1) C(1,5) D(8,5) E(1,3) F(2,3) makes tile (0,0) the hottest at 3.58 with HPWL 34."',
     '"Poussez E et F sur le bord gauche à côté du golden dispersé : A(1,1) B(8,1) C(1,5) D(8,5) E(1,3) F(2,3) rend la tuile (0,0) la plus chaude à 3.58 avec HPWL 34."'),
    # challenge 8 — joint-bound
    (MODEL, 'title: "Peak + total + HPWL bounded together"', 'title: "Pic + total + HPWL bornés ensemble"'),
    (MODEL, '"BY HAND, all three at once on your map: hottest tile at most 3.0, total overflow at most 6, AND total HPWL at least 8 (so collapsing all cells into one point does not count). No method button."',
     '"À LA MAIN, les trois en même temps sur votre carte : tuile la plus chaude au plus 3.0, débordement total au plus 6, ET HPWL total d\'au moins 8 (donc tout concentrer en un point ne compte pas). Pas de bouton de méthode."'),
    (MODEL, '"A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5): peak 2.5, total overflow 6, HPWL 10. The seed fails the peak, the spread golden fails the total, one feedback pass is a method result (and HPWL 3.5)."',
     '"A(5,2) B(7,2) C(5,3) D(7,3) E(5.5,2.5) F(6.5,2.5) : pic 2.5, débordement total 6, HPWL 10. La graine échoue sur le pic, le golden dispersé sur le total, une passe de rétroaction est un résultat de méthode (et HPWL 3.5)."'),
    # challenge 9 — feedback-cooled
    (MODEL, 'title: "Run feedback, read the cooled map"', 'title: "Lancez la rétroaction, lisez la carte refroidie"'),
    (MODEL, '"Click “Run feedback” ONCE from the seed and leave the result untouched. Type its total overflow, its hottest tile (i,j) and that tile\'s congestion. Cooled, not cold: the hottest tile sits at exactly 1.0, right at capacity."',
     '"Cliquez UNE FOIS sur « Lancer la rétroaction » depuis la graine et ne touchez plus au résultat. Tapez son débordement total, sa tuile la plus chaude (i,j) et la congestion de cette tuile. Refroidie, pas froide : la tuile la plus chaude est à exactement 1.0, pile à la capacité."'),
    (MODEL, '"One pass from the seed zeroes the total overflow but the hottest tile is (2,0) at exactly 1.0 — not below. Editing after the button cancels its credit, so do not touch the cells."',
     '"Une passe depuis la graine annule le débordement total mais la tuile la plus chaude est (2,0) à exactement 1.0 — pas en dessous. Éditer après le bouton annule son crédit, donc ne touchez pas aux cellules."'),
]
