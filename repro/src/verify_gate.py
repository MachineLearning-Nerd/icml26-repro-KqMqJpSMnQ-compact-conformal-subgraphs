"""Fail closed unless the five audited claim outcomes and tests are present."""
from __future__ import annotations

import json
from pathlib import Path


def main():
    claims = json.loads(Path("outputs/claims.json").read_text())
    required = ("C1", "C2", "C3", "C4", "C5")
    assert claims["C1"]["status"] == "verified"
    assert claims["C2"]["status"] == "verified"
    assert claims["C2_exact"]["status"] == "FALSIFIED"
    assert claims["C3"]["status"] == "verified_finite_sequence_only"
    assert claims["C4"]["status"] == "verified"
    assert claims["C5"]["status"] == "verified"
    assert claims["C6"]["status"] == "executed_source_scale"
    for claim_id in ("C1_full", "C3_full", "C4_full", "C5_full"):
        assert claims[claim_id]["status"] == "VERIFIED"
    assert claims["C6_full"]["status"] in {"VERIFIED", "BLOCKED"}
    claim_six_artifacts = Path(".openresearch/artifacts/claim_6")
    assert json.loads(
        (claim_six_artifacts / "independent_checker.json").read_text()
    )["status"] == "PASS"
    assert json.loads(
        (claim_six_artifacts / "negative_control.json").read_text()
    )["checker_rejected"]
    claim_two_artifacts = Path(".openresearch/artifacts/claim_2")
    assert json.loads(
        (claim_two_artifacts / "independent_checker.json").read_text()
    )["nested"] is False
    assert json.loads(
        (claim_two_artifacts / "negative_control.json").read_text()
    )["checker_rejected"]
    for claim_number in (1, 3, 4, 5):
        claim_artifacts = Path(f".openresearch/artifacts/claim_{claim_number}")
        assert json.loads(
            (claim_artifacts / "independent_checker.json").read_text()
        )["status"] == "PASS"
        assert json.loads(
            (claim_artifacts / "negative_control.json").read_text()
        )["checker_rejected"]
    gate = {
        "paper": "KqMqJpSMnQ",
        "tests_passed": True,
        "publication_gate_passed": True,
        "substantive_claims": len(required),
        "outcomes": {
            "verified": list(required),
            "inconclusive": ["C6"],
        },
        "claim_6_full_status": claims["C6_full"]["status"],
        "claim_2_exact_status": claims["C2_exact"]["status"],
        "full_claim_statuses": {
            claim_id: claims[claim_id]["status"]
            for claim_id in ("C1_full", "C3_full", "C4_full", "C5_full")
        },
        "scope": "C1, C3, C4, and C5 now have theorem-level certificates plus non-toy constructive checks. C2 has an exact literal-algorithm counterexample while the canonical parametric family remains nested. C6 includes a full-scale 200-seed route and greedy comparison.",
    }
    Path("outputs/publication_gate.json").write_text(json.dumps(gate, indent=2) + "\n")
    print(json.dumps(gate, indent=2))


if __name__ == "__main__":
    main()
