# Reproducibility and release gate

Exact fixed command:

```text
uv run --frozen python repro/src/run_claims.py --out outputs/claims.json && uv run --frozen python -m pytest repro/tests -q && uv run --frozen python repro/src/verify_gate.py
```

Every claim directory contains a contract, source audit, method, raw
machine-readable outputs, independent checker, negative control, pinned
environment and Git provenance, evaluation, and limitations. The cumulative
gate reruns the previously accepted evidence and exits nonzero if any new or
old check fails.

The judged revision `6bbed76df9e229c6577602a49b10f5de74c26e8b` was downloaded
before candidate work. Its 29-file tracked set is retained in full. This page
and the other campaign pages are additive.
