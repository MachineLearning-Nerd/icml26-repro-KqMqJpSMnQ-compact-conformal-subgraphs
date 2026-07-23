"""Build and validate an unpublished, additive update to the judged HF Space."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
UPLOAD = ROOT / "release" / "hf-space"
RELEASE = ROOT / "release"
ARTIFACTS = ROOT / ".openresearch" / "artifacts"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reader_pages() -> dict[str, str]:
    return {
        "pages/campaign-2026-07-overview/page.md": """# Claim-by-claim release candidate

This additive campaign reruns every prior check and directly answers the live
judge's criticisms. Evidence-local results are not a new judge score.

| Claim | Result | New decisive evidence |
| --- | --- | --- |
| 1 | VERIFIED | universal bicriteria certificate; sparse LPs to n=1,000,m=6,000 |
| 2 | FALSIFIED as written | exact optimal-tie counterexample; canonical parametric chain remains nested |
| 3 | VERIFIED | primary parametric-flow theorem plus exact reduction-size mapping |
| 4 | VERIFIED | 140 exact rank cases to n=1,000,000 plus 20,000 trials |
| 5 | VERIFIED | fixed ε=1/2 reduction certificate and two clique solvers |
| 6 | VERIFIED | 200 seeds, 20 exact 52-edge runs, both greedy baselines |

All computation used local CPU and one pinned uv environment. No GPU or
Hugging Face compute was used.
""",
        "pages/campaign-2026-07-claim6/page.md": """# Claim 6 — full navigation experiment

The rebuilt experiment uses the stated undirected 6×6 grid (60 road edges), a
distinct 20-edge bypass used with probability .15, 50 construction routes, and
50 held-out selection routes.

At φ=.75, the LP mean over 200 declared seeds is 57.38 edges (95% CI
55.92–58.84). Twenty seeds select exactly 52 edges. Seed 4 selects 52 with
held-out coverage .76, reproducing the paper's illustrated value.

| φ | LP | Forward greedy | Reverse greedy | Forward−LP 95% CI | Reverse−LP 95% CI |
| --- | ---: | ---: | ---: | ---: | ---: |
| .2 | 29.28 | 44.22 | 39.35 | [13.63,16.25] | [8.47,11.67] |
| .4 | 38.47 | 55.78 | 53.90 | [16.29,18.32] | [14.65,16.21] |
| .6 | 45.00 | 63.20 | 61.34 | [17.20,19.21] | [15.40,17.28] |
| .8 | 63.40 | 69.72 | 68.70 | [4.80,7.83] | [3.80,6.80] |

Both paired intervals are strictly above zero for every plotted φ≤.8. The
paper did not publish executable code, seeds, graph orientation, RNG, or tie
orders; those substitutions are explicit in the evidence.

- [Contract](../../../evidence/claim_6/claim_contract.json)
- [Raw 200-seed results](../../../evidence/claim_6/raw_results.jsonl)
- [Independent checker](../../../evidence/claim_6/independent_checker.json)
- [Negative control](../../../evidence/claim_6/negative_control.json)
- [Provenance](../../../evidence/claim_6/provenance.json)
""",
        "pages/campaign-2026-07-theory/page.md": """# Claims 1–5 — theorem-level evidence

Claims 1, 3, 4, and 5 are universal mathematical statements. The release does
not infer them from scaling plots: each uses an exact proof or reduction
certificate, and larger executions only stress the implementation.

Claim 2 is different. The source algorithm says to solve an LP at each target
but gives no canonical optimum rule. On two equal singleton hyperedges, exact
optimal solutions round to `{0}` at τ=1/5 and `{1}` at τ=1/2 for the same
κ=1/5. This falsifies literal algorithmic nestedness. It does not contradict
the nested maximal-source-side parametric family; specifying that family
repairs the claim.

- [Claim 1 evidence](../../../evidence/claim_1/EVAL.md)
- [Claim 2 exact counterexample](../../../evidence/claim_2/counterexample.json)
- [Claim 3 complexity certificate](../../../evidence/claim_3/proof_certificate.json)
- [Claim 4 exact rank checks](../../../evidence/claim_4/exact_rank_checks.json)
- [Claim 5 reduction certificate](../../../evidence/claim_5/proof_certificate.json)
""",
        "pages/campaign-2026-07-reproducibility/page.md": """# Reproducibility and release gate

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
""",
    }


def build_upload() -> list[str]:
    pages = reader_pages()
    for relative, content in pages.items():
        write(UPLOAD / relative, content)
    for claim_id in range(1, 7):
        source = ARTIFACTS / f"claim_{claim_id}"
        destination = UPLOAD / "evidence" / f"claim_{claim_id}"
        destination.mkdir(parents=True, exist_ok=True)
        for path in sorted(source.iterdir()):
            if path.is_file():
                shutil.copy2(path, destination / path.name)
    shutil.copy2(ARTIFACTS / "source" / "source_manifest.json", UPLOAD / "evidence" / "source_manifest.json")
    for relative in (
        "pyproject.toml",
        "uv.lock",
        "repro/config/campaign.json",
        "repro/src/claim2_exact.py",
        "repro/src/claim6_full.py",
        "repro/src/claims_theory_full.py",
        "repro/src/verify_gate.py",
    ):
        destination = UPLOAD / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, destination)
    return sorted(str(path.relative_to(UPLOAD)) for path in UPLOAD.rglob("*") if path.is_file())


def update_logbook(judged_tree: Path) -> None:
    logbook = json.loads((judged_tree / "logbook.json").read_text())
    additions = [
        ("campaign-2026-07-overview", "2026-07 campaign — overview"),
        ("campaign-2026-07-claim6", "2026-07 campaign — Claim 6"),
        ("campaign-2026-07-theory", "2026-07 campaign — Claims 1–5"),
        ("campaign-2026-07-reproducibility", "2026-07 campaign — reproducibility"),
    ]
    existing = {child["slug"] for child in logbook["root"]["children"]}
    for slug, title in additions:
        if slug not in existing:
            logbook["root"]["children"].append(
                {
                    "slug": slug,
                    "title": title,
                    "file": f"pages/{slug}/page.md",
                    "children": [],
                }
            )
    logbook["updated_at"] = "2026-07-23T23:30:00+05:30"
    (UPLOAD / "logbook.json").write_text(json.dumps(logbook, indent=2) + "\n")


def validate(judged_tree: Path, candidate_tree: Path, upload_paths: list[str]) -> None:
    if candidate_tree.exists():
        shutil.rmtree(candidate_tree)
    shutil.copytree(judged_tree, candidate_tree, ignore=shutil.ignore_patterns(".git"))
    shutil.copytree(UPLOAD, candidate_tree, dirs_exist_ok=True)

    old_files = {
        str(path.relative_to(judged_tree))
        for path in judged_tree.rglob("*")
        if path.is_file() and ".git" not in path.parts
    }
    new_files = {
        str(path.relative_to(candidate_tree))
        for path in candidate_tree.rglob("*")
        if path.is_file()
    }
    missing = sorted(old_files - new_files)
    assert not missing
    changed_old_files = sorted(
        relative
        for relative in old_files
        if sha256(judged_tree / relative) != sha256(candidate_tree / relative)
    )
    assert changed_old_files == ["logbook.json"]
    logbook = json.loads((candidate_tree / "logbook.json").read_text())
    children = logbook["root"]["children"]
    assert len({child["slug"] for child in children}) == len(children)
    for child in children:
        assert (candidate_tree / child["file"]).is_file()

    secret_patterns = [
        re.compile(r"hf_[A-Za-z0-9]{20,}"),
        re.compile(r"(?i)authorization\\s*:\\s*bearer"),
        re.compile(r"(?i)(api[_-]?key|access[_-]?token)\\s*[=:]\\s*['\"][^'\"]+"),
    ]
    findings = []
    for relative in upload_paths:
        text = (UPLOAD / relative).read_text(errors="strict")
        for pattern in secret_patterns:
            if pattern.search(text):
                findings.append({"path": relative, "pattern": pattern.pattern})
    assert not findings
    subset = {
        "judged_revision": "6bbed76df9e229c6577602a49b10f5de74c26e8b",
        "old_file_count": len(old_files),
        "candidate_file_count": len(new_files),
        "old_file_set_is_subset": True,
        "missing_old_files": [],
        "unchanged_old_file_count": len(old_files) - len(changed_old_files),
        "modified_old_files": changed_old_files,
        "modification_reason": "logbook.json adds four campaign pages; all 28 other judged files are byte-identical",
        "logbook_valid": True,
    }
    write(RELEASE / "subset-check.json", json.dumps(subset, indent=2))
    write(
        RELEASE / "secret-scan.json",
        json.dumps({"status": "PASS", "files_scanned": len(upload_paths), "findings": []}, indent=2),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--judged-tree", type=Path, required=True)
    parser.add_argument("--candidate-tree", type=Path, required=True)
    args = parser.parse_args()
    if UPLOAD.exists():
        shutil.rmtree(UPLOAD)
    UPLOAD.mkdir(parents=True)
    update_logbook(args.judged_tree)
    upload_paths = build_upload()
    validate(args.judged_tree, args.candidate_tree, upload_paths)
    write(RELEASE / "upload-allowlist.txt", "\n".join(upload_paths))
    manifest = "\n".join(f"{sha256(UPLOAD / path)}  {path}" for path in upload_paths)
    write(RELEASE / "upload-manifest.sha256", manifest)
    print(json.dumps({"upload_files": len(upload_paths), "candidate": str(args.candidate_tree)}))


if __name__ == "__main__":
    main()
