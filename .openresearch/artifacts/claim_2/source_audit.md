# Claim 2 source audit

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
