# Internal technical and reproducibility audit

Completed 23 September 2026. This is an internal audit, not external peer review.

## Executed verification

- A fresh copy of the source and archived inputs executed `scripts/replicate.py` using the recorded Python 3.12 environment, without invoking the acquisition script.
- All 47 tests passed with warnings treated as errors. Checks include enumeration versus conditional-count aggregation, majorization comparisons, moment feasibility, common-state bounds, boundary cases, optimal cash, and authority-record aggregation.
- The complete numerical pipeline reran: 270 fixed-cash cases, 90 cash-choice cases, 3,618 curve evaluations, six million seeded simulation draws, and the separately recorded refinement.
- All 30 compared result, processed-data, table-source, and PNG files reproduced byte for byte. Elapsed runtime metadata and PDF creation metadata were excluded. The exact paths and comparison results are in `reproduction-check.json`.
- All seven archived input hashes and 36 rational certificates passed. The certificate verifier uses rational arithmetic for the selected fixed-cash cases; the broad parameter sweep and bank-choice calculations use floating-point feasibility checks and reported numerical gaps.
- The source compiles to 22 pages, six figures, six tables, and 20 bibliographic entries. The final compiler log contains no unresolved references or overfull boxes. All final pages were rendered and visually inspected; equation labels, table columns, plot legends, references, and appendix flow were checked.
- PDF SHA-256: `bf213c639f45a03c8c000a8ede95b5c960654eb9e327361bf1c3890709076c5e`.

## Scientific scope and outstanding limitations

The study proves a sharp control-cap bound within a conditional-mixture model and evaluates its economic implications. It does not establish the original idea of AI deposit brokers; that is prior work and is cited prominently. Majorization, moment duality, stop-loss bounds, and expected-shortfall representations are attributed to their antecedents.

Controller size, delegation share, common withdrawal moments, and the cost ratio are assumptions in the quantitative exercises. The FDIC data establish observed bank balance-sheet scale only. There is no observed controller-level withdrawal panel, causal adoption estimate, run equilibrium, or validation of the scenario inputs against real withdrawal behavior. The finite-exchangeable sensitivity materially widens some bounds. These facts limit both empirical interpretation and conference competitiveness.

The practical code aggregates balances governed by a common trigger and computes a conditional risk envelope. It is a research implementation, not an operationally validated bank risk system. Novelty searches cannot establish universal novelty or patentability. No acceptance probability is asserted.

## Release and submission

The public release contains source, data provenance, computed outputs, and the manuscript. Account credentials and private resumes are excluded. Conference submission remains a separate operation; see `submission/status.md` for its actual status. No arXiv submission was performed.
