# Who Can Move the Money?

**Delegated Deposit Control and Bank Liquidity**  
Shivam Gupta · Independent Researcher · 23 September 2026

[Read the paper](output/pdf/Gupta_Delegated_Deposit_Control.pdf)

This repository accompanies a theory paper on the difference between ownership of bank deposits and authority to withdraw them. A cap on the largest jointly controlled balance, combined with a specified class of withdrawal dependence, yields a sharp funding-risk frontier. The analysis also shows why greater concentration can raise funding costs while increasing the bank's chosen lending.

The mathematics uses established majorization, moment optimization, and expected-shortfall tools. The contribution is their joint application to an explicit disclosure and valuation problem in delegated deposit funding. The literature review identifies close antecedents, including prior work on AI deposit brokers and Bernoulli dependence bounds.

## Evidence included

- Proofs of the control-cap frontier, its common-state limit, and the bank's valuation results.
- 270 fixed-cash scenarios, 90 cash-choice scenarios, 3,618 curve evaluations, and a recorded numerical refinement.
- Six million executed simulation draws, exact binomial controls, and 36 exact rational certificates across two numerical resolutions.
- Archived FDIC financial data and insurance flags for year-end 2022, 2024, and 2025. The main sample contains 4,336 insured U.S. banks and savings institutions.
- Six vector figures, six tables, manuscript source, tests, input hashes, and a reproducibility audit.

The FDIC exercise is a **hypothetical balance-sheet scenario analysis**. The data do not measure AI adoption, controller identity, withdrawal propensity, or causal effects. Dependence assumptions materially affect the bounds; the paper includes a broader finite-exchangeable comparator. These calculations are not estimates of bank failure probabilities or regulatory liquidity ratios.

## Reproduce offline

Python 3.12 was used. From the repository root:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python scripts/replicate.py
```

This uses archived inputs and makes no API requests. It runs the tests, computations, exact-certificate checks, bank sample construction, and figure/table generation. The scenario file is compressed as `results/bank_scenarios.csv.gz`.

Compile the paper with [Tectonic](https://tectonic-typesetting.github.io/):

```bash
.venv/bin/python scripts/build_paper.py --tectonic tectonic
```

The build rejects unresolved references and overfull boxes. Visual layout still requires inspection. Final output is `output/pdf/Gupta_Delegated_Deposit_Control.pdf`.

## Try a calculation

```bash
.venv/bin/python scripts/demo.py --cap 0.05 --cash 0.30 \
  --mean 0.10 --correlation 0.05 --cost-ratio 0.20
```

Inputs are scenario assumptions. All amounts are normalized by the potentially delegated pool. A cap is a maximum share controlled by a common economic trigger, not a model vendor's market share. The demonstrated range is 2%–100%; the common-state formula and error bound are useful for finer granularity.

The optional `--authority-json path.json` accepts a list of records with `trigger_id` and `authorized_balance`. Repeated trigger IDs are combined before computing concentration; splitting an account cannot create fictitious diversification. This mode computes an envelope based on the resulting cap, not a fitted withdrawal model.

## Data and provenance

The source is the [FDIC BankFind Suite API](https://api.fdic.gov/banks/docs). Raw responses, retrieval URLs, source index metadata, SHA-256 hashes, and field definitions are in `data/raw/`. `scripts/download_data.py` is the separate online acquisition step. Existing files with metadata are retained; use a new archive location if deliberately collecting a new vintage. Monetary fields are in thousands of U.S. dollars.

Insurance flags and bank class exclude noninsured institutions and insured foreign branches. Invalid domestic-deposit records are then excluded. `results/sample_flow.csv` records the complete sample construction. Controller shares and common-state moments are not inferred from insured/uninsured deposit fields.

## Organization

| Directory | Contents |
|---|---|
| `src/delegated_deposits/` | Exposure aggregation, exact conditional coefficients, moment programs, cash optimization, rational verification |
| `scripts/` | Acquisition, experiments, figures, tables, replication, PDF build, and demonstration |
| `tests/` | Mathematical and authority-aggregation checks |
| `data/raw/` | Unmodified source responses and provenance |
| `data/processed/` | Reconstructed bank samples |
| `results/` | All numerical outputs and certificates |
| `paper/`, `figures/` | LaTeX manuscript, bibliography, generated tables and figures |
| `notes/` | Protocol, amendments, literature review, and internal technical audit |

This is a research implementation, evaluated over the reported cases. It does not establish hidden controller relationships or validate the input assumptions for a real bank. Conference submission and acceptance are separate from publication of this repository.

Code in `src/`, `scripts/`, and `tests/` is MIT-licensed. The manuscript and original figures are copyright Shivam Gupta. FDIC inputs are attributed to their source. See `CITATION.cff` for citation metadata.
