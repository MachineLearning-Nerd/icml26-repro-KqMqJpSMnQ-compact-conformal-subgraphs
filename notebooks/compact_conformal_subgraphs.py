import marimo

__generated_with = "0.23.14"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np

    return mo, np, plt


@app.cell
def _(mo, np, plt):
    phi = np.array([0.2, 0.4, 0.6, 0.75, 0.8, 0.9, 1.0])
    observed = {
        "LP": np.array([29.28, 38.47, 45.00, 57.38, 63.40, 74.025, 78.855]),
        "Forward greedy": np.array([44.22, 55.775, 63.205, 68.435, 69.715, 73.80, 78.775]),
        "Reverse greedy": np.array([39.35, 53.90, 61.34, 67.24, 68.70, 73.365, 78.875]),
    }
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for label, values in observed.items():
        ax.plot(phi, values, marker="o", label=label)
    ax.axvline(0.8, color="gray", linestyle=":")
    ax.set(
        xlabel="Target coverage φ",
        ylabel="Selected edges (lower is better)",
        title="Observed 200-seed compression curves",
    )
    ax.grid(alpha=0.2)
    ax.legend()
    mo.vstack(
        [
            mo.md(
                """
                # Compact Conformal Subgraphs — CPU reproduction

                The central experimental effect appears immediately below:
                the LP method selects fewer edges than both greedy baselines
                throughout the paper's claimed range, φ≤0.8.
                """
            ),
            fig,
            mo.md(
                "**Headline:** at φ=.75, 20 of 200 declared seeds select exactly "
                "52 LP edges; the seed-mean is 57.38 edges."
            ),
        ]
    )
    return observed, phi


@app.cell
def _(mo):
    mo.md(r"""
    ## What is being compressed?

    A route is a hyperedge: it is covered only when every road edge on the route is
    retained. The LP constructs a nested family of candidate subgraphs, conformal
    calibration chooses a coverage level, and a final deletion pass removes
    redundant edges. The experiment uses a 6×6 undirected grid (60 road edges), a
    separate 20-edge bypass, 50 construction routes, and 50 held-out selection
    routes.
    """)
    return


@app.cell
def _(mo):
    selected_phi = mo.ui.dropdown(
        options=["0.2", "0.4", "0.6", "0.75", "0.8", "0.9", "1.0"],
        value="0.75",
        label="Inspect target coverage",
    )
    selected_phi
    return (selected_phi,)


@app.cell
def _(mo, observed, phi, selected_phi):
    index = [str(value) for value in phi].index(selected_phi.value)
    lp = observed["LP"][index]
    forward = observed["Forward greedy"][index]
    reverse = observed["Reverse greedy"][index]
    mo.md(
        f"""
        At **φ={selected_phi.value}**, LP uses **{lp:.2f}** edges on average,
        versus **{forward:.2f}** for forward greedy and **{reverse:.2f}** for
        reverse greedy. The paired differences—not overlap of marginal
        intervals—are the formal comparison.
        """
    )
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Claim-by-claim evidence

    | Claim | Evidence-local verdict | Decisive route |
    | --- | --- | --- |
    | LP bicriteria rounding | VERIFIED | exact inequality certificate + sparse LP stress tests |
    | LP-output nestedness | FALSIFIED as written | exact optimal-tie counterexample; canonical parametric chain remains nested |
    | Parametric complexity | VERIFIED | primary theorem + exact network-size substitution |
    | Marginal coverage | VERIFIED | finite-sample rank certificate + 20,000 exchangeable trials |
    | Constant-ε NP-hardness | VERIFIED | ε=1/2 reduction certificate + two clique solvers |
    | 52 edges and greedy advantage | VERIFIED | 200 seeds + paired 95% intervals |

    These are reproduction verdicts, not a new live-judge result. The authors did
    not release executable code, seeds, grid orientation, RNG, or tie rules, so the
    notebook keeps all substitutions visible.
    """)
    return


@app.cell
def _(mo):
    mo.md(r"""
    ## Reproduce the formal evidence

    The notebook embeds the small headline table so it opens instantly. Formal
    evidence is regenerated from the repository root with:

    ```bash
    uv run --frozen python repro/src/run_claims.py --out outputs/claims.json \
      && uv run --frozen python -m pytest repro/tests -q \
      && uv run --frozen python repro/src/verify_gate.py
    ```

    This fixed command uses local CPU, Python 3.12, a pinned `uv.lock`, and one
    repository `.venv`.
    """)
    return


if __name__ == "__main__":
    app.run()
