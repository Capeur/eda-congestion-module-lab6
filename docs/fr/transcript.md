# Carte de congestion

**Module id:** module02-05-congestion-map
**Lab:** congestion-map
**Tracks:** A (implémentation) · B (lab dans le navigateur)

## Slide 1 — Une puce encombrée s'allume

Pourquoi une puce a-t-elle besoin d'une carte de chaleur ? Imaginez six blocs de logique entassés dans un petit carré de la puce. Les vrais fils ne peuvent pas tous passer par ce carré. Une carte de chaleur de l'encombrement des fils peint ce carré en rouge, pour voir le bouchon avant le routage. Nous appelons cette carte la carte de congestion.

## Slide 2 — La puce et ses cellules

Notre puce est un rectangle de douze unités de large et huit de haut. Elle contient six cellules, nommées A à F. Une cellule est un bloc de logique qui a besoin de sa propre place. Les cellules sont reliées en six groupes appelés réseaux. Un réseau est un ensemble de cellules qu'un même fil doit connecter. Un placement dit où chaque cellule se trouve.

## Slide 3 — Découper la puce en tuiles

Avant le routage, nous coupons la puce en grandes cases appelées GCells. GCell signifie global cell, une grosse tuile de la carte. Notre grille a quatre colonnes et deux lignes, donc huit tuiles. Chaque tuile fait trois unités de large et quatre de haut. Nous nommons une tuile par sa colonne et sa ligne, en comptant à partir de zéro.

## Slide 4 — Demande, capacité et ratio

Chaque tuile a une capacité, le fil autorisé à la traverser. Nos tuiles autorisent deux. La demande d'une tuile est le fil qui veut la traverser. La congestion est la demande divisée par la capacité. Au-dessus de un, une tuile est sursaturée : plus de fil que de place.

## Slide 5 — La carte encombrée de la graine

Dans notre premier placement, appelé la graine, les six cellules sont dans une seule tuile. Cette tuile est la colonne un, ligne zéro, près du milieu de la puce. Les six réseaux y déposent leur fil, donc sa demande est sept. Sept divisé par deux donne une congestion de trois virgule cinq. Son débordement, demande moins capacité, vaut cinq. Faites une pause et devinez : d'où vient une demande de sept ?

## Slide 6 — Le partage égal de RUDY

La réponse : chaque réseau partage son fil également entre ses tuiles. Chaque réseau dessine la plus petite boîte autour de ses cellules, sa boîte englobante. La longueur de fil du réseau est la largeur de la boîte plus sa hauteur. La règle qui partage également est RUDY, pour rectangular uniform density.

## Slide 7 — Une part par tuile

La part d'une tuile est la longueur de fil divisée par son nombre de tuiles. Une boîte sur trois tuiles donne à chaque tuile un tiers. Les dépôts se font dans un ordre fixe : les réseaux dans leur ordre de liste. Dans un réseau, les tuiles se remplissent colonne par colonne, puis ligne par ligne.

## Slide 8 — La graine monte à sept

Regardez maintenant la carte de la graine se construire, réseau par réseau. Le réseau A B a une longueur de fil de un et ne touche que la tuile un zéro, donc il dépose un. Les réseaux C D, A C et B D déposent un chacun, portant la demande à quatre. Le grand réseau A B C D a une longueur de fil de deux, portant la demande à six. Le réseau E F dépose son un, et la demande finit à sept.

## Slide 9 — Des boîtes plus larges en dispersion

Dans le second placement, appelé dispersé, les cellules sont près des coins de la puce. Le réseau A B s'étend sur toute la puce avec une longueur de fil de sept sur trois tuiles de la ligne zéro. Chacune reçoit sept tiers, environ deux virgule trois trois.

## Slide 10 — Le grand réseau, le petit réseau

Le grand réseau A B C D a une longueur de fil de onze sur six tuiles. Chaque tuile reçoit onze sixièmes, environ un virgule huit trois. Le réseau E F a une longueur de fil de un sur deux tuiles, donc zéro virgule cinq chacune. Aucune boîte ne touche la colonne la plus à droite, donc elle reste vide.

## Slide 11 — La demande dispersée

Ajoutez les six dépôts et la demande dispersée apparaît. La ligne zéro vaut six virgule un sept, quatre virgule six sept, six virgule six sept. La ligne un vaut six virgule un sept, quatre virgule un sept, six virgule un sept. Faites une pause et devinez : quelle tuile est la plus chaude une fois divisé par deux ?

## Slide 12 — La tuile la plus chaude

La tuile la plus chaude est la colonne deux, ligne zéro, à trois virgule trois trois. Pour la trouver, nous balayons chaque tuile et gardons la plus grande valeur. Ce gagnant est l'argmax, la tuile du maximum.

## Slide 13 — Un ex aequo doit être écrit

Deux tuiles peuvent égaler le maximum. Si le code choisit l'une ou l'autre, deux programmes corrects peuvent diverger. Alors la règle de départage est écrite. Nous balayons colonne par colonne, puis ligne par ligne. Une tuile ne gagne que si elle est strictement plus grande que la meilleure vue. Le premier maximum dans cet ordre gagne.

## Slide 14 — Un exemple d'ex aequo

Voici un ex aequo. La colonne zéro contient un et deux. Les colonnes un et deux contiennent des zéros. La colonne trois contient deux et zéro. Deux tuiles sont à égalité à deux : colonne zéro ligne un, et colonne trois ligne zéro. Le balayage atteint la colonne zéro en premier, donc cette tuile gagne.

## Slide 15 — La tuile la plus chaude de la graine

Sur la carte de la graine, seule la tuile un zéro est non nulle. Sa valeur est trois virgule cinq. Une seule tuile non nulle ne peut pas égaler. L'argmax de la graine est la colonne un, ligne zéro, à trois virgule cinq.

## Slide 16 — Pourquoi la règle est sur le papier

Les résultats de référence du vérificateur ont besoin de la règle de départage, pour que tous les programmes corrects s'accordent. Faites une pause et devinez : la dispersion a fait baisser le pic. Le débordement total a-t-il aussi baissé ?

## Slide 17 — Non, le total a augmenté

Non : le débordement total a augmenté, pas diminué. Le pic est tombé de trois virgule cinq à trois virgule trois trois. Le débordement total est monté de cinq à vingt-deux. Le compte de tuiles sursaturées est monté de un à six. Le pic et le total sont deux mesures différentes d'une même carte.

## Slide 18 — La carte dispersée en nombres

Divisez les demandes dispersées par la capacité deux. La ligne zéro vaut trois virgule zéro huit, deux virgule trois trois, trois virgule trois trois. La ligne un vaut trois virgule zéro huit, deux virgule zéro huit, trois virgule zéro huit. Six des huit tuiles sont sursaturées. Le plus grand débordement est quatre virgule six sept, en colonne deux ligne zéro.

## Slide 19 — La règle exacte du débordement

Le débordement d'une tuile est la demande moins la capacité, borné à zéro. Une tuile ne compte que si son débordement est strictement au-dessus de zéro. À demande égale à la capacité, le débordement est exactement zéro. Une demande de zéro virgule cinq à capacité zéro virgule cinq compte pour zéro.

## Slide 20 — Le prix en longueur de fil

La dispersion a refroidi le pic, mais les fils sont devenus plus longs. La longueur de fil totale de la graine est sept, et celle de la dispersion trente-quatre. Le placement échange de la longueur de fil contre de la place dans les tuiles.

## Slide 21 — Monter la capacité

La capacité est un bouton que vous pouvez tourner. Sur la carte dispersée, la capacité cinq fait tomber le compte de six à quatre. Les deux tuiles de la colonne un repassent sous la limite. Sur la graine, la capacité un double le ratio à sept, et pourtant une seule tuile compte.

## Slide 22 — Une passe de rétroaction

Une passe de rétroaction pousse les cellules vers des tuiles plus fraîches. Sur la graine, une passe répartit la demande sur deux tuiles : un virgule cinq et deux. Divisé par deux, cela fait zéro virgule sept cinq et un. Le débordement total tombe de cinq à zéro, et le compte à zéro.

## Slide 23 — Un débordement nul est-il sain ?

Faites une pause et devinez : après cette passe le débordement total est zéro. Quelle est la valeur la plus chaude maintenant, et la carte est-elle vraiment saine ?

## Slide 24 — Refroidie, pas froide

Après la passe, aucune tuile n'est sursaturée : le compte est zéro. La tuile la plus chaude est la colonne deux ligne zéro, à exactement un. Elle est exactement à la capacité, pas en dessous. Refroidie n'est pas la même chose que froide.

## Slide 25 — Souvenez-vous

La congestion est la demande divisée par la capacité, par tuile. Au-dessus de un, une tuile est sursaturée. RUDY répartit la longueur de fil de chaque réseau également sur les tuiles que sa boîte touche. La tuile la plus chaude est l'argmax, et le premier maximum dans l'ordre de balayage gagne les ex aequo. Le débordement est la demande moins la capacité, compté strictement au-dessus de zéro. Le pic et le total peuvent évoluer en sens inverse.

## Slide 26 — À vous dans le navigateur

Ouvrez le lab congestion-map dans votre navigateur. La graine allume une tuile à congestion trois virgule cinq. Faites glisser la cellule A à travers la frontière de tuile et regardez le compte monter. Lancez la rétroaction et regardez le débordement total tomber à zéro.

## Slide 27 — À vous en Python

Sur le parcours Python, construisez la carte vous-même. Divisez une matrice de demande par la capacité pour obtenir la congestion. Trouvez la tuile la plus chaude avec la règle de départage écrite. Référence pour la graine : tuile la plus chaude colonne un ligne zéro à trois virgule cinq. Référence pour la dispersion : colonne deux ligne zéro à trois virgule trois trois.

## Slide 28 — Une dernière question

Faites une pause et devinez : vous avez dispersé les cellules et le pic de congestion a baissé. Le routeur devrait-il célébrer ? Vérifiez d'abord le débordement total.
