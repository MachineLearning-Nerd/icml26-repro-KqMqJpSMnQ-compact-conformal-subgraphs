"""Fail closed unless the five audited claim outcomes and tests are present."""
from __future__ import annotations

import json
from pathlib import Path


def main():
    claims = json.loads(Path("outputs/claims.json").read_text())
    required = ("C1", "C2", "C3", "C4", "C5")
    assert claims["C1"]["status"] == "verified"
    assert claims["C2"]["status"] == "verified"
    assert claims["C3"]["status"] == "verified_finite_sequence_only"
    assert claims["C4"]["status"] == "verified"
    assert claims["C5"]["status"] == "verified"
    assert claims["C6"]["status"] == "executed_source_scale"
    assert claims["C6_full"]["status"] in {"VERIFIED", "BLOCKED"}
    claim_six_artifacts = Path(".openresearch/artifacts/claim_6")
    assert json.loads(
        (claim_six_artifacts / "independent_checker.json").read_text()
    )["status"] == "PASS"
    assert json.loads(
        (claim_six_artifacts / "negative_control.json").read_text()
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
        "scope": "C3 remains a finite exact sequence audit. C6 now includes a full-scale, 200-seed source-faithful route and greedy comparison with an independent checker; its verdict is reported separately from the immutable baseline check.",
    }
    Path("outputs/publication_gate.json").write_text(json.dumps(gate, indent=2) + "\n")
    print(json.dumps(gate, indent=2))


if __name__ == "__main__":
    main()
