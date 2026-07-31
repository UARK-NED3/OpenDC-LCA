# Author response to the major-review assessment

We thank the reviewer for identifying methodological issues that could not be
resolved by reframing. We consequently rebuilt the electricity analysis,
added joint and functional-unit sensitivity, reorganized the manuscript around
evidence validity, expanded the literature review, reduced the main-figure
set, and moved software demonstrations and peripheral datasets to
Supplementary Information.

The revised manuscript does **not** claim that all submission requirements are
complete. Primary architecture-resolved measurements, bills of quantities,
empirical uncertainty/correlation, an external critical review, and a
DOI-bearing immutable archive remain necessary before a decision-grade
comparative assertion.

## Major comments

### 1. Figure 1 was stale, coarse, and too wordy

**Response:** Fully revised. Figure 1 was redesigned as a three-stage
evidence-to-decision schematic with a single calculation spine and four
evidence classes. The stale 61 kg CO2e/MWh value was removed; the current
figure reports the corrected 96.7 kg CO2e/MWh crossover, 29.8% anchor
extrapolation, and the 99%-to-56% stress-frequency range. Text was shortened
and enlarged for manuscript-scale rendering.

### 2. Equation 7 mixed GaBi lifecycle anchors with direct eGRID rates

**Response:** Addressed through a methodological change, not a wording change.
The equations now define a numerical intensity-position index rather than
presenting eGRID as a replacement lifecycle electricity process. The
manuscript explicitly states that the Microsoft anchors are GaBi lifecycle
GTP100 results whereas eGRID supplies direct generation GWP100 rates. The
transformation is classified as screening. A separate 0-100 kg CO2e/MWh
boundary-allowance stress tests whether rankings depend on this mismatch.

The result is consequential: Vermont is the only 2023 state below the
cold-plate/single-phase crossover at the unadjusted rate, but that reversal
disappears at a 75 kg CO2e/MWh allowance. Two-phase remains first in 51/51
states across the tested boundary allowances.

### 3. A material fraction of eGRID rows is outside the released anchors

**Response:** Fully quantified. New
`table21_anchor_extrapolation_diagnostic.csv` reports that 322 of 459
state-years are within the anchors, one is below the renewable anchor, and 136
are above the grid anchor. Thus 137/459 (29.85%) are extrapolations. In 2023,
9/51 (17.65%) are above the grid anchor. Methods, results, discussion, caption,
and conclusion now preserve this distinction.

### 4. Historical eGRID CO2e used changing GWP bases

**Response:** Fully rebuilt. State and U.S. rates are now reconstructed from
net generation and gas-specific CO2, CH4, and N2O emissions under one AR5
GWP100 basis (CH4=28; N2O=265). The provider CO2e rate and original GWP basis
are retained for comparison. The maximum national difference between the
provider and harmonized series is 0.248 kg CO2e/MWh, in 2012. The harmonized
U.S. factor declines from 517.731 in 2012 to 349.667 in 2023 (32.462%).

This demonstrates that the national trend is robust to the GWP update while
leaving the larger lifecycle-boundary mismatch visible.

### 5. Deterministic break-even analysis was not joint uncertainty

**Response:** Substantively expanded. A seeded 20,000-iteration joint
assumption-stress ensemble now perturbs shared grid rate and
technology-specific use phase, embodied contribution, and service-equivalence
terms. Narrow, screening, and wide triangular envelopes are declared in the
methods. They are not fitted distributions, so the manuscript calls the
outputs stress frequencies rather than probabilities or confidence.

For 2023 U.S. generation, two-phase first-rank frequency is 99.33%, 75.97%,
and 56.16% across the three envelopes. At the lowest-carbon state it is
63.19%, 42.55%, and 33.90%. These results replace the previous implication
that deterministic first rank across 459 grid factors established broad
robustness.

### 6. Functional-unit equivalence was asserted but not stress-tested

**Response:** New Eq. (11) calculates the adverse correction to two-phase
impact per equivalent useful computation required to equal the runner-up. The
median threshold is 5.503% across 2023 states, with a 5.236-6.042% range.
This result is now central to the discussion and defines an empirical
measurement target for throughput, server count, throttling, reliability, and
lifetime. It is not described as a measured penalty.

### 7. Integration of downloaded datasets was shallow or unclear

**Response:** The revised Table 1 assigns a numerical role and explicit
exclusion reason to every downloaded source class:

- Microsoft/WSP: arithmetic reconstruction and fixed foreground;
- eGRID: harmonized generation-rate scenarios;
- Boavizta: empirical server-manufacturing scale stress;
- ÖKOBAUDAT: matched per-unit material procurement levers;
- NOAA TMY: performance-map software test only;
- USLCI/GLAD: registered and exchange-tested, not numerically linked;
- USGS: geometry/data-contract test, not water consumption or scarcity.

The main paper now uses only evidence that changes the scientific argument.
Hourly synthetic cases, server distributions, material-lever figures,
reliability, and interoperability details were moved to Supplementary
Information.

### 8. The analysis lacked an empirical case suitable for Applied Energy

**Response:** This limitation cannot be solved honestly from the downloaded
files. We did not fabricate laboratory or facility measurements. Instead, the
revision quantifies the empirical resolution required: approximately 5-6% in
impact per equivalent useful computation for the deterministic two-phase
margin, plus architecture-resolved power, water, bills of quantities,
reliability, and correlations.

The paper is now positioned as a boundary-aware secondary analysis and
open-method contribution. Before submission as a decision-grade comparative
study, primary performance surfaces and functional-computation data should be
added. The limitation is stated in the abstract, discussion, conclusion, and
response record.

### 9. The contribution-weighted pedigree index was heuristic

**Response:** A rank-robustness analysis now evaluates
`contribution^a × weakness^b` for all nine combinations of
`a,b ∈ {0.5,1,2}`. Use phase ranks first in eight specifications and in the top
three in eight; networking ranks first once; storage remains top-three in all
nine; compute is top-three in four. The paper no longer presents the base
index as a unique acquisition order or formal value of information. It
identifies the additional decision losses, measurement costs, empirical
distributions, and posterior updating needed for VoI.

### 10. A coauthor cannot supply independent critical review

**Response:** Corrected throughout. Dr. Nutter is described as the LCA
coauthor/methodologist, not an independent reviewer. The limitations and
pre-submission checklist require an external critical reviewer for a public
comparative assertion.

### 11. The literature review was incomplete

**Response:** Substantially expanded and reorganized. The revision now covers:

- data-center cooling experiments and recent technology reviews;
- data-center LCA, water, and cooling-device studies;
- lifecycle versus location-, market-, average-, and marginal-electricity
  accounting;
- dynamic and time-explicit LCA, including Temporalis and bw_timex;
- uncertainty/variability, pedigree data quality, and value of information;
- the domain gap between openLCA/Brightway calculation and cooling-specific
  functional-equivalence and evidence governance.

Reference 25 (formerly 23) was corrected to Asli Isler-Kaya and Filiz
Karaosmanoglu, *Energy and Buildings* 288, 113006 (2023).

### 12. The repository lacked an immutable archival record

**Response:** Partly addressed. The data/code statement no longer implies that
a GitHub tag is equivalent to a submission archive. It states that a
DOI-bearing immutable archive of the accepted commit, derived tables, figures,
configuration, and reproducibility manifest will be minted before submission.
The repository now contains an archival-release checklist. Minting the DOI is
an external release action and has not been falsely claimed as complete.

## Additional revisions

- The title now foregrounds boundary-aware evidence synthesis rather than
  claiming a universal technology comparison.
- The abstract distinguishes robust national decarbonization from conditional
  local rankings and labels stress frequencies correctly.
- Main figures were reduced to five scientific figures; synthetic/weather,
  server, material, and detailed crossover panels moved to the supplement.
- The conclusion now reports anchor coverage, boundary sensitivity, joint
  stress, and functional-unit thresholds instead of only deterministic rank.
- All generated CSV files use stable LF line endings.
- Four regression tests were added for common-basis eGRID values,
  extrapolation counts, boundary sensitivity, and functional-unit sensitivity.
  The complete suite now contains 46 passing tests.

## Evidence still required before submission

1. Primary, architecture-resolved useful-computation and cooling-performance
   surfaces over a common load-weather domain.
2. Server, network, storage, cooling, support-equipment, building, fluid, and
   replacement bills of quantities with service life and uncertainty.
3. Consumption-based lifecycle electricity processes under the same LCIA
   method as the foreground, with clearly separated location-, market-, and
   marginal signals.
4. Hourly water and watershed scarcity characterization where water claims are
   made.
5. Empirical uncertainty distributions and correlations sufficient for rank
   probability and value-of-information analysis.
6. External LCA critical review and confirmation of authorship, contributions,
   funding, competing interests, and acknowledgments.
7. A DOI-bearing immutable code/data archive for the exact submitted commit.
