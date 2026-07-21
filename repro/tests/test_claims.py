from repro.src.run_claims import claim_four, claim_five, claim_one, claim_two_three


def test_rounding_audit():
    assert claim_one()["instances"] >= 40


def test_parametric_audit():
    assert claim_two_three()["C2"]["nested"]


def test_exchangeable_rank_bound():
    assert claim_four()["exact_coverage"] >= .75


def test_reduction_separates_yes_and_no():
    result = claim_five()
    assert result["yes_max"] >= result["target_induced_edges"] > result["no_max"]
