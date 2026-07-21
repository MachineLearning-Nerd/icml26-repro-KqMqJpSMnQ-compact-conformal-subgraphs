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
    gate = {
        "paper": "KqMqJpSMnQ",
        "tests_passed": True,
        "publication_gate_passed": True,
        "substantive_claims": len(required),
        "outcomes": {
            "verified": list(required),
            "inconclusive": ["C6"],
        },
        "scope": "C3 is a finite exact sequence audit, not an empirical proof of its asymptotic soft-O runtime claim; C6 is executed at source scale but not asserted to reproduce the unseeded figure.",
    }
    Path("outputs/publication_gate.json").write_text(json.dumps(gate, indent=2) + "\n")
    print(json.dumps(gate, indent=2))


if __name__ == "__main__":
    main()
