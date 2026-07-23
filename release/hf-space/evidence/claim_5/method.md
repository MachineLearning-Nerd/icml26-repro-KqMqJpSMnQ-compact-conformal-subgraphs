# Method

Check P1-P3 and the polynomial parameter construction exactly at fixed
epsilon=1/2. Generate 25 source graphs from n=20 through n=60, solve maximum
clique independently with NetworkX maximal-clique enumeration and a custom
bitset branch-and-bound solver, and certify both YES and NO reduction queries.
The proof certificate supplies the universal reduction logic; scale cases
exercise its implementation.
