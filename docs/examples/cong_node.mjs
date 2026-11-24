// Helper of congestion_map_check.py --vs-node (read-only import of platform/assets/congestion-core.js).
//   node cong_node.mjs <file:// URL of congestion-core.js> <file:// URL of interactive-congestion-lab.js> < request.json > answer.json
// request: { instances: [{name, capacity, nets, placements: {run: positions}, caps}],
//            probes: {hottest_tie, hottest_zeros, cell_gcell: [[x,y]..], fb_clamp_x: {F:[x,y]}, fb_clamp_y: {F:[x,y]}, drag: [[x,y]..]} }
// For every run it returns the REAL rudyDemand/congestionMap/overflowMetrics/hottest results plus a deposit-event
// log built by a copy of the same fill loop; the copy is proven bit-equal to rudyDemand on the spot ("coreOk").
// The drag clamp is evaluated from the literals found in the real lab file (11.5 / 7.5), as written.
import fs from "node:fs";

const core = await import(process.argv[2]);
const {
  CAPACITY, NETS, CONGESTED_SEED, cellGcell, netBBox, hpwl, totalHpwl,
  rudyDemand, congestionMap, overflowMetrics, hottest, placementFeedbackLite,
} = core;
const netBbox = netBBox;

function fillTiles(b) {
  const a = cellGcell(b.x0, b.y0), c = cellGcell(b.x1, b.y1);
  const tiles = [];
  for (let i = Math.min(a.i, c.i); i <= Math.max(a.i, c.i); i++)
    for (let j = Math.min(a.j, c.j); j <= Math.max(a.j, c.j); j++) tiles.push([i, j]);
  return tiles;
}

function eventsOf(pos, nets) {
  const out = [];
  const demand = rudyDemand(pos); // start from the real thing? no — accumulate a copy and prove equality
  const acc = Array.from({ length: demand.length }, () => Array(demand[0].length).fill(0));
  for (const [idx, net] of nets.entries()) {
    const b = netBBox(net, pos);
    const wl = hpwl(net, pos);
    const tiles = fillTiles(b);
    const share = wl / Math.max(1, tiles.length);
    for (const [i, j] of tiles) acc[i][j] += share;
    out.push({ net: idx, pins: net, bbox: [b.x0, b.y0, b.x1, b.y1], hpwl: wl, tiles, share });
  }
  const same = JSON.stringify(acc) === JSON.stringify(demand);
  return { events: out, demand: acc, same };
}

const req = JSON.parse(fs.readFileSync(0, "utf8"));
const out = { coreOk: true, instances: [], probes: {} };

for (const inst of req.instances || []) {
  const cap = inst.capacity ?? CAPACITY;
  const nets = inst.nets ?? NETS;
  const runs = [];
  const sweep = {};
  for (const [name, pos] of Object.entries(inst.placements || {})) {
    const { events, demand, same } = eventsOf(pos, nets);
    if (!same) out.coreOk = false;
    const cong = congestionMap(demand, cap);
    const ov = overflowMetrics(demand, cap);
    const h = hottest(cong);
    runs.push({
      name, positions: pos, capacity: cap, events,
      demand, congestion: cong,
      overflow: { perCell: ov.perCell, total: ov.total, max: ov.max, count: ov.count },
      hottest: { i: h.i, j: h.j, v: h.v },
      hpwl: totalHpwl(pos, nets), net_hpwl: nets.map((n) => hpwl(n, pos)),
    });
    sweep[name] = (inst.caps || []).map((c) => {
      const o = overflowMetrics(demand, c);
      return { capacity: c, overflow: { perCell: o.perCell, total: o.total, max: o.max, count: o.count } };
    });
  }
  const entry = { name: inst.name, runs, sweep };
  const seed = (inst.placements || {}).congested_seed;
  if (seed) {
    const before = overflowMetrics(rudyDemand(seed), cap);
    const to = placementFeedbackLite(seed, cap);
    const after = overflowMetrics(rudyDemand(to), cap);
    entry.feedback = {
      to,
      overflowBefore: { total: before.total, max: before.max, count: before.count },
      overflowAfter: { total: after.total, max: after.max, count: after.count },
    };
  }
  out.instances.push(entry);
}

const p = req.probes || {};
out.probes.hottest_tie = hottest(p.hottest_tie);
out.probes.hottest_zeros = hottest(p.hottest_zeros);
out.probes.cell_gcell = (p.cell_gcell || []).map(([x, y]) => cellGcell(x, y));
for (const tag of ["fb_clamp_x", "fb_clamp_y"]) {
  if (p[tag]) {
    const pos = { ...CONGESTED_SEED, F: { x: p[tag].F[0], y: p[tag].F[1] } };
    const o = placementFeedbackLite(pos, CAPACITY);
    out.probes[tag] = { x: o.F.x, y: o.F.y };
  }
}
// the drag clamp, read AS WRITTEN from the real lab file
const labSrc = fs.readFileSync(process.argv[3].replace(/^file:\/\//, ""), "utf8");
const litX = /Math\.min\(11\.5, wx\)/.test(labSrc);
const litY = /Math\.min\(7\.5, wy\)/.test(labSrc);
out.probes.drag = {
  literalsFound: litX && litY,
  probes: (p.drag || []).map(([wx, wy]) => ({
    x: Math.max(0, Math.min(11.5, wx)),
    y: Math.max(0, Math.min(7.5, wy)),
  })),
};

process.stdout.write(JSON.stringify(out));
