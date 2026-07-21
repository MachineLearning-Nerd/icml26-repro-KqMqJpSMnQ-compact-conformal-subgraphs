# Evidence and scope

This is a source-anchored clean-room reproduction. The primary arXiv source is
vendored under `source/` and no official executable implementation was released.

Five claims have independent, retained CPU evidence:

- C1: 48 weighted hypergraphs pass the literal LP rounding loss and cardinality
  inequalities; the worst observed normalized loss and size ratios are 1.60 and
  1.25 respectively, both within the kappa=1 bounds of 2.
- C2: exact Lagrangian minimizer enumeration on 32 hypergraphs produces nested
  source-side sets for every enumerated breakpoint and interval.
- C3: the same exact audit constructs every finite supported set sequence,
  with at most four distinct sets on six-vertex instances. This is evidence for
  the finite sequence construction only; it is not presented as a measurement
  proving the paper's asymptotic soft-O bound.
- C4: an exhaustive 40,320-permutation split-conformal rank check reaches the
  phi=.75 bound exactly. A second 256-draw finite Stage-1 filtering check has
  coverage .71484375, above the phi-delta=.50 lower bound.
- C5: an exact component dynamic program validates a constant-epsilon Clique
  gadget instance: the YES target reaches 31 induced edges while the NO target
  reaches only 30.

C6 was executed at the paper's declared scale: 6×6 routing, 50 training and
50 held-out routes, ten CPU seeds. The clean-room implementation follows the
source's parametric min-cut split and fixed-order deletion, but the paper omits
code, seed, and calibration tie-breaking details. Its unseeded 52-edge figure
therefore cannot be identified or claimed as reproduced. The retained ten-run
mean is 64 selected edges and .774 held-out coverage at phi=.75.

## Scope & cost

| | This reproduction | Full replication |
|---|---|---|
| Scope | C1–C5 independent checks; C6 full stated synthetic DGP | Exact author code, seed, and figure pipeline unavailable |
| Hardware | local CPU | CPU; no GPU claimed or used |
| Time | ~1.5 s for the full retained claim run | source says under one minute for its LP instances |
| Cost | $0 local CPU | unknown without released implementation |
| Outcome | five verified claim outcomes; C6 inconclusive | not established |

