# Research protocol: withdrawal-control disclosure

Created 23 September 2026 before numerical experiments. This is a local protocol, not external preregistration. A two-record FDIC connectivity/schema probe preceded this file.

## Question and contribution to assess
Can disclosure of the largest jointly controlled deposit balance produce informative bounds on a bank's liquidity cost when the distribution of common withdrawal incentives is unknown? Which information can account ownership, individual withdrawal probabilities, and pairwise correlation fail to supply?

This is a theory paper with computational verification and a public-balance-sheet illustration. It does not estimate AI adoption, causal effects, real withdrawal probabilities, or bank failure probabilities. No language model is used to invent depositor behavior or manufacture economic evidence.

## Model
Normalize potentially delegated balances to one. Nonnegative controller shares sum to one and are capped at h. Given P in [0,1], controllers independently withdraw with probability P. The distribution of P has mean mu and second moment nu=mu^2+rho*mu*(1-mu). A controller is an economic common trigger, not necessarily a software vendor. Bank cash l incurs opportunity cost r*l, and uncovered withdrawals incur c*(W-l)+. The reference cost ratio r/c is 0.2. Quantities are horizon-specific, dimensionless theoretical inputs.

Prove cap-extremal exposure using majorization, the associated univariate moment problem, a constructive Bernstein dual upper bound, feasible primal lower bounds, the common-state floor, and the difference between funding cost and chosen lending. Attribute standard mathematics explicitly.

## Planned numerical work
1. Compare enumeration, direct binomial probabilities, conditional-count coefficients, and Monte Carlo on constructed control structures.
2. Evaluate h in {1,0.5,0.2,0.1,0.05,0.02}, mu in {0.05,0.1,0.2}, rho in {0,0.01,0.05,0.2,1}. Primary plots use mu=0.1, rho in {0,0.05,0.2}; all parameter sweeps are retained.
3. Compute worst expected uncovered withdrawals at cash fractions 0.1, 0.2, 0.3, and bank optimal liquidity at r/c in {0.05,0.2,0.5}. Report primal-dual numerical gaps, not just an optimizer's success flag.
4. Compare a beta common-state distribution to admissible extremal distributions with identical first two moments. The beta distribution is a sensitivity comparator, not an estimated law.
5. Test failure cases: arbitrary dependence without the conditional independence model, heterogeneous controller probabilities, and endogenous bank choice.

## Public-data illustration
Use all available bank-level FDIC financials at 2025-12-31, a completed calendar year selected before computing results; secondary dates 2022-12-31 and 2024-12-31. Save raw responses, API metadata, field definitions, retrieval timestamps, and SHA-256 hashes. Use domestic deposits and cash/balances due; separately examine Treasury securities. Exclude missing/nonpositive domestic deposits or assets, invalid negative buffers, and flag duplicate certificates. Do not select banks by stress outcome. Compute hypothetical delegated shares theta in {0.1,0.25,0.5}; none is an observed adoption rate. Scale incremental delegated withdrawals only, with no claims about total bank liquidity adequacy. No bank names in risk rankings.

## Reporting
All tables and figures must be generated from archived input and executable scripts. Distinguish theorem proofs, numerical checks, controlled simulations, and descriptive real data. Report unfavorable results and failed scientific claims. Do not guarantee novelty, patentability, acceptance, or commercial value. The submission destination is the BIS-CEPR-Gerzensee-SFI Conference on Financial Intermediation 2027 only; no arXiv submission.
