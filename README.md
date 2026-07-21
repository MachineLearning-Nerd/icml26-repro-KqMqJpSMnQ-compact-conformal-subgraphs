# Compact Conformal Subgraphs — reproduction

Clean-room CPU reproduction of OpenReview paper `KqMqJpSMnQ` (arXiv:2602.07530).
The authors' source archive is pinned under `source/`; no official executable
code was found during the audit. This repository therefore distinguishes
source-attested statements from independently executed checks.

Run (after creating the environment):

```bash
uv run --python 3.12 python repro/src/run_claims.py --out outputs/claims.json
uv run --python 3.12 python -m pytest repro/tests -q
uv run --python 3.12 python repro/src/verify_gate.py
```

The run uses only CPU and executes the paper's stated 6×6 / 50-route train /
50-route test protocol. It does not substitute a reduced benchmark or a GPU run.
The five-claim gate deliberately records the sixth (unseeded-figure) claim as
inconclusive rather than asserting an exact figure reproduction.
