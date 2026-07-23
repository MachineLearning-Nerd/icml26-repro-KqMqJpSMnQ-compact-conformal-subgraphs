# Method

This run uses committed selection mode `paper_literal`. It regenerates all
routes from seeds 0–199, builds the complete supported parametric
minimum-cut chain once per seed, applies the paper's fixed-order final deletion,
and implements the two greedy definitions from Section 5.1. Every reported set
is recomputed by an independent checker directly from raw routes.

The paper-figure points are digitized only as a forensic curve reference. They
are never used as raw observations or as inputs to the verifier.
