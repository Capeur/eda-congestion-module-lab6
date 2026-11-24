# Congestion heat map

**Module id:** module02-05-congestion-map
**Lab:** congestion-map
**Tracks:** A (implement) · B (browser lab)

## Slide 1 — A crowded chip lights up

Why does a chip need a heat map? Picture six blocks of logic crowded into one small square of the chip. Real wires cannot all fit through that square. A heat map of wire crowding paints that square red, so you see the jam before routing. We call that map the congestion map.

## Slide 2 — The chip and its cells

Our chip is a rectangle twelve units wide and eight units tall. It holds six cells, named A to F. A cell is a block of logic that needs its own spot. The cells are joined in six groups called nets. A net is a set of cells that one wire must connect. A placement says where every cell sits.

## Slide 3 — Cutting the chip into tiles

Before routing, we cut the chip into big squares called GCells. GCell stands for global cell, a coarse tile of the map. Our grid has four columns and two rows, so eight tiles. Each tile is three units wide and four units tall. We name a tile by its column and its row, counting from zero.

## Slide 4 — Demand, capacity, and the ratio

Each tile has a capacity, the wire allowed to cross it. Our tiles allow two. The demand of a tile is the wire that wants to cross it. Congestion is demand divided by capacity. Above one, a tile is oversubscribed: more wire than room.

## Slide 5 — The crowded seed map

In our first placement, called the seed, all six cells sit in one tile. That tile is column one, row zero, near the chip's middle. All six nets drop their wire there, so its demand is seven. Seven divided by two gives congestion three point five. Its overflow, demand minus capacity, is five. Pause and guess: where does a demand of seven come from?

## Slide 6 — RUDY's even split

The answer: each net splits its wire evenly over its tiles. Each net draws the smallest box around its cells, its bounding box. The net's wirelength is the box width plus its height. The rule that splits it evenly is RUDY, for rectangular uniform density.

## Slide 7 — One share per tile

A tile's share is the wirelength divided by its tile count. A box over three tiles gives each tile one third. Deposits happen in a fixed order: nets in their listed order. Inside one net, tiles fill column by column, then row by row.

## Slide 8 — The seed builds to seven

Now watch the seed map build, net by net. Net A B has wirelength one and touches only tile one zero, so it drops one. Nets C D, A C and B D drop one each, bringing demand to four. The big net A B C D has wirelength two, making demand six. Net E F drops its one, and the demand ends at seven.

## Slide 9 — Wider boxes in the spread

In the second placement, called spread, the cells sit near the chip's corners. Net A B stretches across the chip with wirelength seven over three tiles in row zero. Each gets seven thirds, about two point three three.

## Slide 10 — The big net, the small net

The big net A B C D has wirelength eleven over six tiles. Each tile gets eleven sixths, about one point eight three. Net E F has wirelength one over two tiles, so zero point five each. No box touches the rightmost column, so it stays empty.

## Slide 11 — The spread demand

Add the six deposits and the spread demand appears. Row zero reads six point one seven, four point six seven, six point six seven. Row one reads six point one seven, four point one seven, six point one seven. Pause and guess: which tile is hottest once we divide by two?

## Slide 12 — The hottest tile

The hottest tile is column two, row zero, at three point three three. To find it, we scan every tile and keep the largest value. That winner is the argmax, the tile of the maximum.

## Slide 13 — A tie must be written down

Two tiles can tie for the maximum. If code picks either one, two correct programs can disagree. So the tie-break is written down. We scan column by column, then row by row. A tile wins only if strictly greater than the best so far. The first maximum in that order wins.

## Slide 14 — A tie example

Here is a tie. Column zero holds one and two. Columns one and two hold zeros. Column three holds two and zero. Two tiles tie at two: column zero row one, and column three row zero. The scan reaches column zero first, so that tile wins.

## Slide 15 — The seed's hottest tile

On the seed map, only tile one zero is nonzero. Its value is three point five. One nonzero tile cannot tie. The argmax of the seed is column one, row zero, at three point five.

## Slide 16 — Why the rule is on paper

The checker's goldens need the tie-break, so all correct programs agree. Pause and guess: spreading lowered the peak. Did the total overflow fall too?

## Slide 17 — No, the total went up

No: the total overflow went up, not down. The peak fell from three point five to three point three three. The total overflow rose from five to twenty-two. The oversubscribed count rose from one to six. Peak and total are different measures of one map.

## Slide 18 — The spread map in numbers

Divide the spread demands by capacity two. Row zero reads three point zero eight, two point three three, three point three three. Row one reads three point zero eight, two point zero eight, three point zero eight. Six of the eight tiles are oversubscribed. The largest overflow is four point six seven, in column two row zero.

## Slide 19 — Overflow's exact rule

A tile's overflow is demand minus capacity, floored at zero. A tile counts only when its overflow is strictly above zero. At demand equal to capacity, the overflow is exactly zero. Demand zero point five at capacity zero point five counts as zero.

## Slide 20 — The price in wirelength

Spreading cooled the peak, but the wires grew longer. The seed's total wirelength is seven, and the spread's is thirty-four. Placement trades wirelength against room in the tiles.

## Slide 21 — Raising the capacity

Capacity is a knob you can turn. On the spread map, capacity five drops the count from six to four. The two tiles of column one fall back under the limit. On the seed, capacity one doubles the ratio to seven, yet still only one tile counts.

## Slide 22 — One feedback pass

A feedback pass nudges cells toward cooler tiles. On the seed, one pass splits the demand over two tiles: one point five and two. Divided by two, that is zero point seven five and one. The total overflow falls from five to zero, and the count to zero.

## Slide 23 — Is zero overflow healthy?

Pause and guess: after that pass the total overflow is zero. What is the hottest value now, and is the map truly healthy?

## Slide 24 — Cooled, not cold

After the pass, no tile is oversubscribed: the count is zero. The hottest tile is column two row zero, at exactly one. It sits right at capacity, not below it. Cooled is not the same as cold.

## Slide 25 — Remember

Congestion is demand divided by capacity, per tile. Above one, a tile is oversubscribed. RUDY splits each net's wirelength evenly over the tiles its box touches. The hottest tile is the argmax, and the first maximum in scan order wins ties. Overflow is demand minus capacity, counted strictly above zero. Peak and total can move in opposite directions.

## Slide 26 — Your turn in the browser

Open the congestion-map lab in your browser. The seed lights one tile at congestion three point five. Drag cell A across the tile boundary and watch the count rise. Press run feedback and watch the total overflow fall to zero.

## Slide 27 — Your turn in Python

On the Python track, build the map yourself. Divide a demand matrix by capacity for congestion. Find the hottest tile with the written tie-break. Golden seed hottest: column one row zero at three point five. Golden spread hottest: column two row zero at three point three three.

## Slide 28 — One last question

Pause and guess: you spread the cells and the peak congestion fell. Should the router celebrate? Check the total overflow first.
