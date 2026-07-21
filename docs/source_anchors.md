# Source anchors

Pinned primary source: arXiv 2602.07530 source archive, SHA-256
`9d325e820577d33c01e3d1de923157b4274ff944e85f6280389810df313f7922`.

| Claim | Primary-source location | Executed check |
|---|---|---|
| C1 | `statement.tex`, `mainproof.tex` | finite weighted-hypergraph LP rounding audit |
| C2 | `statement.tex`, `monotone.tex` | exact parametric set-sequence audit |
| C3 | `statement.tex`, `monotone.tex` | complete finite threshold sequence audit (not a hardware-speed claim) |
| C4 | `conformal_proof.tex` | exhaustive finite exchangeability/rank check |
| C5 | `hardness_compression.tex` | exact component-DP check of a constant-epsilon Clique reduction instance |
| C6 | `experiments.tex` | stated 6×6, 50-train/50-test routing protocol, CPU only |

The source calls the full-sequence complexity result `lem:lag-mon`; this
reproduction will not relabel an empirical finite audit as a proof of its
asymptotic soft-O runtime statement.

