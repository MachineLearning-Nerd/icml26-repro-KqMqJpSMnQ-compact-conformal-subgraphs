# Claims 1–5 — theorem-level evidence

Claims 1, 3, 4, and 5 are universal mathematical statements. The release does
not infer them from scaling plots: each uses an exact proof or reduction
certificate, and larger executions only stress the implementation.

Claim 2 is different. The source algorithm says to solve an LP at each target
but gives no canonical optimum rule. On two equal singleton hyperedges, exact
optimal solutions round to `{0}` at τ=1/5 and `{1}` at τ=1/2 for the same
κ=1/5. This falsifies literal algorithmic nestedness. It does not contradict
the nested maximal-source-side parametric family; specifying that family
repairs the claim.

- [Claim 1 evidence](../../../evidence/claim_1/EVAL.md)
- [Claim 2 exact counterexample](../../../evidence/claim_2/counterexample.json)
- [Claim 3 complexity certificate](../../../evidence/claim_3/proof_certificate.json)
- [Claim 4 exact rank checks](../../../evidence/claim_4/exact_rank_checks.json)
- [Claim 5 reduction certificate](../../../evidence/claim_5/proof_certificate.json)
