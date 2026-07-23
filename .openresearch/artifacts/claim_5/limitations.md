# Limitations

The executable parameter sweep uses the representative fixed constant
epsilon=1/2; the source's algebraic proof handles any fixed rational epsilon in
(0,1). The checker restricts to r>=3 and nonempty graphs, avoiding trivial
CLIQUE instances without weakening NP-hardness. It certifies the reduced
answer using P1-P3 rather than materializing exponentially hard reduced
instances.
