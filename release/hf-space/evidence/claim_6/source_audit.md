# Claim 6 source audit

Primary current source: ar5iv HTML for arXiv:2602.07530, retrieved
2026-07-23 with an explicit browser User-Agent, SHA-256
`c2f69b82d308ef5a75b5e4eba386a645ba45093a37a287d1cef31e775693d288`.

Anchors: Section 5.1, Figure 1(b,c), paragraphs “Greedy Baselines” and
“Synthetic Routing Experiment”. The text specifies a 6x6 grid, opposite-corner
routing, Uniform[0.1,2] random edge weights, 85% grid traffic, a 20-edge bypass
used by 15%, and 50 train plus 50 held-out routes. It reports a 52-edge LP
selection at phi=0.75 and says LP is significantly more compressed than both
greedy methods for every plotted phi <= 0.8. No code, seeds, graph orientation,
RNG, shortest-path tie rule, or greedy tie order is supplied.
