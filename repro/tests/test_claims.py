from repro.src.run_claims import claim_four, claim_five, claim_one, claim_two_three
from repro.src.claim6_full import (
    GRID_EDGE_COUNT,
    TOTAL_EDGE_COUNT,
    forward_greedy,
    lp_select,
    parametric_route_chain,
    reverse_greedy,
    sample_route,
)

import numpy as np


def test_rounding_audit():
    assert claim_one()["instances"] >= 40


def test_parametric_audit():
    assert claim_two_three()["C2"]["nested"]


def test_exchangeable_rank_bound():
    assert claim_four()["exact_coverage"] >= .75


def test_reduction_separates_yes_and_no():
    result = claim_five()
    assert result["yes_max"] >= result["target_induced_edges"] > result["no_max"]


def test_navigation_dgp_and_methods():
    rng = np.random.default_rng(17)
    train = [sample_route(rng) for _ in range(20)]
    held_out = [sample_route(rng) for _ in range(20)]
    assert all(route and max(route) < TOTAL_EDGE_COUNT for route in train + held_out)
    assert any(max(route) >= GRID_EDGE_COUNT for route in train + held_out)
    chain = parametric_route_chain(train)
    assert all(left <= right for left, right in zip(chain, chain[1:]))
    for method in (
        lambda: lp_select(train, held_out, 0.6, chain)[0],
        lambda: forward_greedy(train, held_out, 0.6),
        lambda: reverse_greedy(train, held_out, 0.6),
    ):
        chosen = method()
        assert sum(set(route) <= set(chosen) for route in held_out) / 20 >= 0.6
