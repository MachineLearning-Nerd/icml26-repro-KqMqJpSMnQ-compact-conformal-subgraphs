"""CPU-only, clean-room checks derived from the pinned TeX source."""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import networkx as nx
from scipy.optimize import linprog

try:
    from repro.src.claim6_full import run_claim6
except ModuleNotFoundError:  # Direct execution adds repro/src, not repo root.
    from claim6_full import run_claim6


def mass(edges, weights, chosen):
    return sum(w for edge, w in zip(edges, weights) if set(edge) <= chosen)


def optimum_size(n, edges, weights, target):
    for size in range(n + 1):
        for bits in itertools.combinations(range(n), size):
            if mass(edges, weights, set(bits)) + 1e-9 >= target:
                return size
    raise AssertionError("target was not coverable")


def lp_round(n, edges, weights, epsilon, kappa=1.0):
    """The LP and threshold rounding in statement.tex/mainproof.tex."""
    m, total = len(edges), float(sum(weights))
    # Variables are x_0..x_(n-1), z_0..z_(m-1).  z_e <= x_v.
    c = np.r_[np.ones(n), np.zeros(m)]
    aub, bub = [], []
    for j, edge in enumerate(edges):
        for v in edge:
            row = np.zeros(n + m)
            row[n + j], row[v] = 1, -1
            aub.append(row); bub.append(0)
    row = np.zeros(n + m); row[n:] = -np.asarray(weights)
    aub.append(row); bub.append(-(1 - epsilon) * total)
    result = linprog(c, A_ub=np.asarray(aub), b_ub=np.asarray(bub),
                     bounds=[(0, 1)] * (n + m), method="highs")
    if not result.success:
        raise RuntimeError(result.message)
    rho = kappa / (1 + kappa)
    chosen = {i for i, x in enumerate(result.x[:n]) if x >= rho - 1e-9}
    return chosen, result.x[:n]


def claim_one():
    rng = np.random.default_rng(20260721)
    checked = 0
    worst = {"loss_ratio": 0.0, "size_ratio": 0.0}
    for _ in range(48):
        n = 5
        edges = []
        for bits in itertools.chain.from_iterable(itertools.combinations(range(n), r) for r in (1, 2, 3)):
            if rng.random() < 0.26:
                edges.append(bits)
        if not edges:
            continue
        weights = rng.integers(1, 6, len(edges)).astype(float)
        epsilon, kappa = .25, 1.0
        chosen, _ = lp_round(n, edges, weights, epsilon, kappa)
        total = sum(weights)
        r = optimum_size(n, edges, weights, (1 - epsilon) * total)
        loss = total - mass(edges, weights, chosen)
        assert loss <= (1 + kappa) * epsilon * total + 1e-7
        assert len(chosen) <= (1 + 1 / kappa) * r + 1e-7
        checked += 1
        worst["loss_ratio"] = max(worst["loss_ratio"], loss / (epsilon * total))
        worst["size_ratio"] = max(worst["size_ratio"], len(chosen) / r)
    return {"status": "verified", "instances": checked, "worst_normalized": worst}


def parametric_sequence(n, edges, weights):
    """Exact finite audit of source-side Lagrangian minimizers.

    For each lambda, choose the union of all tied minimizers.  This is the
    maximal minimum cut convention used to obtain the nested source sides.
    """
    subsets = [set(s) for r in range(n + 1) for s in itertools.combinations(range(n), r)]
    values = [(len(s), mass(edges, weights, s)) for s in subsets]
    lambdas = {0.0}
    for (a, ea), (b, eb) in itertools.combinations(values, 2):
        if abs(ea - eb) > 1e-12:
            lam = (a - b) / (ea - eb)
            if lam >= 0: lambdas.add(float(lam))
    ordered = sorted(lambdas)
    probes = set(ordered)
    probes.update((a + b) / 2 for a, b in zip(ordered, ordered[1:]))
    probes.add((ordered[-1] + 1) if ordered else 1.0)
    sequence = []
    for lam in sorted(probes):
        objective = [a - lam * e for a, e in values]
        best = min(objective)
        union = set()
        for subset, value in zip(subsets, objective):
            if abs(value - best) < 1e-9:
                union |= subset
        if not sequence or union != sequence[-1]: sequence.append(union)
    return sequence


def claim_two_three():
    rng = np.random.default_rng(71)
    chain_counts = []
    for _ in range(32):
        n = 6
        edges = [bits for r in (1, 2, 3) for bits in itertools.combinations(range(n), r)
                 if rng.random() < .22]
        weights = rng.integers(1, 5, len(edges)).astype(float)
        chain = parametric_sequence(n, edges, weights)
        assert all(a <= b for a, b in zip(chain, chain[1:]))
        chain_counts.append(len(chain))
    return {
        "C2": {"status": "verified", "instances": len(chain_counts), "nested": True},
        "C3": {"status": "verified_finite_sequence_only", "instances": len(chain_counts),
               "max_distinct_sets": max(chain_counts), "vertices": 6,
               "note": "Finite exact sequence audit; no empirical run proves the source's asymptotic soft-O bound."},
    }


def claim_four():
    # Exact split-conformal rank audit, with the stage-1 filter retaining all
    # routes (delta=0).  Eight distinct exchangeable scores, 7 calibration.
    phi, ncal = .75, 7
    k = math.ceil(phi * (ncal + 1))
    successes = 0
    for perm in itertools.permutations(range(ncal + 1)):
        threshold = sorted(perm[:ncal])[k - 1]
        successes += int(perm[ncal] <= threshold)
    probability = successes / math.factorial(ncal + 1)
    assert probability >= phi
    # A second exact audit exercises the source proof's stage-1 subtraction.
    # There are four equally likely route types; the fourth is filtered out,
    # hence delta=1/4. Enumerating all i.i.d. split/calibration/test draws
    # checks the stated phi-delta lower bound without assuming continuity.
    filtered_scores = [.1, .4, .7, 1.0]
    stage_successes = 0
    for draw in itertools.product(range(4), repeat=4):
        threshold = sorted(filtered_scores[index] for index in draw[:3])[2]
        stage_successes += int(draw[3] < 3 and filtered_scores[draw[3]] <= threshold)
    stage_coverage = stage_successes / 4**4
    assert stage_coverage >= .75 - .25
    return {"status": "verified", "phi": phi, "delta": 0.0, "exact_coverage": probability,
            "permutations": math.factorial(ncal + 1), "rank": k,
            "stage_one_audit": {"phi": .75, "delta": .25, "exact_coverage": stage_coverage,
                                "draws": 4**4, "bound": .5}}


def component_dp(components, budget):
    dp = [-10**9] * (budget + 1); dp[0] = 0
    for options in components:
        nxt = [-10**9] * (budget + 1)
        for used, base in enumerate(dp):
            for size, edges in options:
                if used + size <= budget:
                    nxt[used + size] = max(nxt[used + size], base + edges)
        dp = nxt
    return max(dp)


def reduction_instance(kind):
    # Constant-epsilon instance of the construction in hardness_compression.tex.
    # Both graphs have m=3; K3 has a 3-clique and K1,3 does not.
    eps, m, r, c, s, d = .5, 3, 3, 8, 8, 3
    l_yes = math.comb(s, 2) + math.comb(r, 2)
    W = 2 * l_yes - 1
    padding = W - (c * m + math.comb(s, 2))
    assert padding >= 0 and l_yes - 1 < (1-eps)*W <= l_yes and s - 1 > 2*d
    if kind == "yes":
        base = [(0, 0), (1, 0), (1, 0), (2, 1), (2, 1), (2, 1), (3, 3)]
    else:  # K1,3: the selected leaves have no induced edge.
        base = [(0, 0), (1, 0), (2, 1), (2, 0), (3, 2), (3, 0), (4, 3)]
    components = [base] * c
    components.append([(t, math.comb(t, 2)) for t in range(s + 1)])
    components.extend([[(0, 0), (1, 0), (2, 1)]] * padding)
    return component_dp(components, r + s), l_yes, {"c": c, "s": s, "padding": padding, "W": W}


def claim_five():
    yes, target, params = reduction_instance("yes")
    no, _, _ = reduction_instance("no")
    assert yes >= target and no < target
    return {"status": "verified", "target_induced_edges": target,
            "yes_max": yes, "no_max": no, "parameters": params}


def sample_route(rng):
    if rng.random() < .15:
        return tuple(range(60, 80))
    # 6x6 directed right/down grid: 30 horizontal + 30 vertical edges.
    weights = rng.uniform(.1, 2, 60)
    dist = [float("inf")] * 36; parent = [None] * 36; dist[0] = 0.
    for u in range(36):
        row, col = divmod(u, 6)
        for v, edge in ((u + 1, row * 5 + col) if col < 5 else (None, None),
                        (u + 6, 30 + row * 6 + col) if row < 5 else (None, None)):
            if v is not None and dist[u] + weights[edge] < dist[v]:
                dist[v] = dist[u] + weights[edge]; parent[v] = (u, edge)
    path, node = [], 35
    while node:
        node, edge = parent[node]; path.append(edge)
    return tuple(sorted(path))


def lagrangian_cut(routes, lam):
    """Source-side minimum cut for the network in `small_conformal.tex`."""
    counts = Counter(routes)
    graph = nx.DiGraph()
    graph.add_nodes_from(("s", "t"))
    # Any finite cut can cost at most 80, so this is safely infinite here.
    infinity = 10_000.0
    for index, (route, weight) in enumerate(counts.items()):
        hnode = f"h{index}"
        graph.add_edge("s", hnode, capacity=lam * weight)
        for vertex in route:
            graph.add_edge(hnode, f"v{vertex}", capacity=infinity)
    for vertex in range(80):
        graph.add_edge(f"v{vertex}", "t", capacity=1.0)
    _, partition = nx.minimum_cut(graph, "s", "t", flow_func=nx.algorithms.flow.preflow_push)
    return frozenset(int(node[1:]) for node in partition[0] if node.startswith("v"))


def parametric_route_chain(routes):
    """Discover the complete supported min-cut chain by breakpoint recursion.

    At a candidate breakpoint, a tiny positive perturbation requests the
    maximal (post-breakpoint) source side. This is the tie convention needed
    for the nested family in the source proof.
    """
    counts = Counter(routes)
    route_edges, route_weights = list(counts), list(counts.values())
    low, high = frozenset(), lagrangian_cut(routes, 100.0)
    seen = {(low, high)}

    def induced(chosen):
        return mass(route_edges, route_weights, set(chosen))

    def refine(left, right):
        if left == right:
            return [left]
        left_mass, right_mass = induced(left), induced(right)
        if right_mass <= left_mass:
            return [left, right]
        lam = (len(right) - len(left)) / (right_mass - left_mass)
        middle = lagrangian_cut(routes, lam * (1 + 1e-10) + 1e-10)
        # A direct adjacent pair has no strictly supported intermediate set.
        if middle == left or middle == right or (left, middle) in seen:
            return [left, right]
        assert left <= middle <= right
        seen.add((left, middle)); seen.add((middle, right))
        return refine(left, middle)[:-1] + refine(middle, right)

    chain = refine(low, high)
    assert all(a <= b for a, b in zip(chain, chain[1:]))
    return chain


def route_solution(train, phi):
    """Literal fixed-context procedure from `small_conformal.tex`.

    The first half constructs the parametric sequence; the second half selects
    the first set attaining phi, followed by its prescribed fixed-order
    deletion within the final increment.
    """
    sequence_routes, calibration_routes = train[:25], train[25:]
    chain = parametric_route_chain(sequence_routes)
    coverage = lambda chosen: sum(set(route) <= chosen for route in calibration_routes) / len(calibration_routes)
    selected_index = next((i for i, chosen in enumerate(chain) if coverage(chosen) >= phi), None)
    if selected_index is None:
        # This is the source's exceptional "add vertices in fixed order" path.
        selected = set(chain[-1])
        for vertex in range(80):
            selected.add(vertex)
            if coverage(selected) >= phi: break
    else:
        selected = set(chain[selected_index])
        previous = chain[selected_index - 1] if selected_index else frozenset()
        for vertex in sorted(selected - previous):
            candidate = selected - {vertex}
            if coverage(candidate) >= phi:
                selected = candidate
    return selected, len(chain)


def claim_six():
    # The source specifies the DGP but no seed, executable code, or precise LP
    # tie-breaking. We therefore report the literal fixed-seed clean-room result
    # and do not force it to match the figure's 52-edge realization.
    records = []
    for seed in range(10):
        rng = np.random.default_rng(seed)
        train = [sample_route(rng) for _ in range(50)]
        test = [sample_route(rng) for _ in range(50)]
        chosen, chain_size = route_solution(train, .75)
        coverage = sum(set(route) <= chosen for route in test) / 50
        records.append({"seed": seed, "edges": len(chosen), "test_coverage": coverage,
                        "parametric_sets": chain_size})
    return {"status": "executed_source_scale", "grid": "6x6", "train_routes": 50,
            "test_routes": 50, "runs": records,
            "mean_edges": float(np.mean([r["edges"] for r in records])),
            "mean_test_coverage": float(np.mean([r["test_coverage"] for r in records])),
            "note": "Literal source-defined split, parametric-min-cut sequence, and fixed-order deletion; CPU only. The source gives no seed or code, so this does not identify which run produced its 52-edge visualization."}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--out", required=True)
    args = parser.parse_args()
    config = json.loads(Path("repro/config/campaign.json").read_text())
    result = {"source": "arXiv:2602.07530", "C1": claim_one()}
    result.update(claim_two_three())
    result["C4"] = claim_four(); result["C5"] = claim_five(); result["C6"] = claim_six()
    result["C6_full"] = run_claim6(
        config["claim_6"], Path(".openresearch/artifacts")
    )
    path = Path(args.out); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
