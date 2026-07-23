# Claim 6 — full navigation experiment

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
