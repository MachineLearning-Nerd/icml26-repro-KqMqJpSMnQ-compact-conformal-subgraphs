"""Full-scale synthetic navigation experiment from Section 5.

The implementation deliberately keeps the paper's two plausible split
interpretations configurable in committed JSON.  All randomness is generated
from explicit NumPy seeds and all reported sets are checked independently.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import platform
import time
from collections import Counter
from pathlib import Path
from typing import Iterable, Sequence

import networkx as nx
import numpy as np
from scipy import stats

GRID_SIDE = 6
GRID_EDGE_COUNT = 60
BYPASS_EDGE_COUNT = 20
TOTAL_EDGE_COUNT = GRID_EDGE_COUNT + BYPASS_EDGE_COUNT
TRAIN_ROUTES = 50
TEST_ROUTES = 50
PAPER_FIGURE_MEANS = {
    "phi": [0.2, 0.4, 0.6, 0.8, 0.9, 1.0],
    # Digitized from the plotted marker centers. These are forensic references,
    # not substituted raw author data.
    "lp": [32.5, 41.0, 46.5, 58.0, 74.0, 82.0],
    "forward": [48.0, 60.5, 68.0, 74.0, 77.5, 82.5],
    "reverse": [39.0, 54.0, 63.0, 69.0, 73.0, 79.5],
}


def _grid_edges() -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for row in range(GRID_SIDE):
        for col in range(GRID_SIDE):
            node = row * GRID_SIDE + col
            if col + 1 < GRID_SIDE:
                edges.append((node, node + 1))
            if row + 1 < GRID_SIDE:
                edges.append((node, node + GRID_SIDE))
    assert len(edges) == GRID_EDGE_COUNT
    return edges


GRID_EDGES = _grid_edges()
GRID_EDGE_IDS = {tuple(sorted(edge)): index for index, edge in enumerate(GRID_EDGES)}


def sample_route(rng: np.random.Generator) -> tuple[int, ...]:
    """Sample one route from the exact Section 5 mixture.

    Grid paths use an undirected 6x6 grid, 60 independently reweighted road
    edges, and a weighted shortest path between opposite corners. The bypass
    consists of 20 distinct edges and is selected with probability 0.15.
    """
    if rng.random() < 0.15:
        return tuple(range(GRID_EDGE_COUNT, TOTAL_EDGE_COUNT))
    weights = rng.uniform(0.1, 2.0, GRID_EDGE_COUNT)
    graph = nx.Graph()
    for edge_id, (left, right) in enumerate(GRID_EDGES):
        graph.add_edge(left, right, weight=float(weights[edge_id]))
    nodes = nx.shortest_path(
        graph, source=0, target=GRID_SIDE * GRID_SIDE - 1, weight="weight"
    )
    edge_ids = [
        GRID_EDGE_IDS[tuple(sorted((left, right)))]
        for left, right in zip(nodes, nodes[1:])
    ]
    return tuple(sorted(edge_ids))


def coverage(routes: Sequence[Sequence[int]], chosen: Iterable[int]) -> float:
    selected = set(chosen)
    return sum(set(route) <= selected for route in routes) / len(routes)


def _mass(
    route_edges: Sequence[Sequence[int]], route_weights: Sequence[int], chosen: set[int]
) -> int:
    return sum(
        weight
        for route, weight in zip(route_edges, route_weights)
        if set(route) <= chosen
    )


def lagrangian_cut(routes: Sequence[Sequence[int]], lam: float) -> frozenset[int]:
    counts = Counter(tuple(route) for route in routes)
    graph = nx.DiGraph()
    graph.add_nodes_from(("s", "t"))
    # Any finite cut in this instance is at most 80 + lambda*50.
    infinity = 1_000_000.0
    for index, (route, weight) in enumerate(sorted(counts.items())):
        route_node = f"h{index}"
        graph.add_edge("s", route_node, capacity=lam * weight)
        for edge_id in route:
            graph.add_edge(route_node, f"v{edge_id}", capacity=infinity)
    for edge_id in range(TOTAL_EDGE_COUNT):
        graph.add_edge(f"v{edge_id}", "t", capacity=1.0)
    _, partition = nx.minimum_cut(
        graph, "s", "t", flow_func=nx.algorithms.flow.preflow_push
    )
    return frozenset(
        int(node[1:]) for node in partition[0] if node.startswith("v")
    )


def parametric_route_chain(
    routes: Sequence[Sequence[int]],
) -> list[frozenset[int]]:
    """Discover every supported source-side min-cut by breakpoint recursion."""
    counts = Counter(tuple(route) for route in routes)
    route_edges, route_weights = list(counts), list(counts.values())
    low = frozenset()
    high = lagrangian_cut(routes, 100.0)
    visited_pairs: set[tuple[frozenset[int], frozenset[int]]] = {(low, high)}

    def induced(chosen: frozenset[int]) -> int:
        return _mass(route_edges, route_weights, set(chosen))

    def refine(
        left: frozenset[int], right: frozenset[int]
    ) -> list[frozenset[int]]:
        if left == right:
            return [left]
        left_mass, right_mass = induced(left), induced(right)
        if right_mass <= left_mass:
            return [left, right]
        breakpoint = (len(right) - len(left)) / (right_mass - left_mass)
        middle = lagrangian_cut(routes, breakpoint * (1 + 1e-10) + 1e-10)
        if (
            middle == left
            or middle == right
            or (left, middle) in visited_pairs
        ):
            return [left, right]
        assert left <= middle <= right
        visited_pairs.add((left, middle))
        visited_pairs.add((middle, right))
        return refine(left, middle)[:-1] + refine(middle, right)

    chain = refine(low, high)
    assert all(left <= right for left, right in zip(chain, chain[1:]))
    return chain


def lp_select(
    construction_routes: Sequence[Sequence[int]],
    selection_routes: Sequence[Sequence[int]],
    phi: float,
    chain: Sequence[frozenset[int]] | None = None,
) -> tuple[frozenset[int], int]:
    """Paper's nested-min-cut selection plus fixed-order final deletion."""
    if chain is None:
        chain = parametric_route_chain(construction_routes)
    selected_index = next(
        (
            index
            for index, candidate in enumerate(chain)
            if coverage(selection_routes, candidate) + 1e-12 >= phi
        ),
        None,
    )
    if selected_index is None:
        selected = set(chain[-1])
        for edge_id in range(TOTAL_EDGE_COUNT):
            selected.add(edge_id)
            if coverage(selection_routes, selected) + 1e-12 >= phi:
                break
    else:
        selected = set(chain[selected_index])
        previous = chain[selected_index - 1] if selected_index else frozenset()
        for edge_id in sorted(selected - previous):
            candidate = selected - {edge_id}
            if coverage(selection_routes, candidate) + 1e-12 >= phi:
                selected = candidate
    return frozenset(selected), len(chain)


def forward_greedy(
    construction_routes: Sequence[Sequence[int]],
    selection_routes: Sequence[Sequence[int]],
    phi: float,
) -> frozenset[int]:
    counts = Counter(
        edge_id for route in construction_routes for edge_id in set(route)
    )
    order = sorted(range(TOTAL_EDGE_COUNT), key=lambda edge: (-counts[edge], edge))
    selected: set[int] = set()
    for edge_id in order:
        selected.add(edge_id)
        if coverage(selection_routes, selected) + 1e-12 >= phi:
            break
    return frozenset(selected)


def reverse_greedy(
    construction_routes: Sequence[Sequence[int]],
    selection_routes: Sequence[Sequence[int]],
    phi: float,
) -> frozenset[int]:
    selected = set(range(TOTAL_EDGE_COUNT))
    active_routes = [tuple(route) for route in construction_routes]
    while selected:
        counts = Counter(
            edge_id for route in active_routes for edge_id in set(route)
        )
        edge_id = min(selected, key=lambda edge: (counts[edge], edge))
        candidate = selected - {edge_id}
        if coverage(selection_routes, candidate) + 1e-12 < phi:
            break
        selected = candidate
        active_routes = [route for route in active_routes if edge_id not in route]
    return frozenset(selected)


def _mean_interval(values: Sequence[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    mean = float(array.mean())
    if len(array) == 1:
        return {"mean": mean, "sd": 0.0, "ci95_low": mean, "ci95_high": mean}
    sd = float(array.std(ddof=1))
    half_width = float(
        stats.t.ppf(0.975, len(array) - 1) * sd / math.sqrt(len(array))
    )
    return {
        "mean": mean,
        "sd": sd,
        "ci95_low": mean - half_width,
        "ci95_high": mean + half_width,
    }


def _route_digest(routes: Sequence[Sequence[int]]) -> str:
    payload = json.dumps([list(route) for route in routes], separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def _independent_check(record: dict, phi_values: Sequence[float]) -> None:
    for route_group in ("construction_routes", "selection_routes", "evaluation_routes"):
        for route in record[route_group]:
            assert route
            assert all(0 <= edge_id < TOTAL_EDGE_COUNT for edge_id in route)
            assert len(route) == len(set(route))
    assert record["construction_digest"] == _route_digest(
        record["construction_routes"]
    )
    assert record["selection_digest"] == _route_digest(record["selection_routes"])
    assert record["evaluation_digest"] == _route_digest(record["evaluation_routes"])
    for phi in phi_values:
        key = str(phi)
        for method in ("lp", "forward", "reverse"):
            chosen = record["results"][key][method]["chosen"]
            assert len(chosen) == len(set(chosen))
            assert record["results"][key][method]["edges"] == len(chosen)
            expected_selection = coverage(record["selection_routes"], chosen)
            expected_evaluation = coverage(record["evaluation_routes"], chosen)
            assert abs(
                expected_selection
                - record["results"][key][method]["selection_coverage"]
            ) < 1e-12
            assert abs(
                expected_evaluation
                - record["results"][key][method]["evaluation_coverage"]
            ) < 1e-12
            assert expected_selection + 1e-12 >= phi


def _write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def run_claim6(config: dict, artifact_root: Path) -> dict:
    started_wall = time.perf_counter()
    started_cpu = time.process_time()
    selection_mode = config["selection_mode"]
    seeds = list(range(int(config["seeds"])))
    phi_values = [float(phi) for phi in config["phi_values"]]
    claim_dir = artifact_root / "claim_6"
    claim_dir.mkdir(parents=True, exist_ok=True)
    raw_path = claim_dir / "raw_results.jsonl"
    records: list[dict] = []

    with raw_path.open("w") as raw_file:
        for seed in seeds:
            rng = np.random.default_rng(seed)
            train = [sample_route(rng) for _ in range(TRAIN_ROUTES)]
            test = [sample_route(rng) for _ in range(TEST_ROUTES)]
            if selection_mode == "paper_literal":
                construction, selection, evaluation = train, test, test
            elif selection_mode == "three_way":
                construction, selection, evaluation = train[:25], train[25:], test
            else:
                raise ValueError(f"unknown selection mode: {selection_mode}")
            chain = parametric_route_chain(construction)
            result_by_phi: dict[str, dict] = {}
            for phi in phi_values:
                lp, chain_size = lp_select(construction, selection, phi, chain)
                forward = forward_greedy(construction, selection, phi)
                reverse = reverse_greedy(construction, selection, phi)
                methods = {"lp": lp, "forward": forward, "reverse": reverse}
                result_by_phi[str(phi)] = {
                    method: {
                        "chosen": sorted(chosen),
                        "edges": len(chosen),
                        "selection_coverage": coverage(selection, chosen),
                        "evaluation_coverage": coverage(evaluation, chosen),
                        **({"parametric_sets": chain_size} if method == "lp" else {}),
                    }
                    for method, chosen in methods.items()
                }
            record = {
                "seed": seed,
                "selection_mode": selection_mode,
                "construction_routes": [list(route) for route in construction],
                "selection_routes": [list(route) for route in selection],
                "evaluation_routes": [list(route) for route in evaluation],
                "construction_digest": _route_digest(construction),
                "selection_digest": _route_digest(selection),
                "evaluation_digest": _route_digest(evaluation),
                "results": result_by_phi,
            }
            _independent_check(record, phi_values)
            records.append(record)
            raw_file.write(json.dumps(record, separators=(",", ":")) + "\n")

    summary_by_phi: dict[str, dict] = {}
    for phi in phi_values:
        key = str(phi)
        lp_edges = [record["results"][key]["lp"]["edges"] for record in records]
        forward_edges = [
            record["results"][key]["forward"]["edges"] for record in records
        ]
        reverse_edges = [
            record["results"][key]["reverse"]["edges"] for record in records
        ]
        summary_by_phi[key] = {
            "lp_edges": _mean_interval(lp_edges),
            "forward_edges": _mean_interval(forward_edges),
            "reverse_edges": _mean_interval(reverse_edges),
            "forward_minus_lp": _mean_interval(
                [forward - lp for forward, lp in zip(forward_edges, lp_edges)]
            ),
            "reverse_minus_lp": _mean_interval(
                [reverse - lp for reverse, lp in zip(reverse_edges, lp_edges)]
            ),
            "lp_evaluation_coverage": _mean_interval(
                [
                    record["results"][key]["lp"]["evaluation_coverage"]
                    for record in records
                ]
            ),
            "lp_edge_range": [min(lp_edges), max(lp_edges)],
            "lp_52_edge_seeds": [
                record["seed"]
                for record, edge_count in zip(records, lp_edges)
                if edge_count == 52
            ],
        }

    comparison_phis = [phi for phi in (0.2, 0.4, 0.6, 0.8) if phi in phi_values]
    strict_superiority = all(
        summary_by_phi[str(phi)]["forward_minus_lp"]["ci95_low"] > 0
        and summary_by_phi[str(phi)]["reverse_minus_lp"]["ci95_low"] > 0
        for phi in comparison_phis
    )
    edge_52_seeds = summary_by_phi[str(0.75)]["lp_52_edge_seeds"]
    paper_curve_rmse: dict[str, float] = {}
    for method in ("lp", "forward", "reverse"):
        observed = [
            summary_by_phi[str(phi)][f"{method}_edges"]["mean"]
            for phi in PAPER_FIGURE_MEANS["phi"]
        ]
        reference = PAPER_FIGURE_MEANS[method]
        paper_curve_rmse[method] = float(
            np.sqrt(np.mean((np.asarray(observed) - np.asarray(reference)) ** 2))
        )

    elapsed_wall = time.perf_counter() - started_wall
    elapsed_cpu = time.process_time() - started_cpu
    summary = {
        "status": (
            "VERIFIED"
            if strict_superiority and edge_52_seeds and selection_mode == "paper_literal"
            else "BLOCKED"
        ),
        "selection_mode": selection_mode,
        "seeds": seeds,
        "grid": "undirected 6x6",
        "grid_edges": GRID_EDGE_COUNT,
        "bypass_edges": BYPASS_EDGE_COUNT,
        "train_routes": TRAIN_ROUTES,
        "test_routes": TEST_ROUTES,
        "phi_values": phi_values,
        "summary_by_phi": summary_by_phi,
        "strict_superiority_phi_le_0_8": strict_superiority,
        "lp_52_edge_seeds_at_phi_0_75": edge_52_seeds,
        "digitized_paper_curve_rmse_edges": paper_curve_rmse,
        "runtime": {
            "wall_seconds": elapsed_wall,
            "cpu_seconds": elapsed_cpu,
            "logical_cpus": os.cpu_count(),
            "platform": platform.platform(),
            "python": platform.python_version(),
        },
    }
    (claim_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    contract = {
        "claim_id": 6,
        "paper_statement": (
            "On the 6x6 synthetic routing experiment with 50 train and 50 "
            "held-out routes, the LP solution uses 52 edges at phi=0.75 and "
            "is significantly more compressed than forward and reverse greedy "
            "for all plotted phi <= 0.8."
        ),
        "assumptions": [
            "undirected 6x6 grid with 60 road edges",
            "15% traffic uses a distinct 20-edge bypass",
            "85% uses a shortest path under i.i.d. Uniform[0.1,2] road weights",
            "50 training and 50 held-out routes from the same mixture",
            "fixed deterministic tie order because the source omits one",
        ],
        "verification_rule": {
            "52_edge_result": "at least one declared seed yields exactly 52 LP edges at phi=0.75",
            "greedy_result": (
                "paired 95% t intervals for forward-minus-LP and "
                "reverse-minus-LP edge counts are strictly above zero at "
                "phi in {0.2,0.4,0.6,0.8}"
            ),
            "integrity": "independent route/set checker passes every seed and phi",
        },
    }
    (claim_dir / "claim_contract.json").write_text(
        json.dumps(contract, indent=2) + "\n"
    )
    _write_text(
        claim_dir / "source_audit.md",
        """# Claim 6 source audit

Primary current source: ar5iv HTML for arXiv:2602.07530, retrieved
2026-07-23 with an explicit browser User-Agent, SHA-256
`c2f69b82d308ef5a75b5e4eba386a645ba45093a37a287d1cef31e775693d288`.

Anchors: Section 5.1, Figure 1(b,c), paragraphs “Greedy Baselines” and
“Synthetic Routing Experiment”. The text specifies a 6x6 grid, opposite-corner
routing, Uniform[0.1,2] random edge weights, 85% grid traffic, a 20-edge bypass
used by 15%, and 50 train plus 50 held-out routes. It reports a 52-edge LP
selection at phi=0.75 and says LP is significantly more compressed than both
greedy methods for every plotted phi <= 0.8. No code, seeds, graph orientation,
RNG, shortest-path tie rule, or greedy tie order is supplied.
""",
    )
    _write_text(
        claim_dir / "method.md",
        f"""# Method

This run uses committed selection mode `{selection_mode}`. It regenerates all
routes from seeds 0–{seeds[-1]}, builds the complete supported parametric
minimum-cut chain once per seed, applies the paper's fixed-order final deletion,
and implements the two greedy definitions from Section 5.1. Every reported set
is recomputed by an independent checker directly from raw routes.

The paper-figure points are digitized only as a forensic curve reference. They
are never used as raw observations or as inputs to the verifier.
""",
    )
    independent = {
        "status": "PASS",
        "records_checked": len(records),
        "phi_values_checked": phi_values,
        "checks_per_method": [
            "edge ids valid and unique",
            "route SHA-256 digests reproduce",
            "chosen cardinality reproduces",
            "selection and evaluation coverage reproduce",
            "selection coverage reaches target phi",
        ],
    }
    (claim_dir / "independent_checker.json").write_text(
        json.dumps(independent, indent=2) + "\n"
    )
    corrupted = json.loads(json.dumps(records[0]))
    corrupted["construction_routes"][0][0] = TOTAL_EDGE_COUNT + 1
    negative_failed = False
    negative_message = ""
    try:
        _independent_check(corrupted, phi_values)
    except AssertionError as error:
        negative_failed = True
        negative_message = type(error).__name__
    assert negative_failed
    negative = {
        "status": "PASS",
        "mutation": "replace one valid edge id with 81",
        "checker_rejected": negative_failed,
        "exception": negative_message,
    }
    (claim_dir / "negative_control.json").write_text(
        json.dumps(negative, indent=2) + "\n"
    )
    environment = {
        "command": (
            "uv run --frozen python repro/src/run_claims.py --out "
            "outputs/claims.json && uv run --frozen python -m pytest "
            "repro/tests -q && uv run --frozen python repro/src/verify_gate.py"
        ),
        "lockfile": "uv.lock",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "logical_cpus": os.cpu_count(),
        "seeds": seeds,
    }
    (claim_dir / "environment.json").write_text(
        json.dumps(environment, indent=2) + "\n"
    )
    _write_text(
        claim_dir / "limitations.md",
        """# Limitations and deviations

The paper does not release executable code, seeds, graph directionality, RNG,
or tie-breaking. This run uses the standard undirected interpretation of a
6x6 road grid and an ascending edge-id tie order. In paper-literal mode the
held-out routes select the displayed subgraph exactly as Section 5 describes,
so those same routes are not an additional independent generalization set.
The 95% intervals quantify seed variability of this declared implementation;
they do not reconstruct the authors' missing randomness.
""",
    )
    eval_lines = [
        "# Claim 6 evaluation",
        "",
        f"Verdict: **{summary['status']}**",
        "",
        f"- Selection mode: `{selection_mode}`",
        f"- Seeds: {len(seeds)}",
        f"- 52-edge seeds at phi=0.75: {edge_52_seeds}",
        f"- LP strictly beats both greedy baselines through phi=0.8: {strict_superiority}",
        f"- Wall time: {elapsed_wall:.3f} s; CPU time: {elapsed_cpu:.3f} s",
        "",
        "This verdict is evidence-local and is not a live judge result.",
    ]
    _write_text(claim_dir / "EVAL.md", "\n".join(eval_lines))
    return summary
