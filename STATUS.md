# Status — Compact Conformal Subgraphs

Current phase: five-claim local publication gate passed; public GitHub handoff
and canonical queueing are next.

The official executable implementation was not released. The pinned arXiv source
archive (SHA-256 `9d325e820577d33c01e3d1de923157b4274ff944e85f6280389810df313f7922`)
is retained in `source/`; every implemented item below is derived from its TeX.

Completed:

- Audited the six proposed claims against the primary source.
- Confirmed the synthetic protocol is a 6×6 grid with 50 train and 50 test
  routes, and no GPU is required or permitted.
- Created a Python 3.12 CPU environment and ran `repro/src/run_claims.py`.
  The independent C1 LP-rounding audit (48 instances), C2 exact nested-set
  audit (32 instances), C4 exhaustive 40,320-permutation rank audit, and C5
  exact reduction dynamic-program check passed. Four unit tests passed.
- Executed the stated 6×6/50/50 routing data-generating process for ten seeds
  locally with the source-defined parametric split and fixed-order deletion.
  The source does not give executable code, a seed, or all calibration
  tie-breaking details; C6 is therefore inconclusive, not claimed.
- Passed the fail-closed five-claim gate in `outputs/publication_gate.json`.
  Trackio pages, source anchors, retained commands, raw JSON, and the pinned
  Conclusion summary are in place.

Next:

- Secret-scan, create the public GitHub handoff, then atomically enqueue the
  gate-complete five-claim bundle through the shared backlog tool. C6 stays
  visibly inconclusive in the public evidence.

Cost policy: local CPU only; an HF `cpu-upgrade` job is permitted only if a
full-scale CPU sweep cannot complete locally. No T4, L4, or other GPU job.
