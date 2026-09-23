# Literature and contribution audit

Search date: 23 September 2026. This is a scoped literature review, not a proof of universal novelty or a patent search.

## Research decisions

The initial idea, “AI deposit agents can accelerate bank runs,” was rejected as a novelty claim. Todd Phillips's *When Siri becomes a deposit broker* (2025) directly discusses that mechanism. Digital switching and deposit-franchise fragility are also established topics. The paper instead asks what a disclosure of withdrawal authority can identify about liquidity costs, and how controller granularity interacts with unknown common-state tails and a bank's chosen cash.

The mathematical tools are also established. The cap comparison specializes majorization; the common-state optimization specializes the moment problem; the limiting stop-loss formula belongs to robust inventory/actuarial analysis; the expected-shortfall and Bernstein representations are standard. The paper credits those antecedents and claims a specific economic formulation, its joint frontier, and its executable evaluation.

## Closest work and differences

| Work | Relation to the present study |
|---|---|
| [Phillips (2025), *When Siri becomes a deposit broker*](https://doi.org/10.1017/fas.2025.10018) | Closest substantive motivation: autonomous deposit brokers, coordinated transfers, and regulatory authority. The present paper supplies a conditional valuation model and sharp disclosure bounds, not the original warning. |
| [Koont, Santos, Zingales (2024), *Destabilizing Digital “Bank Walks”*](https://www.nber.org/system/files/working_papers/w32601/revisions/w32601.rev0.pdf) | Digital banking and deposit franchise stability. This paper does not identify technology adoption; it changes control dependence holding marginal incentives fixed. |
| [Brei et al. (2026), BIS WP 1357](https://www.bis.org/publ/work1357.htm) | Deposit pricing, digital banks, and social media. Our control map is different from a digital-bank or social-media exposure indicator. |
| [Drechsler et al. (2026), *Deposit Franchise Runs*](https://doi.org/10.1111/jofi.70034) | An equilibrium mechanism linking franchise value and run incentives. The present treasury model holds those incentives fixed and does not replace this run theory. |
| [Narayanan and Ratnadiwakara (2024)](https://doi.org/10.2139/ssrn.4839754) | Customer composition and deposit stability. The observation of authority adds a decision-rights object to ownership/customer data. |
| [Robinson (2024), Federal Reserve](https://www.cbcfrs.org/articles/2024/second-release-2024/a-deposit-deep-dive-liquidity-risk-management-for-uninsured-and-nontraditional-deposits) | Supervisors already recognize concentrated nontraditional funding, including some insured deposits. The manuscript makes no regulatory-blindness claim. |
| [Marshall, Olkin, Arnold (2011)](https://doi.org/10.1007/978-0-387-68276-1) | Symmetric convex functions are Schur-convex. This is the engine of the extremal-cap proof, not a new general inequality. |
| [Dhaene et al. (2002)](https://doi.org/10.1016/S0167-6687(02)00134-8) | Comonotonicity and risk aggregation. The unrestricted-dependence endpoint is classical. |
| Scarf (1958), *A Min-Max Solution of an Inventory Problem* | Distributionally robust shortage costs. The bounded-support common-state floor is a specialization of a classical problem. |
| [Bertsimas and Popescu (2005)](https://doi.org/10.1137/S1052623401399903) | Moment optimization, polynomial duals, and sharp bounds. The present paper reduces unknown control exposures to a particular small moment problem. |
| [Rockafellar and Uryasev (2002)](https://doi.org/10.1016/S0378-4266(02)00271-6) | The cost/expected-shortfall identity, including discrete distributions, is attributed directly. |
| [Fontana and Semeraro (2022)](https://doi.org/10.1007/s42519-021-00231-x), [2023](https://iris.polito.it/retrieve/2f194e60-a60a-4a7e-996f-357ed563e661/ExchBern_jspi_Rev2.pdf) | Bernoulli dependence classes and exchangeability. These are particularly close statistical antecedents; the finite-exchangeable LP is an application, not an independent new method. |
| [Ben Sassi and Sankaranarayanan (2015)](https://arxiv.org/abs/1509.01156) | Bernstein polynomial LP relaxations. We provide a specialized exact-rational certificate for the financial bound. |

## Search coverage

Queries covered AI deposit agents and bank runs; automated deposit switching and liquidity; delegated deposits and control concentration; deposit granularity and optimal cash; distributionally robust bank liquidity; moment problems and stop-loss premiums; Bernoulli weighted sums, majorization, and convex order; finite exchangeability versus conditional mixtures; binomial-mixture moment identification; Bernstein moment bounds; deposit franchise and digital bank walks. We inspected primary journal, author, central-bank, regulator, and working-paper sources. Other related work discovered included switching costs and financial stability, LLM depositor simulations, dynamic clustered bank runs, and tokenized deposits.

## What remains uncertain

No located source presents this exact joint disclosure-to-funding formulation, but the proximity to established actuarial mathematics limits the novelty claim. The most defensible contribution is financial measurement and its economic implications, rather than a new generic optimization method. The paper is a completed theory-and-computation study; its FDIC section is a descriptive scenario illustration. It lacks controller-level validation and a causal identification design. Those are material limitations for a very selective financial-intermediation program, and there is no defensible numerical acceptance probability.

## Lessons from the supplied earlier papers

Avoid a broad new label for an established mathematical observation; avoid model-generated economic behavior as a substitute for financial evidence; distinguish analytical results from constructed simulations; verify numerical bounds rather than quoting solver outputs; report the nearest antecedents and adverse sensitivity results. The current study applies these lessons by identifying an explicit financial decision, retaining dependence failures, and using archived regulatory data only for the quantities it actually measures.
