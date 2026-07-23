# Method

Use the smallest symmetric weighted hypergraph with two vertices and two
singleton hyperedges. Exact `Fraction` arithmetic checks feasibility,
optimality (by a matching algebraic lower bound), the paper's kappa domain, and
threshold rounding. A separate HiGHS solve lexicographically selects the same
two endpoints of the optimal faces. The negative control lowers required mass
and must be rejected.
