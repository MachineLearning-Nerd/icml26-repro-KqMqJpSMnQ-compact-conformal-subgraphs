# Compact Conformal Subgraphs — claim-by-claim reproduction

[![Open in molab](https://marimo.io/molab-shield.svg)](https://molab.marimo.io/github/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/blob/main/notebooks/compact_conformal_subgraphs.py)

This clean-room reproduction tests all six claims from
[*Compact Conformal Subgraphs*](https://arxiv.org/abs/2602.07530) on local CPU.
The central 6×6 navigation experiment uses the stated 50 construction and 50
held-out routes with no scale reduction. Across 200 declared seeds, the LP
method averages 57.38 edges at φ=.75; 20 seeds reproduce the paper's 52-edge
realization, including seed 4 with .76 held-out coverage. Paired 95% intervals
show fewer LP edges than both greedy baselines at every plotted φ≤.8.

The theorem claims are checked at their actual quantifiers: exact proof
certificates are primary, with non-toy executions as implementation stress
tests. The LP bicriteria, parametric complexity, marginal coverage, and
constant-ε hardness claims are evidence-locally **VERIFIED**. The literal
LP-output nestedness claim is **FALSIFIED as written** by an exact optimal-tie
counterexample; this does not contradict the nested canonical parametric
min-cut family. These labels are reproduction results, not a new live-judge
score.

- [Illustrated claim-by-claim report](reports/claim-by-claim/report.md)
- [Self-contained marimo tutorial](notebooks/compact_conformal_subgraphs.py)
- Local notebook: `uv run --frozen marimo edit notebooks/compact_conformal_subgraphs.py`
- Local app: `uv run --frozen marimo run notebooks/compact_conformal_subgraphs.py`

Compute: Apple CPU, Python 3.12.11, uv 0.11.29, one locked repository `.venv`;
no GPU and no Hugging Face compute were used. Missing author code, seeds, graph
orientation, RNG, and tie orders are documented substitutions.

## Experiment log

| Branch / experiment | Purpose or change | Exact run command | Assessment / outcome | Compute |
| --- | --- | --- | --- | --- |
| `main` | Public landing page and presentation artifacts | Not run as an experiment (publication surface) | Awaiting approved mirror from the release candidate | — |
| [`orx/frozen-baseline-with-uv-environment`](https://github.com/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/tree/orx/frozen-baseline-with-uv-environment) | Freeze the judged 5/12 implementation under a reproducible uv lock | `uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py` | Reproduced the prior toy/theoretical checks and inconclusive Claim 6 state | Local CPU |
| [`orx/claim-6-paper-literal-50-plus-50`](https://github.com/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/tree/orx/claim-6-paper-literal-50-plus-50) | Implement the source-scale LP route and both greedy baselines over 200 seeds | `uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py` | Claim 6 VERIFIED: 20 exact 52-edge seeds; paired advantage through φ=.8 | Local CPU |
| [`orx/exact-lp-tie-breaking-theorem-audit`](https://github.com/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/tree/orx/exact-lp-tie-breaking-theorem-audit) | Audit the literal Theorem 2 LP-to-parametric equality under unspecified ties | `uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py` | Literal LP algorithm FALSIFIED; repaired canonical interpretation remains nested | Local CPU |
| [`orx/universal-certificates-and-scale-audits`](https://github.com/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/tree/orx/universal-certificates-and-scale-audits) | Replace toy evidence for Claims 1, 3, 4, and 5 with theorem-level certificates and larger checks | `uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py` | All four VERIFIED; seven regressions and all negative controls passed | Local CPU |
| [`orx/release-candidate-evidence-package`](https://github.com/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/tree/orx/release-candidate-evidence-package) | Package provenance, report, notebook, protected logbook, and manifests | `uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py` | Passed unchanged command and generated exact per-claim provenance | Local CPU |
| [`orx/final-evidence-snapshot`](https://github.com/MachineLearning-Nerd/icml26-repro-KqMqJpSMnQ-compact-conformal-subgraphs/tree/orx/final-evidence-snapshot) | Snapshot terminal evidence and the 29-file-preserving text-only Space bundle | `uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py` | Approval candidate; final unchanged-command gate pending | Local CPU |

## Reproduce

```bash
uv sync --frozen
uv run --frozen python repro/src/run_claims.py --out outputs/claims.json \
  && uv run --frozen python -m pytest repro/tests -q \
  && uv run --frozen python repro/src/verify_gate.py
```

Machine-readable contracts, raw data, independent checks, negative controls,
source audits, pinned environment data, and limitations are under
`.openresearch/artifacts/claim_*/`.
