"""Exact audit of Theorem 2 under the algorithm's unspecified LP tie-breaking."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


def _check_lp_point(
    tau: Fraction,
    kappa: Fraction,
    x: tuple[Fraction, Fraction],
    z: tuple[Fraction, Fraction],
) -> dict:
    required = 2 * tau
    rho = kappa / (1 + kappa)
    assert 0 < tau < 1
    assert 0 < kappa < tau / (1 - tau)
    assert all(0 <= value <= 1 for value in x + z)
    assert all(z_value <= x_value for x_value, z_value in zip(x, z))
    assert sum(z) >= required
    # For this singleton-edge instance, sum(x) >= sum(z) >= 2*tau.
    # Equality therefore supplies an exact primal lower-bound certificate.
    assert sum(x) == required
    rounded = [index for index, value in enumerate(x) if value >= rho]
    return {
        "tau": str(tau),
        "epsilon": str(1 - tau),
        "kappa": str(kappa),
        "rho": str(rho),
        "x": [str(value) for value in x],
        "z": [str(value) for value in z],
        "objective": str(sum(x)),
        "objective_lower_bound": str(required),
        "rounded_set": rounded,
        "feasible": True,
        "optimal": True,
    }


def _independent_scipy_solution(
    tau: Fraction, prefer_vertex: int
) -> tuple[float, float]:
    """Lexicographically select an endpoint of the optimal LP face."""
    required = float(2 * tau)
    # x0,x1,z0,z1. First-stage optimum is exactly required by a lower bound.
    # Fix that objective face, then maximize the preferred x coordinate.
    objective = np.zeros(4)
    objective[prefer_vertex] = -1.0
    a_ub = np.array(
        [
            [-1.0, 0.0, 1.0, 0.0],
            [0.0, -1.0, 0.0, 1.0],
            [0.0, 0.0, -1.0, -1.0],
        ]
    )
    b_ub = np.array([0.0, 0.0, -required])
    result = linprog(
        objective,
        A_ub=a_ub,
        b_ub=b_ub,
        A_eq=np.array([[1.0, 1.0, 0.0, 0.0]]),
        b_eq=np.array([required]),
        bounds=[(0.0, 1.0)] * 4,
        method="highs",
    )
    assert result.success
    assert abs(result.x[0] + result.x[1] - required) < 1e-10
    assert result.x[2] + result.x[3] + 1e-10 >= required
    return float(result.x[0]), float(result.x[1])


def run_claim2_exact(artifact_root: Path) -> dict:
    claim_dir = artifact_root / "claim_2"
    claim_dir.mkdir(parents=True, exist_ok=True)
    kappa = Fraction(1, 5)
    tau_low = Fraction(1, 5)
    tau_high = Fraction(1, 2)
    low = _check_lp_point(
        tau_low,
        kappa,
        (Fraction(2, 5), Fraction(0)),
        (Fraction(2, 5), Fraction(0)),
    )
    high = _check_lp_point(
        tau_high,
        kappa,
        (Fraction(0), Fraction(1)),
        (Fraction(0), Fraction(1)),
    )
    low_set = set(low["rounded_set"])
    high_set = set(high["rounded_set"])
    assert tau_low < tau_high
    assert not low_set <= high_set

    scipy_low = _independent_scipy_solution(tau_low, prefer_vertex=0)
    scipy_high = _independent_scipy_solution(tau_high, prefer_vertex=1)
    assert np.allclose(scipy_low, [0.4, 0.0], atol=1e-9)
    assert np.allclose(scipy_high, [0.0, 1.0], atol=1e-9)
    independent = {
        "status": "PASS",
        "solver": "scipy.optimize.linprog(method='highs')",
        "low_x": scipy_low,
        "high_x": scipy_high,
        "low_rounded": [0],
        "high_rounded": [1],
        "nested": False,
    }

    negative_rejected = False
    try:
        _check_lp_point(
            tau_low,
            kappa,
            (Fraction(1, 10), Fraction(0)),
            (Fraction(1, 10), Fraction(0)),
        )
    except AssertionError:
        negative_rejected = True
    assert negative_rejected
    negative = {
        "status": "PASS",
        "mutation": "reduce the low-tau LP mass from 2/5 to 1/10",
        "checker_rejected": True,
    }

    certificate = {
        "instance": {
            "vertices": [0, 1],
            "hyperedges": [[0], [1]],
            "weights": [1, 1],
            "total_weight": 2,
        },
        "low": low,
        "high": high,
        "tau_ordered": True,
        "nested": False,
        "parametric_maximal_chain": [[], [0, 1]],
        "lp_equals_parametric_at_low_tau": False,
    }
    (claim_dir / "counterexample.json").write_text(
        json.dumps(certificate, indent=2) + "\n"
    )
    (claim_dir / "independent_checker.json").write_text(
        json.dumps(independent, indent=2) + "\n"
    )
    (claim_dir / "negative_control.json").write_text(
        json.dumps(negative, indent=2) + "\n"
    )
    contract = {
        "claim_id": 2,
        "verdict": "FALSIFIED",
        "literal_quantifier": (
            "Fix kappa. For any target tau, the discrete subgraph obtained by "
            "solving the LP and threshold rounding equals the parametric "
            "min-cut output and the outputs are monotone in tau."
        ),
        "falsification_rule": (
            "Two ordered tau values satisfying the algorithm's kappa domain "
            "have exact optimal LP solutions whose thresholded vertex sets "
            "are not nested."
        ),
        "scope": (
            "This falsifies the algorithm as written without a canonical "
            "optimal-solution tie rule; it does not contradict nestedness of "
            "the maximal-source-side parametric min-cut chain."
        ),
    }
    (claim_dir / "claim_contract.json").write_text(
        json.dumps(contract, indent=2) + "\n"
    )
    (claim_dir / "source_audit.md").write_text(
        """# Claim 2 source audit

Current ar5iv anchors: Section 4.1 “LP Rounding Algorithm”, Section 4.2
“Monotonicity and Nested Structure”, Theorem 2 (`Thmtheorem2`), and Appendix D.
The algorithm says to “construct and solve” the LP for each target and return
the thresholded optimal solution; it supplies no canonical optimum or
tie-breaking rule. Theorem 2 fixes one slack parameter kappa and quantifies over
every target coverage tau, asserting equality with the parametric output and
monotonicity in tau.

The appendix proves only that there *exists* an optimal LP solution with a
nested two-set convex-combination structure. Existence does not make every
optimal solution returned by the stated algorithm canonical.
""",
    )
    (claim_dir / "method.md").write_text(
        """# Method

Use the smallest symmetric weighted hypergraph with two vertices and two
singleton hyperedges. Exact `Fraction` arithmetic checks feasibility,
optimality (by a matching algebraic lower bound), the paper's kappa domain, and
threshold rounding. A separate HiGHS solve lexicographically selects the same
two endpoints of the optimal faces. The negative control lowers required mass
and must be rejected.
""",
    )
    (claim_dir / "limitations.md").write_text(
        """# Limitations and interpretation

The counterexample is intentionally minimal because Theorem 2 is universally
quantified; scale is irrelevant to a valid counterexample. A repaired theorem
could specify the maximal-source-side parametric solution, or a canonical
nested LP optimum. Under that repaired interpretation the parametric family is
nested, and this evidence must not be described as contradicting that fact.
""",
    )
    (claim_dir / "EVAL.md").write_text(
        """# Claim 2 evaluation

Verdict: **FALSIFIED**

The literal LP algorithm admits exact optimal outputs `{0}` at tau=1/5 and
`{1}` at tau=1/2 for the same kappa=1/5. Since `{0}` is not a subset of `{1}`,
the claimed monotonicity and equality to the canonical parametric chain fail
without an additional tie-breaking assumption.
"""
    )
    return {
        "status": "FALSIFIED",
        "counterexample": certificate,
        "independent_checker": independent["status"],
        "negative_control": negative["status"],
    }
