# Numerical refinement and storage

23 September 2026. Degree-512 results showed visible upper-lower gaps. Refine all 18 central cases (mu=0.1, cash=0.3, rho=0.01/0.05/0.2, all six caps) to degrees 1,024, 2,048, and 4,096 with 4,001 moment-grid nodes. Refine all 18 corresponding bank-choice cases at cost ratio 0.2. Keep the original parameter sweep and the complete convergence history; do not select cases by which comparative static looks favorable. Exact rational certificates accompany the degree-4,096 fixed-cash results.

The bankwise scenario output is gzip-compressed to avoid a redundant 20+ MB generated CSV. Compression uses a fixed timestamp. Other scripts read the smaller scenario summary rather than duplicating the bankwise file.
