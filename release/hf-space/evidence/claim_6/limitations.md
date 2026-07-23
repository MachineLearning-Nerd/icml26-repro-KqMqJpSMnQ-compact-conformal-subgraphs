# Limitations and deviations

The paper does not release executable code, seeds, graph directionality, RNG,
or tie-breaking. This run uses the standard undirected interpretation of a
6x6 road grid and an ascending edge-id tie order. In paper-literal mode the
held-out routes select the displayed subgraph exactly as Section 5 describes,
so those same routes are not an additional independent generalization set.
The 95% intervals quantify seed variability of this declared implementation;
they do not reconstruct the authors' missing randomness.
