# Transferability audit of data-center cooling life-cycle assessment considering lifecycle electricity, functional equivalence, and rank robustness

**Braden Stevens (1, 5), Pengjiang Xiang (1, 5), Pawel Wolinski (2), Charles Dwyer (3), Yimin Chen (4), Darin Nutter (1), and Han Hu (1)**

(1) Department of Mechanical Engineering, University of Arkansas, Fayetteville, AR 72701, U.S.

(2) Arkansas High Performance Computing Center, University of Arkansas, Fayetteville, AR 72701, U.S.

(3) IT Services, University of Arkansas, Fayetteville, AR 72701, U.S.

(4) Building Technologies Research and Integration Center, Oak Ridge National Laboratory, Oak Ridge, TN 37830, U.S.

(5) Harrison French & Associates Ltd., Bentonville, AR 72712, U.S.

*The corresponding author is Han Hu (hanhu@uark.edu).*

## Abstract

Published data-center cooling life-cycle assessments (LCAs) are difficult to
transfer because electricity boundaries, climate methods, useful-computation
equivalence, and foreground inventories differ. This Technology Assessment
uses OpenDC-LCA, an open-source evidence-audit and comparison-validation tool,
to test which conclusions from the released Microsoft/WSP comparison remain
supportable. We reconstructed 24 totals, harmonized nine U.S. Environmental
Protection Agency Emissions & Generation Resource Integrated Database (eGRID)
releases to the Intergovernmental Panel on Climate Change Fifth Assessment
Report 100-year global warming potential (AR5 GWP100), and calculated 71
non-residual 2023 Federal LCA Commons electricity-consumption systems. The
article reports AR5 GWP100, but its archived workbook places the numeric
electricity endpoints in 100-year global temperature-change-potential (GTP100)
cells while the corresponding GWP100 cells are blank and the comparative
use-phase formulas reference those blank cells.
We therefore retain cooling totals only as numerical transferability screens.
The harmonized national direct-generation factor declined 32.46%, from 517.73
to 349.67 kg carbon dioxide equivalent per megawatt-hour between 2012 and 2023.
The partial linked national consumption system yielded 422.93 kg carbon
dioxide equivalent per megawatt-hour but retained 287 unlinked technosphere
inputs. Under equal relative bounds, the first-rank screen failed at a 1.32%
all-block half-width. Service-equivalence and use-phase thresholds were 2.64%
and 2.99%, compared with 22.15% for embodied burden. This result reverses an
earlier attribution of rank sensitivity to embodied variation. The audit
supports the decline in generation-related greenhouse-gas intensity and
identifies decision-critical data, but it does not identify a universally
preferable cooling architecture.

**Keywords**  data center, life-cycle assessment, energy efficiency, lifecycle electricity, functional equivalence, sensitivity analysis, open-source software

## 1. Introduction

### 1.1. Cooling-system lifecycle context

Data centers couple rapidly changing computing hardware to long-lived
buildings, electrical systems, cooling plants, and regional energy and water
systems. Global data-center electricity estimates remain uncertain, but the
scale and growth of cloud and artificial intelligence (AI) workloads make energy
efficiency and electricity-supply emissions simultaneous design constraints [1,2].
At the equipment level, increasing processor heat flux and rack density are
driving a transition from room air cooling toward rear-door heat exchangers,
direct-to-chip cold plates, and single- or two-phase immersion [3-5].

These cooling architectures alter more than the heat exchanger because they
also change server fans, pumps, coolant distribution units, heat-rejection
temperature, fluid inventory, rack or tank construction, packing density,
repair procedures, and sometimes achievable clock rate. System experiments
have reported materially
different coefficient of performance and cost behavior for single- and
two-phase immersion over load [6], while recent single-phase tests show that
flow direction, coolant viscosity, and water temperature affect chip
temperature, thermal resistance, and power usage effectiveness (PUE) [7]. Two-phase experiments similarly
show that boiling, pressure stability, and condenser performance must be
evaluated at server and system levels [8]. A comparison at equal rack count,
equal IT electricity, or equal nameplate capacity risks comparing different
computational services.

PUE remains useful for facility energy management, but it is not a lifecycle
functional unit and does not represent hardware production, cooling-fluid
loss, replacement, water scarcity, or useful computation. Cooling selection is
an energy-system decision with lifecycle consequences, not a
single-metric efficiency contest.

### 1.2. Data-center LCA literature

Early environmental assessments showed that operating electricity dominates
many data-center footprints and that PUE alone can transfer burdens outside
the measured facility boundary [9]. U.S. studies subsequently linked data
centers to spatially varying electricity and water burdens [10,11]. At the
product scale, Isler-Kaya and Karaosmanoglu collected manufacturing inventory
for a cooling device and evaluated electricity and waste scenarios [12].
Wenzel and Radgen compared energy, material-flow, exergy, and lifecycle
assessment methods for a wet cooling tower, illustrating that method choice
changes the question answered [13].

Alissa et al. published the most detailed public hyperscale comparison of
air, cold-plate, single-phase immersion, and two-phase immersion [14]. Their
cradle-to-grave model included buildings, support equipment, servers, racks or
tanks, cables, cooling fluids, use-phase electricity and water, replacement,
and end of life. The use of Vcore-year as the functional unit was a major
advance because it allowed packing density and cooling-enabled computation to
enter the comparison. The accompanying archive includes normalized
contributions, equations, uncertainty material, and a pedigree assessment [15].
It does not, however, disclose every licensed background process,
architecture-specific bill of quantities, or a transferable mapping from
electricity to workload performance.

Recent work has moved closer to architecture- and service-level assessment.
d'Orgeval et al. modeled complete data-center configurations and reported
performance-normalized results for GPU-based subsets [16]. Wu et al. released
and validated a cooling-plant virtual testbed against three months of operating
data, with 7.62% mean absolute percentage error for power [17]. These studies
provide performance and architecture evidence that a secondary normalized
table cannot supply. ITU-T L.1410 likewise treats the functional unit and the
rules for comparative ICT analysis as explicit study choices [18].

Other LCA work confirms that changes in electricity-generation emissions and cooling
efficiency are complementary but can shift impacts among categories [19].
Manufacturer and ICT studies also show wide dispersion in embodied server
impacts [20,21]. Together, the performance and manufacturer evidence leaves a
specific transferability gap because available primary studies do not provide
a reusable audit for determining whether a published cooling comparison can be
moved to a different electricity system without changing its method, boundary,
or computational service.

### 1.3. Temporal and geographic electricity accounting

Electricity is not a scalar independent of method. Attributional LCA usually
requires a consumption mix with upstream generation, transmission, and other
indirect processes, whereas eGRID state total-output rates describe direct
emissions from in-state generation. Location-based, market-based, and marginal
factors answer different questions. Combining location- and market-based
accounting inconsistently can double count renewable attributes [22,23].
Average rates can also fail to represent the effect of workload shifting.
Dandres et al. found that average and marginal electricity signals can lead to
different real-time data-center decisions [24].

Time affects i) cooling performance across load and weather, ii) hourly and
long-term grid composition, iii) discrete equipment replacement, and iv)
background technology. Dynamic-LCA reviews
distinguish temporal inventory, characterization, and prospective background
change [25,26]. Open tools such as Temporalis and, more recently, bw_timex show
how temporal information can be propagated through process networks [27-29].
For cooling, hourly operation is necessary but insufficient. The grid method,
geography, and upstream boundary must also be aligned. A weather file cannot
repair an incompatible electricity inventory.

### 1.4. Data quality, uncertainty, and decision value

LCA uncertainty arises from parameters, scenarios, model form, allocation,
system boundary, and incomplete knowledge. Monte Carlo propagation is useful
when distributions and correlations are supportable. It becomes misleading
when arbitrary ranges are presented as confidence. Correlation can materially
change propagated uncertainty and cannot be inferred from marginal ranges
alone [30]. Reviews recommend separating variability from uncertainty and
using sensitivity analysis to identify influential assumptions [31]. Pedigree matrices can communicate
reliability, temporal, geographic, and technological representativeness, but
the conversion from qualitative scores to uncertainty is itself a modeling
choice [32,33].

EPA guidance treats reproducible documentation at flow and process levels as
part of data-quality assessment [33]. Value-of-information methods extend this
assessment by prioritizing data whose resolution is expected to change a
decision rather than simply improving every weak input [34]. For
electronics-cooling laboratories, this distinction separates a poor-pedigree
parameter with negligible decision leverage from a small PUE difference that
may decide between nearly tied lifecycle alternatives.

ISO 14040 and ISO 14044 define the LCA framework and requirements, whereas ISO
14071 (2024) specifies the critical-review process and reviewer competencies
needed for stronger claims, with particular relevance to comparative
assertions intended for public disclosure [35,36]. Code tests, data checks, and
coauthor review can strengthen traceability, but none is a substitute for an
independent critical review.

### 1.5. Research gap and contributions

General engines such as openLCA and Brightway calculate process networks,
exchange inventories, and apply life-cycle impact assessment (LCIA) methods [37,38]. They do not determine
whether cooling alternatives deliver equivalent computation, whether a
performance map covers the operating domain, whether a grid substitution
preserves the original electricity boundary, or whether secondary screening
results support a public comparative assertion. Conversely, cooling-plant
models can validate operational power without closing lifecycle inventories
or comparative-review requirements [17].

Four gaps remain at the intersection of cooling engineering and LCA. First,
published normalized totals cannot be transparently updated when foreground
quantities and licensed process mappings are incomplete. Second, common-unit
electricity factors can retain incompatible characterization methods and
system boundaries. Third, qualitative data-quality scores do not directly
show which measurement could change the technology decision. Fourth, software
often produces a number without preserving whether it is reconstructed,
screened, empirically supported, or suitable for a comparative claim.

This technology assessment addresses the transferability of the released
Microsoft/WSP case through five linked contributions. First, it reconstructs
24 released totals and audits the workbook cells to identify an unresolved
GTP100/GWP100 inconsistency in the public archive. Second, it harmonizes nine
eGRID releases from gas-specific emissions. Third, it calculates 71
Federal LCA Commons 2023 consumption systems with an openLCA-compatible JSON-LD
workflow and reports process links, numerical
residuals, and unlinked technosphere cutoffs rather than hiding them.
Fourth, it derives exact, equal-width, deterministic rank-robustness
certificates that distinguish the effects of grid, use phase, embodied burden,
and service equivalence without assigning unsupported probabilities. Finally,
it provides the open-source OpenDC-LCA comparison validator, which blocks
incompatible functional units, boundaries, electricity accounting, LCIA
methods, or missing field-level lineage while stating that metadata checks are
not physical validation.

Together, the reconstruction addresses the missing public arithmetic in gap 1.
The harmonization and linked-system calculations expose the method and
boundary conflicts in gap 2. The rank-robustness certificates identify the
measurements with decision leverage in gap 3. The OpenDC-LCA validator
preserves the evidence class needed to prevent gap 4. OpenDC-LCA is therefore
the reproducible implementation of this assessment layer, not a replacement
for the process-network engines openLCA or Brightway.

The aim is not to reconstruct licensed background inventories or declare a
winning cooling technology. It is to determine which claims survive a
transferability audit and which require primary measurement, complete
inventories, or external critical review.

## 2. Framework and methods

### 2.1. Evidence-to-decision framework

Figure 1 traces released lifecycle results, public scenario data,
exchange-ready inventories, and primary engineering evidence through gates for
functional equivalence, method alignment, transformation limits, and evidence
classification. The workflow returns three decision products consisting of a
reproducibility result, a conditional comparison boundary, and a robustness
threshold paired with the next evidence requirement. The repository records
source-family metadata and a per-file path, byte count, and SHA-256 checksum.
Dataset-specific tables retain the worksheet, field, unit, boundary, and
numerical role used in each analysis. This is file-level integrity plus
family-level provenance, not a complete flow-level data-lineage graph. The
harmonization gates determine i) whether the alternatives are functionally
equivalent, ii) whether the units, characterization methods, time, and geography
are aligned, iii) whether the required transformation is interpolation or
extrapolation, and iv) whether uncertainty, correlation, and review status are
adequate for the proposed claim. The result is classified as reconstructed,
screening-transformed, registered/unlinked, or supported by primary
decision-grade evidence.

![Figure 1. OpenDC-LCA evidence-to-decision architecture. Inputs are assigned a numerical role before calculation. The harmonization spine makes functional equivalence, method alignment, extrapolation, uncertainty, and claim status explicit. Outputs combine the numerical result with its evidence class and next-data requirement. The diagram layout was developed with assistance from OpenAI Codex and was reviewed and edited by the authors.](figures/figure0_opendc_lca_workflow.svg)

OpenDC-LCA is implemented in Python 3.10 or later and distributed under the
MIT License [39]. The development branch evaluated here extends version 1.1.0
and provides a command-line interface, Python API,
local browser GUI, scenario and performance-map schemas, reliability and
replacement models, openLCA JSON-LD and Brightway mappings, evidence audits,
and human- and machine-readable reports. Its comparison validator checks
cross-scenario metadata and field-level source mappings before calculating a
comparison. It cannot verify whether a declared source, uncertainty model, or
review status is true. All interfaces call the same calculation engine.

### 2.2. Goal, functional units, and system boundaries

The practitioner package defaults to one MWh delivered to IT equipment
(`it_mwh`) for operational screening. That unit is valid for comparison only
when alternatives provide equivalent computational output, utilization,
quality of service, reliability, and hardware life. The Microsoft/WSP
secondary analysis remains in its released functional unit of one Vcore-year.
No conversion between IT MWh and Vcore-year was made because the public archive
does not provide a workload-independent mapping between them.

The package supports a cooling-system cradle-to-grave boundary and a broader
facility cradle-to-grave boundary. The former includes cooling and
heat-rejection equipment, fluids, represented maintenance and replacement,
operation, and end of life. The latter can also include building, electrical,
and IT assets. Common systems may be excluded only when their quantity,
performance, lifetime, and end-of-life treatment are unchanged. Onsite water
and electricity-supply-chain water are reported separately. Location- and
market-based electricity are not merged.

### 2.3. Dataset roles and inclusion criteria

Table 1 distinguishes eight downloaded source families according to i) the
records used, ii) their numerical role in this study, iii) the unresolved
boundary or transfer limit, and iv) the permissible claim class. This
source-to-claim mapping prevents software readability from being mistaken for
compatibility with the case model.

**Table 1. Numerical role and boundary assigned to downloaded evidence.**

| Source and evidence used | Numerical role in this paper | Boundary or transfer limit | Claim class |
|---|---|---|---|
| Microsoft/WSP archive with 24 totals, component tables, 2 electricity anchors, and pedigree records [14,15] | Arithmetic reconstruction, foreground contribution model, crossover and stress analyses | Licensed background inventories and complete bills of quantities are not public | Released/reconstructed |
| EPA eGRID with 459 state/DC-year rows and 9 U.S. aggregates [40,41] | Common-basis generation-rate scenarios and historical trend | Direct generation rates are not consumption-based lifecycle electricity inventories | Screening transformation |
| Federal LCA Commons U.S. Electricity Baseline 2023 and IPCC GWP method [42] | Linked consumption-system factors for 60 balancing authorities, 10 FERC regions, and the United States | Unlinked technosphere inputs remain zero-burden cutoffs and are not harmonized with the released cooling foreground | Partial linked-system screen |
| Boavizta with 48 server PCF records [43] | Server-manufacturing dispersion and common-scaling stress | Products, configurations, PCRs, lifetimes, and performance are heterogeneous | Secondary cross-product evidence |
| ÖKOBAUDAT with 6 selected A1-A3 processes [44] | Matched steel- and cement-route procurement levers | German generic factors require architecture-specific bills of quantities | Secondary process evidence |
| NOAA TMY with 8,760 Fayetteville weather rows [45] | Performance-map and hourly-integration software test | No measured four-architecture cooling surface is available | Illustrative only |
| USLCI and 7 GLAD hydrogen archives [46,47] | Exchange and interoperability tests | Product-system links, allocation, providers, and LCIA methods are unresolved | Registered/unlinked |
| USGS watershed boundary with HU12 geometry [48] | Spatial data contract test | Geometry is not withdrawal, consumption, or water-scarcity characterization | Registered/unlinked |

Provider-native raw files remain outside the public repository when
redistribution permission is unclear or large upstream archives have not been
reviewed for redistribution. Derived tables retain filenames, worksheets,
fields, units, and checksums.

### 2.4. Static lifecycle calculations

For IT capacity \(P_\mathrm{IT}\), utilization \(u\), and one year, annual IT
electricity is

\[
E_\mathrm{IT}=P_\mathrm{IT}u(8760).
\tag{1}
\]

Facility electricity is

\[
E_\mathrm{facility}=E_\mathrm{IT}\mathrm{PUE}.
\tag{2}
\]

For operational impact factor \(EF_k\), the operational impact per delivered
IT electricity is

\[
I_{k,\mathrm{op}}=EF_k\mathrm{PUE}.
\tag{3}
\]

Equipment production and end-of-life burdens are annualized with discrete
replacement according to

\[
I_{k,\mathrm{eq}} =
\sum_i
\frac{q_i\left\lceil L_s/L_i\right\rceil
\left(I_{k,i}^{\mathrm{prod}}+I_{k,i}^{\mathrm{EOL}}\right)}
{L_s},
\tag{4}
\]

where \(q_i\) is quantity, \(L_s\) the study period, and \(L_i\) service life.
The package also supports a linear screening option. For initial fluid mass
\(m_0\), facility life \(L_f\), annual loss \(m_\mathrm{loss}\), production
factor \(I_k^\mathrm{prod}\), end-of-life factor \(I_k^\mathrm{EOL}\), and direct global-warming factor
\(GWP_\mathrm{direct}\),

\[
m_\mathrm{prod,annual}=\frac{m_0}{L_f}+m_\mathrm{loss},
\tag{5}
\]

\[
I_{k,\mathrm{fluid}}=m_\mathrm{prod,annual}I_k^\mathrm{prod}
+\frac{m_0}{L_f}I_k^\mathrm{EOL},
\qquad
GHG_\mathrm{direct}=m_\mathrm{loss}GWP_\mathrm{direct}.
\tag{6}
\]

The model assumes that annual losses are replaced, so the charge remains
\(m_0\), and that the full remaining charge is treated at facility end of life.
Annual purchases and outputs balance as
\(m_0/L_f+m_\mathrm{loss}\). These equations are part of the software engine. The secondary Microsoft/WSP
analysis uses the normalized component values released by the authors rather
than inventing missing quantities.

### 2.5. Released-model reconstruction

For each of four cooling architectures, two electricity cases, and three
impact metrics, the released total was recomputed from the seven aggregate
categories in the Nature supplementary workbook `Figure4` sheet. These
categories are use phase, building, server, rack/tank, cable, supporting
equipment, and fluid impacts.
This 24-cell test is an arithmetic-consistency audit. It does not validate
confidential quantities, licensed LCA for Experts or ecoinvent processes,
allocation, performance, or field operation.

The public files do not establish one unambiguous climate-method identity for
the electricity endpoints. The article reports IPCC AR5 GWP100 [14]. In the
archived detailed workbook, the numeric values 524.893 and 6.133 kg CO2e/MWh
appear in cells F26 labeled “IPCC AR5 GTP100,” while the GWP100 cells F29 are
blank. Direct worksheet-XML inspection further shows that `Comparative results
0% RE!D118` and `Comparative results 100% RE!D122` reference the blank F29
cells for conventional and renewable electricity. We treat the two numbers as
label-free numerical anchors, not verified GWP100 or
GTP100 factors, and define an intensity-position index

\[
z_s=\frac{g_s-g_R}{g_G-g_R},
\tag{7}
\]

where \(g_G\) and \(g_R\) are the released GaBi electricity anchors and \(g_s\)
is an external screening rate. The released impact for technology \(j\) is
then transferred as

\[
I_{j,s}=I_{j,R}+\left(I_{j,G}-I_{j,R}\right)z_s.
\tag{8}
\]

Equations (7)-(8) reproduce both numerical endpoints exactly. They are not a
background-process substitution. Common units do not resolve the endpoint
method identity or the upstream-boundary mismatch with eGRID. In this study,
\(g_s\) is a screening index and every extrapolation is counted. The slope
of each use-phase line has units of MWh/Vcore-year and is reported as an
*implied electricity-response coefficient*. It is not a measured energy
demand because the two endpoint methods are unresolved.

The crossover of technologies \(a\) and \(b\) follows from equality in Eq.
(8).

\[
g^*=g_R+(g_G-g_R)
\frac{I_{b,R}-I_{a,R}}
{(I_{a,G}-I_{a,R})-(I_{b,G}-I_{b,R})}.
\tag{9}
\]

### 2.6. eGRID harmonization

EPA changed the GWP values used by eGRID. Releases before 2018 used IPCC SAR,
2018-2022 used AR4, and 2023 used AR5 without climate-carbon feedback [40,41].
To remove this avoidable discontinuity, every state and U.S. factor was
reconstructed from net generation and gas-specific annual emissions as follows.

\[
g_{y}^{\mathrm{AR5}}=
\frac{2000M_{\mathrm{CO2},y}
+28M_{\mathrm{CH4},y}
+265M_{\mathrm{N2O},y}}
{E_y}(0.45359237),
\tag{10}
\]

where CO2 is reported in short tons, CH4 and N2O in pounds, \(E_y\) in MWh,
and the final factor converts pounds to kilograms. The provider-published
CO2e rate was retained as a comparison. The provider U.S. aggregate, rather
than the 50-state-plus-DC reconstruction, was used for national results.
Puerto Rico was excluded from the state/DC panel. The resulting scope coverage
was reported for each year.

The eGRID factors describe in-state generation. They are not consumption
mixes, marginal rates, hourly signals, contractual procurement, or LCIs with
upstream fuel and infrastructure. No state-specific LCA is claimed.

### 2.7. Federal LCA Commons electricity accounting

The 2023 U.S. Electricity Baseline was downloaded from the Federal LCA Commons
as openLCA 2 JSON-LD together with the repository's IPCC GWP method [42]. The
inventory contains 947 processes and 142 product systems generated with
ElectricityLCI 3.0.0. We retained 71 non-residual, at-user consumption systems,
consisting of 60 balancing authorities, 10 FERC regions, and the national mix. The matched
residual-consumption systems were calculated separately as a market-based
accounting sensitivity and were never pooled with the ordinary consumption
systems.

For each product system, process links defined the technosphere coefficients.
Activities were solved by fixed-point iteration for the declared target of 1
MWh at user. All exchange and target units were converted through the JSON-LD
unit groups. Elementary exchanges were characterized with IPCC AR5-100
category UUID `7d05b807-2caa-3cd9-b55c-399d3b820cbc`. The calculation reports
process count, link count, iteration count, maximum balance residual, impacts
from generation processes, and all other linked upstream and infrastructure
impacts.

An input without a product-system provider link was assigned no upstream
burden, consistent with the published link structure, and was recorded as a
cutoff. The national system contained 287 such exchanges. Because their
omitted magnitude was not bounded and the calculation was not independently
reproduced in openLCA or Brightway, the resulting factors are termed *partial
linked-system factors*. They improve on a direct-generation proxy but do not
constitute complete lifecycle benchmarks.

The provider scope includes trade, transmission and distribution losses, and
upstream fuel supply. Generation infrastructure is included only for the
provider-specified gas, oil, coal, solar, wind, and geothermal technologies.
other generation infrastructure and transmission/distribution infrastructure
are outside scope [42]. The very low factors in some hydropower-dominated
systems must not be interpreted as complete electricity LCAs.

### 2.8. Transferability diagnostics

Each of the 459 state-year rates was classified as below, between, or above
the two released electricity anchors. Equation (8) is interpolation only for
the middle class.

The earlier analysis added transparent allowances of 0, 25, 50, 75, and 100
kg CO2e/MWh to every 2023 eGRID rate. Those values were not data-based and are
retained only in the Supplementary Information as a diagnostic of the direct
generation boundary. The primary boundary analysis instead uses the partial
linked-system factors in Section 2.7. We also report the exact numerical
clearance between the lowest 2023 direct rate and the
cold-plate/single-phase crossover, \(g^*-\min(g_s)\), without interpreting it
as an upstream estimate.

Functional-unit sensitivity was evaluated separately. At each state-year, the
minimum multiplicative increase in two-phase impact per equivalent useful
computation required to equal the second-ranked architecture was

\[
\delta_{\mathrm{service}}=
\frac{\min_{j\ne 2P}I_j}{I_{2P}}-1.
\tag{11}
\]

This correction represents an unresolved combination of useful throughput,
server count, quality of service, lifetime, and replacement. It is not a
measured two-phase penalty.

### 2.9. Rank-robustness and stress analyses

The main robustness analysis uses equal relative half-widths so that one
assumption block is not made influential merely by assigning it a wider range.
For every Federal LCA Commons factor, we found the smallest half-width \(h\)
at which the nominal numerical first rank could be reversed. Five sets were
tested, namely i) shared grid only, ii) technology-specific use phase only,
iii) embodied burden only, iv) service equivalence only, and v) all four blocks
at the same \(h\). The grid
multiplier was common and nonnegative. Foreground multipliers could vary in
opposite adverse directions for the nominal winner and each competitor. All
monotone adverse foreground directions and both shared-grid endpoints were
evaluated, and the first crossing was found by bisection.
The reported threshold is an exact certificate for the declared box, not a
probability or empirical uncertainty interval.

For comparison with the earlier screening analysis, we also retained seeded,
20,000-iteration triangular stress designs for the 2023
U.S. generation factor and the lowest-carbon 2023 state. The headline design
used one shared grid multiplier and independent technology-specific
multipliers for use phase, embodied contribution, and impact per equivalent
service. It is the all-block, zero-correlation member of the dependence
analysis described below. Table 2 defines the narrow, screening, and wide
envelopes by pairing grid, use-phase, and service half-widths of ±2%, ±5%, and
±10% with embodied half-widths of ±20%, ±50%, and ±100%, respectively.

**Table 2. Declared half-widths for joint assumption-stress ensembles.**

| Envelope | Grid, use, and service half-width | Embodied half-width | Purpose |
|---|---:|---:|---|
| Narrow | ±2% | ±20% | Numerical stability near released values |
| Screening | ±5% | ±50% | Intermediate declared stress, not a fitted range |
| Wide | ±10% | ±100% | Deliberately severe robustness test |

The triangular mode was 1.0 and the base seed was 20250730. A stable hash of
the context, envelope, active block, and dependence case generated a separate
seed for every design, so output does not depend on loop order. We then repeated
the stress with grid only, use phase only, embodied contribution only, service
equivalence only, and all four blocks active. Technology-specific multipliers
were coupled with a Gaussian copula at declared latent correlations of 0, 0.5,
and 1 while retaining the same triangular marginals. These correlations are
not measurements. Rank frequencies describe the declared designs. They are
not posterior probabilities, confidence levels, or a substitute for empirical
uncertainty distributions.

Numerical convergence was checked with nested 5,000-, 20,000-, and
80,000-draw runs using the same scenario seeds. The binomial Monte Carlo
standard error is reported only as integration precision within each declared
design. It is not a confidence interval for cooling performance or a remedy
for unsupported input distributions.

### 2.10. Server, construction, and data-priority analyses

Boavizta records were filtered to `Datacenter/Server` products with total GHG,
manufacturing share, and lifetime. Manufacturing GHG was calculated as total
product GHG times manufacturing share and annualized by declared lifetime.
The candidate-flow table retains all 55 server records. Of these records, 48
met the three-field rule, while seven Lenovo records were excluded because manufacturing share was
blank. No candidate was silently discarded.
The minimum, quartiles, median, and maximum annualized values were divided by
the empirical median and used only as common multiplicative stresses on the
released compute, storage, and networking contributions. This preserves a
unitless scale test without treating different servers as functionally
interchangeable.

Selected ÖKOBAUDAT A1-A3 steel and cement records were compared within product
families according to

\[
R=100\left(1-\frac{I_\mathrm{alternative}}
{I_\mathrm{baseline}}\right).
\tag{12}
\]

No material factor was multiplied by an assumed data-center quantity.

For data priority, released pedigree scores were averaged by component and
combined with mean GHG contribution share \(S_c\) according to

\[
P_c=S_c\left(\frac{D_c-1}{4}\right),
\tag{13}
\]

where \(D_c=1\) is best and 5 worst. Because Eq. (13) is heuristic, rank
robustness was tested using
\(P_c=S_c^a[(D_c-1)/4]^b\) for
\(a,b\in\{0.5,1,2\}\). This is a screening priority, not formal
value-of-information.

### 2.11. Temporal performance and software controls

The package can bilinearly interpolate a bounded IT-load/dry-bulb performance
map and integrate its cooling-only partial PUE against hourly conditions using
one declared, constant grid factor. Wet-bulb values are schema-checked but are
not an interpolation coordinate, and non-cooling facility overhead is outside
this partial-PUE calculation. It rejects uncovered operating points, and
extrapolation is disabled. The Fayetteville TMY file
and synthetic performance surface are used only in software examples because
no measured four-architecture surface was available.

Reliability is represented with Weibull failure,
\(F(t)=1-\exp[-(t/\eta)^\beta]\), renewal expectation, and optional Arrhenius
life acceleration. openLCA JSON-LD and Brightway mappings preserve process and
flow identifiers, providers, units, locations, and uncertainty metadata.
USLCI and GLAD imports test exchange, not case-model completeness.

The scenario audit checks required metadata, duplicate identifiers, physical
values, uncertainty declarations, evidence labels, and comparative intent.
The comparison validator additionally requires matching functional units,
system boundaries, electricity accounting, allocation and replacement rules,
and LCIA methods. For a declared public assertion, each modeled input group
must map to a registered source identifier. Synthetic inputs, unquantified
uncertainty, and insufficient declared review remain blockers. These checks
also reject non-finite numeric inputs, retain the field-to-source map in result
manifests, and require a matching inclusion/exclusion record for custom
comparative boundaries. They verify metadata consistency only and cannot authenticate a citation,
distribution, review status, physical model, or ISO conformity [35,36].

OpenAI Codex (OpenAI) was used in a supporting role during software
development and review, test generation, plotting-code review, and manuscript
organization and language editing. It did not provide primary data or serve as
an evidence source. Reported numerical results were regenerated with the
version-controlled deterministic workflows described above and checked
against the cited sources and automated tests under author supervision.

## 3. Results

### 3.1. Released-model method identity

Figure 2 compares the released reductions relative to air cooling for cold
plate, single-phase immersion, and two-phase immersion under the U.S.-grid case
across GHG, primary energy, and blue water. All 24 released combinations of
architecture, electricity scenario, and impact metric reconciled to the seven
published Figure-4 contributions at workbook precision. Under the released
U.S. grid case, the reconstructed table
reports 20.66% lower GHG, 20.00% lower primary energy, and 46.78% lower blue
water for two-phase immersion than air cooling. These are reproduced source
results, not independent comparisons.

The cell-level audit changed their permissible use. The article identifies
AR5 GWP100, but the detailed workbook's numeric endpoint cells are labeled
AR5 GTP100 and the corresponding GWP100 cells are blank. Comparative
use-phase formulas also reference those blank F29 cells. The two numeric
endpoints lack a resolved LCIA-method identity in the public archive. The
implied use-phase response coefficients
were 0.06317, 0.05364, 0.05259, and 0.05006 MWh/Vcore-year for air, cold plate,
single-phase, and two-phase, respectively, with zero-intensity intercepts of
0.010-0.013 kg CO2e/Vcore-year. These slopes are useful diagnostics, but they
are not independently measured electricity demand.

![Figure 2. Relative GHG, primary-energy, and blue-water reductions for cold plate, single-phase immersion, and two-phase immersion versus air cooling under the released U.S.-grid case. The 24 architecture, electricity, and impact combinations reconcile at workbook precision and reproduce the released arithmetic without validating the underlying inventories, LCIA-method identity, or field performance.](figures/figure1_microsoft_grid_reductions.svg)

### 3.2. Historical generation-emission intensity

The common-basis U.S. generation factor declined from 517.731 kg CO2e/MWh in
2012 to 349.667 kg CO2e/MWh in 2023, a 32.462% reduction. The trajectory was
not monotonic. The factor rose from 373.097 in 2020 to 388.699 in 2021 before
declining. Reconstructing every year with AR5 GWP100 changed the
provider-published national rate by no more than 0.248 kg CO2e/MWh, in 2012.
The direct CO2-only rate was 348.000 kg/MWh in 2023. Thus, the long-run decline
is not an artifact of eGRID's transition from SAR to AR4 and AR5.

The 50-state-plus-DC reconstruction matched the official national result
through 2018. From 2019 onward it was 0.32-0.43% lower because the panel
covered 99.55-99.58% of the provider U.S. generation after excluding Puerto
Rico. Figure 3 places all 459 harmonized state/DC generation rates from nine
eGRID releases on a common kg CO2e/MWh axis, overlays the reported provider
U.S. aggregate trajectory as an orange polyline, and identifies points below
the 96.704 kg CO2e/MWh cold-plate/single-phase crossover in blue. The provider
aggregate was retained for the national series and was not fitted to the
state/DC points. Across the full panel, 137 of 459 numerical rates lay outside
the two released cooling anchors, so 29.85% of the transfers were
extrapolations.

![Figure 3. Harmonized AR5-GWP100 eGRID state/DC generation rates for nine releases, with electricity intensity on the horizontal axis in kg CO2e/MWh. The orange polyline connects the reported provider U.S. aggregate for each year. Blue points fall below the released-model numerical cold-plate/single-phase crossover. These are direct-generation scenarios, not consumption LCIs or state cooling LCAs.](figures/figure6_historical_grid_transition.svg)

### 3.3. Lifecycle electricity factors

Figure 4 compares the partial linked-system GHG intensity of 10 FERC-region
consumption systems and the national system on a delivered-electricity basis.
Each bar separates generation-process impacts from other linked upstream and
infrastructure impacts, while the two dashed lines locate the 96.704 and
524.893 kg CO2e/MWh released numerical anchors.

The 71 non-residual Federal LCA Commons systems ranged from 0.921 to 987.844
kg CO2e/MWh. The national linked-system factor was 422.931 kg CO2e/MWh. It
comprised 369.848 from electricity-generation processes and 53.084 from other linked
upstream and infrastructure processes. It exceeded the 2023 national eGRID
direct-generation rate by 73.264 kg CO2e/MWh, although the difference also
contains consumption-mix, delivery-loss, flow-coverage, and boundary effects
and is not an isolated upstream correction.

All 10 FERC-region systems exceeded the 96.704 kg CO2e/MWh numerical
cold-plate/single-phase crossover. Their factors ranged from 238.897 kg CO2e/MWh for
NYISO to 557.110 kg CO2e/MWh for MISO. Ten of 60 balancing-authority systems
fell below the crossover, and 15 of all 71 systems exceeded the released high
anchor of 524.893 kg CO2e/MWh. The numerical cooling screen placed two-phase
first in all 71 systems, but this is not a common-method comparative LCA because
the cooling foreground method remains unresolved.

The national result converged in five fixed-point iterations with a balance
residual of zero at the reporting precision, using 582 processes and 1,174
links. It also contained 287 unlinked technosphere exchanges across 47
processes, including fuels, construction materials, chemicals, and reclaimed
water. Their upstream burdens were zero in the linked calculation and were not
bounded. The factor is more complete than eGRID direct emissions but
still a partial linked-system result.

The national residual-consumption system was 455.350 kg CO2e/MWh, comprising
399.934 from generation processes and 55.417 from other linked processes. It
was 7.67% above the ordinary consumption-system result. This difference is an
electricity-accounting sensitivity, not an uncertainty interval, and the two
accounting products were not mixed within any cooling screen.

![Figure 4. IPCC AR5-GWP100 partial linked-system electricity factors for 10 FERC regions and the United States. The horizontal axis is kg CO2e/MWh delivered at the user. Bars separate generation-process impacts from other linked upstream and infrastructure impacts. The green dashed line marks the 96.704 kg CO2e/MWh cold-plate/single-phase numerical crossover. The purple dashed line marks the 524.893 kg CO2e/MWh released high numerical anchor. Neither line creates method equivalence.](figures/figure10_lifecycle_electricity.svg)

### 3.4. Rank-robustness thresholds

Figure 5 compares the national critical half-widths for shared grid, use phase,
embodied burden, service equivalence, and simultaneous equal-width variation
in panel A. Panel B plots the all-block critical half-width against lifecycle
electricity intensity for 60 balancing authorities, 10 FERC regions, and the
national system.

At the national lifecycle factor, the numerical two-phase first rank could not
be reversed by a shared grid-factor change within the tested nonnegative range
through a 99.999% half-width. With technology-specific variation, reversal
occurred at 2.994% for use phase, 22.154% for embodied burden, and 2.637% for
service equivalence. When all four blocks used the same half-width, the first
reversal occurred at 1.318%, against single-phase.

Across all 71 electricity contexts, the all-block critical half-width ranged
from 1.123% at PUD No. 1 of Douglas County to 1.479% at Duke Energy Progress
West. At the lowest-carbon system, the critical competitor was cold plate.
At that point, the embodied-only and service-only thresholds were 2.291% and
2.246%, while use-phase and shared-grid changes did not reverse rank through
99.999%.
The ranking is numerically fragile even though it survives every
unperturbed electricity factor.

This equalized analysis reverses one conclusion from the earlier triangular
stress design. Embodied variation had appeared to cause the largest rank loss
because its assigned half-width was 10 times those of use phase and service.
At equal widths, embodied burden has the largest national one-block tolerance,
whereas service equivalence and use phase are limiting. The earlier stress
frequencies
and their dependence/convergence diagnostics remain in the Supplementary
Information as evidence about the chosen design, not the technologies.

The one-sided functional-unit diagnostic gives a complementary threshold.
Across 2023 direct-rate contexts, a 5.24-6.04% adverse correction to two-phase
impact per equivalent useful computation would erase its numerical first rank.
This is a break-even requirement for future measurements, not an observed
performance difference.

![Figure 5. Deterministic equal-width rank-robustness certificates. (A) National critical half-width by active block. (B) all-block thresholds across 60 balancing authorities, 10 FERC regions, and the national system. Bounds are uncertainty sets, not probability distributions or physical validation.](figures/figure11_standardized_robustness.svg)

### 3.5. Server and construction evidence

Of 55 Boavizta `Datacenter/Server` candidates, 48 included records spanned
465-2,503 kg CO2e/server for
manufacturing, a 5.38-fold range. Annualized values spanned 116-626 kg
CO2e/server-year. Commonly scaling the released server-related contributions
across the empirical 0.38-2.06-fold annualized envelope did not change the
deterministic two-phase first rank. That structural stress does not model
architecture-specific server count, configuration, throughput, or lifetime.

The selected ÖKOBAUDAT high-scrap electric-arc-furnace galvanized steel record
had 59.9% lower A1-A3 GHG, 47.9% lower nonrenewable primary energy, and 52.0%
lower freshwater use per kilogram than the selected low-scrap
blast-furnace-route record. The selected CEM III cement record had 49.8% lower
GHG, 12.1% lower nonrenewable primary energy, and 23.5% lower freshwater use
than CEM II/A. These are procurement levers, not data-center reductions. Their
facility effect remains unknown until each architecture has a reviewed bill of
quantities.

### 3.6. Data-priority sensitivity

Under the base contribution-times-weakness index, use phase was the highest
priority, followed by storage, networking, and compute-server evidence. Across
the nine alternative exponent combinations, use phase ranked first in eight
and in the top three in eight. Networking ranked first once, storage remained
in the top three in all nine, and compute was in the top three in four. The
rank of use phase ranged from first to fourth.

This sensitivity changes the interpretation of the pedigree result. It
supports a near-term measurement sequence—hourly IT and cooling electricity,
then server inventories and functional performance—but not a unique value of
information. A formal acquisition decision requires empirical parameter
distributions, correlations, measurement cost, and the loss associated with a
wrong architecture choice [34].

### 3.7. Software verification and practitioner outputs

The full local test suite covers calculation, fluid mass conservation,
interoperability, reliability, public-data parsing, practitioner workflow,
GUI/API parity, endpoint reconstruction, eGRID harmonization, Federal LCA
Commons process-system solution, cutoff reporting, equal-width robustness,
comparison incompatibility, field-level lineage, stress-design determinism,
and provenance integrity. Paper-reconstruction tests skip explicitly when
locally held provider files are absent. No substitute values are inserted.

A practitioner supplies IT capacity, utilization, PUE, facility lifetime,
onsite water, location- and market-based electricity factors, optional
equipment/fluid inventories, and a citable source record. The package returns
annual and per-IT-MWh impacts, contribution breakdowns, evidence
classification, warnings or blockers, a scenario digest, model version, and
the next-data list. Advanced users can add hourly performance maps,
replacement and reliability, and openLCA/Brightway inventories. Software
consistency does not validate user inputs, the truth of metadata labels, or
the physical adequacy of a screening model.

## 4. Discussion

### 4.1. Comparative claim boundaries

The released table and every unperturbed electricity screen place two-phase
first. Three independent findings prevent that order from becoming a public
comparative conclusion. First, the archive does not resolve the climate method
of the numeric electricity endpoints. Second, the cooling foreground cannot be
recalculated under the same AR5 method as the electricity inventories. Third,
useful computation has not been measured across the four architectures. The most
important outcome is the boundary between reproduced arithmetic and
a physically identified comparison.

The 96.704 kg CO2e/MWh cold-plate/single-phase crossover is a property of two
released numerical endpoints. It helps locate where their affine lines cross,
but it is not an environmental threshold for a real site. Likewise, survival
across 71 electricity factors explores one background dimension. It does not
provide 71 independent observations of cooling performance. A transferable
assessment must report the numerical result together with its functional unit,
method identity, system boundary, cutoff structure, robustness definition, and
claim status.

### 4.2. Electricity-system boundaries

The eGRID reconstruction shows that the 32.46% historical national decline is
robust to changing GWP conventions. The Federal LCA Commons calculation then
replaces an arbitrary additive boundary allowance with a provider-linked
consumption model. At the national point, linked upstream and infrastructure
processes add 53.084 kg CO2e/MWh beyond generation processes, and the total is
73.264 kg CO2e/MWh above the eGRID national rate. All FERC regions lie above
the numerical cold-plate/single-phase crossover.

Provider-linked consumption modeling improves boundary traceability but does
not complete harmonization because the difference between the two national
factors also reflects delivery losses, consumption versus
generation geography, and elementary-flow coverage. More importantly, 287
unlinked technosphere exchanges still carry zero upstream burden. A complete
calculation requires those providers to be linked or their omitted impacts to
be bounded and independently reproduced. Even then, electricity cannot repair
the unresolved cooling-foreground LCIA method. Location- and market-based
cases must also remain consistent throughout the product system [22,23].
The 7.67% national difference between ordinary and residual consumption mixes
shows that the accounting choice is consequential even before the cooling
foreground is harmonized.

### 4.3. Robustness-bound design

The earlier triangular analysis assigned embodied burden a half-width 10 times
the use-phase and service widths. Its conclusion that embodied variation was
the largest one-block source of rank loss conflated sensitivity with an
arbitrary range choice. The equal-width certificate separates range assignment
from model sensitivity. At the national lifecycle factor, embodied burden can vary by 22.15%
before a worst-case one-block reversal, whereas service equivalence and use
phase require only 2.64% and 2.99%.

The all-block threshold of 1.32% is not a confidence bound. It is the radius of
a specified box in which a shared grid multiplier and adverse
technology-specific foreground multipliers cannot reverse the numerical first
rank. The certificate is falsifiable because any proposed empirical uncertainty
model can be compared against the same bound structure. A probability of rank
would additionally require measured marginal distributions and correlations
[30].

Because functional equivalence and use-phase demand are limiting at equal
widths, near-term measurements should close those two evidence gaps first,
while bills of quantities and material inventories remain necessary for a
common-method lifecycle comparison. The legacy triangular results still demonstrate that
dependence assumptions matter, but they do not rank the real-world importance
of uncertainty blocks.

### 4.4. Functional equivalence

Vcore-year is more informative than facility area or rack count, but it is
still a proxy. Equivalent useful computation depends on workload, accelerator
utilization, memory and network constraints, throttling, overclocking,
availability, and quality of service. The one-sided 5.50% median threshold and
the symmetric 2.64% national service bound are break-even requirements, not
measured penalties. They define the approximate resolution required of a
comparative experiment. ITU-T L.1410 similarly requires an explicit functional
unit and comparative baseline for ICT services [18].

A shared protocol should collect several forms of evidence for every
architecture. It should measure i) completed workload or benchmark output,
ii) IT and cooling power, and iii) inlet and component temperatures together
with flow and pressure drop. It should also record iv) fan, pump, cooling
distribution unit, and heat-rejection power, v) onsite water use and
failure/maintenance events, and vi) uncertainty and calibration lineage over
the same load-weather domain. Server count, configuration, and replacement must be
tracked with that performance. A thermal result without useful computation
cannot close the LCA functional unit. A product carbon footprint without
architecture quantity cannot close the embodied inventory.

### 4.5. Grid decarbonization and evidence priorities

National grid decarbonization simultaneously lowers every
electricity-dependent cooling result, contracts the absolute value of
operational efficiency, and increases the fraction supplied by embodied
terms. The absolute modeled two-phase-versus-air benefit fell 29.45% between
the 2012 and 2023 generation conditions, a change that percentage savings alone
do not reveal.

This shift explains why the Boavizta and ÖKOBAUDAT datasets matter even though
they were not inserted into architecture totals. The 5.38-fold server
manufacturing range is larger than many cooling differences, but heterogeneous
PCFs cannot be treated as an uncertainty distribution for interchangeable
servers. The approximately 50-60% material-route GHG levers are large per
kilogram, but kilograms by architecture are missing. The needed research
product is a linked foreground dataset that combines useful computation, server
configuration and lifetime, cooling bill of quantities, material route, and
measured operation under one functional unit.

### 4.6. Relationship to LCA software

OpenDC-LCA does not replace openLCA, Brightway, Temporalis, premise, or
bw_timex. Those tools provide process-network calculation, database
management, prospective backgrounds, or time-explicit LCA [27-29,37,38]. The
OpenDC-LCA assessment layer adds six comparison-audit functions. First, it
checks functional equivalence
against useful computation. Second, it represents load-weather cooling
performance and performs bounded annual integration. Third, it represents
reliability, replacement, and cooling fluids. Fourth, it separates lifecycle
electricity, direct generation rates, market instruments, and marginal
signals. Fifth, it preserves source and transformation provenance. Finally,
its automated metadata validator blocks declared comparisons with incompatible
methods, boundaries, or source mappings.

The metadata validator is deliberately narrower than a scientific review
because it trusts
the metadata supplied by the user and cannot determine whether a performance
map is representative, a distribution is empirical, or an external review
occurred. Its role is to catch machine-detectable incompatibilities before
calculation, not to authorize a public environmental claim.

This comparison-audit role also differs from recent data-center performance
and architecture models. AlphaDataCenterCooling provides operational
validation of a cooling plant
[17], while d'Orgeval et al. compare full data-center architectures and, for a
subset, normalize by computational performance [16]. The present work tests
whether published secondary LCA results retain their meaning when moved across
electricity datasets and claim contexts. It does not duplicate either primary
modeling capability.

This is why USLCI and GLAD hydrogen archives were exchange-tested but not
forced into the results. Backup power is a relevant future application, yet a
hydrogen dataset becomes numerical evidence only after technology,
electricity source, compression/storage, allocation, geography, and LCIA
method are linked to a declared product system.

### 4.7. Hyperscale applications

The most useful extension of the Microsoft/WSP work is not another static
national scenario. It is a jointly governed evidence package that allows the
released model to be updated without weakening its functional-unit insight.
Closing the method, foreground, performance, electricity, and uncertainty gaps
requires five additions. First, the original GWP100 electricity factors or
elementary-flow inventories are needed to resolve the public workbook's blank
F29 cells. Second, the package requires architecture-specific, anonymized bills
of quantities and service lives. Third, it requires measured performance
surfaces for IT output, server power, facility parasitics, and onsite water
across load and weather. Fourth, it requires a complete provider-linked
lifecycle electricity model under the same LCIA method, with cutoffs linked or
bounded and with location-based, market-based, and marginal operational signals
reported separately. Finally, empirical uncertainty and correlation
information are needed for rank-probability and value-of-information analyses.

OpenDC-LCA supplies schemas, transformations, tests, and claim boundaries for
that collaboration. A preliminary university high-performance-computing site
characterization illustrates why those claim boundaries matter in practice. The
site combines dedicated IT and liquid-cooling paths with raised-floor CRAC
cooling shared by several institutional users. It therefore cannot support a
single facility PUE without a documented allocation of shared support loads.
The preliminary record contains no operational time series and does not report
site energy, cooling performance, PUE, or environmental impacts. It instead
defines the metering sequence required to produce those results.

The custom-boundary validator now classifies each energy item as metered,
allocated, or excluded. Metered records identify their meter, allocated records
identify an allocation method, and excluded records state a rationale. A
facility-PUE label requires a complete energy-item inventory, a metered IT-load
boundary, and no excluded shared-support item. A partial record can instead
report a dedicated-support ratio for the stated UPS and dedicated-cooling
boundary. This check does not authenticate meter data or determine whether an
allocation is physically representative, but it prevents incomplete shared
infrastructure from being silently labeled as facility energy.

The two conclusions supported independently here are the
released arithmetic and the national direct-generation trend. The cooling
crossovers, first ranks, and response coefficients remain conditional numerical
screens until the five evidence gaps are closed.

### 4.8. Limitations and evidence requirements

Because this analysis is secondary, it does not recreate proprietary
background inventories, confidential bills of quantities, the full
virtual-core model, or measured hyperscale operation. Equation (8) uses a numerical axis whose
climate-method identity is unresolved in the public archive. The Federal LCA
Commons factors contain 287 national unlinked technosphere exchanges. The
custom solver has not been independently reproduced in openLCA or Brightway.
The additive allowance, triangular marginals, and copula dependence cases are
secondary diagnostics, not estimates. The convergence check limits numerical
sampling error within those designs. It does not reduce epistemic uncertainty
in the ranges, dependence structure, cutoffs, or foreground model. eGRID
state rates omit consumption transfers, contracts, hourly dispatch, and
marginal effects.

The climate-focused extension does not provide a boundary-consistent
comparison of primary energy, water scarcity, toxicity, resource use, or other
impact categories. The Boavizta sample mixes products and methods, while
ÖKOBAUDAT records are German generic A1-A3 factors. The TMY and synthetic performance examples validate
software pathways, not technology performance. The USGS file provides
watershed geometry rather than water consumption or AWARE characterization.
Reliability models omit dependent failures, repair queues, redundancy and
maintenance logistics unless the user supplies them. A coauthor methodology
review is not an independent critical review.

The evidence supports a methodological Technology Assessment of transferability,
not a public assertion that one cooling architecture is environmentally
preferable. Such an assertion would require resolved common-method inventories,
reviewed primary performance and useful-computation data, architecture bills
of quantities, water-scarcity characterization, empirically supported joint
uncertainty, and an external critical review panel.

## 5. Conclusions

This assessment separates three evidence levels that had previously been
combined. These levels are reproduced source arithmetic, direct-generation
trend analysis, and conditional cooling screens. All 24 published totals were arithmetically
reproduced, but the public archive does not resolve whether the two numeric
electricity endpoints used by the screening axis are AR5 GWP100 or GTP100.
Cooling ranks derived from that axis cannot be interpreted as common-method
comparative LCA results.

The national eGRID generation factor declined 32.46% from 2012 to 2023 after
all nine releases were harmonized to AR5 GWP100. The Federal LCA Commons
national consumption system yielded 422.93 kg CO2e/MWh, including 53.08
kg CO2e/MWh from linked processes beyond generation, and all 10 FERC regions
lay above the 96.70 kg CO2e/MWh numerical crossover. These partial
linked-system factors retain documented technosphere cutoffs and require
independent calculator verification before benchmark use.

Equal-width robustness analysis corrected the earlier attribution of rank
loss to embodied variation. At the national lifecycle factor, the first-rank
screen failed at 2.64% service-equivalence variation, 2.99% use-phase
variation, and 22.15% embodied variation. Simultaneous equal-width changes
failed at 1.32%. The dominant near-term evidence needs are
architecture-resolved useful computation and use-phase demand, followed by
complete bills of quantities and common-method inventories.

The OpenDC-LCA validator rejects configured comparisons whose declared
metadata contain mismatched functional units, boundaries, electricity
accounting, LCIA methods, or missing field-level source mappings. This check
detects declared incompatibilities but does not verify the underlying science.
The study is suitable as a transferability Technology Assessment. It does not
support a public claim of environmental superiority among cooling
architectures.

## Data and code availability

OpenDC-LCA version 1.1.0 is publicly available at
https://github.com/UARK-NED3/OpenDC-LCA and
https://github.com/UARK-NED3/OpenDC-LCA/releases/tag/v1.1.0. The development
revision evaluated here adds the Federal LCA Commons solver, cutoff reporting,
equal-width robustness certificates, and comparison-level metadata checks. It
will be tagged and archived before submission. Analysis metadata and the
provider-file manifest record file sizes and SHA-256 checksums. Provider-native
files remain outside Git when redistribution permission is unclear or a large
upstream archive has not been reviewed for redistribution. The Microsoft
archive, eGRID files, Federal LCA Commons baseline and method, and NOAA data are
available from their public providers [15,40-42,45]. No DOI-bearing software
archive is available at the time of this draft.

## Competing interests

Braden Stevens and Pengjiang Xiang are full-time employees of Harrison French
& Associates Ltd.

## Ethics statement

This secondary study used public or author-held engineering datasets and did
not involve human participants or animals. Research-ethics approval was not
required.

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During preparation of this work, the authors used OpenAI Codex to support code
review, test development, figure-code review, manuscript organization, and
language editing. The authors reviewed and edited the resulting material,
verified the reported calculations and cited sources, and take full
responsibility for the content of the article.

## References

1. Masanet, E., Shehabi, A., Lei, N., Smith, S. & Koomey, J. Recalibrating
    global data center energy-use estimates. *Science* **367**, 984-986
    (2020). https://doi.org/10.1126/science.aba3758
2. International Energy Agency. Data centres and data transmission networks.
    https://www.iea.org/energy-system/buildings/data-centres-and-data-transmission-networks
    (accessed 11 August 2026).
3. Khalaj, A. H. & Halgamuge, S. K. A review on efficient thermal management
    of air- and liquid-cooled data centers. *Applied Energy* **205**, 1165-1184
    (2017). https://doi.org/10.1016/j.apenergy.2017.08.037
4. Alkrush, A. A., Salem, M. S., Abdelrehim, O. & Hegazi, A. A. Data centers
    cooling: a critical review of techniques, challenges, and energy saving
    solutions. *International Journal of Refrigeration* **160**, 246-262
    (2024). https://doi.org/10.1016/j.ijrefrig.2024.02.007
5. Kanbur, B. B., Wu, C., Fan, S. & Duan, F. Two-phase liquid-immersion data
    center cooling system: experimental performance and thermoeconomic
    analysis. *International Journal of Refrigeration* **118**, 290-301
    (2020). https://doi.org/10.1016/j.ijrefrig.2020.05.026
6. Kanbur, B. B., Wu, C., Fan, S. & Duan, F. System-level experimental
    investigations of direct immersion cooling data center units with
    thermodynamic and thermoeconomic assessments. *Energy* **217**, 119373
    (2021). https://doi.org/10.1016/j.energy.2020.119373
7. Huang, Y., Liu, B., Xu, S., Bao, C., Zhong, Y. & Zhang, C. Experimental
    study on immersion liquid cooling performance of high-power data center
    servers. *Energy* **297**, 131195 (2024).
    https://doi.org/10.1016/j.energy.2024.131195
8. Wu, X. et al. Investigations on heat dissipation performance and overall
    characteristics of two-phase liquid immersion cooling systems for data
    center. *International Journal of Heat and Mass Transfer* **239**, 126575
    (2025). https://doi.org/10.1016/j.ijheatmasstransfer.2024.126575
9. Whitehead, B., Andrews, D., Shah, A. & Maidment, G. Assessing the
    environmental impact of data centres. Part 1: background, energy use and
    metrics. *Building and Environment* **82**, 151-159 (2014).
    https://doi.org/10.1016/j.buildenv.2014.08.021
10. Siddik, M. A. B., Shehabi, A. & Marston, L. The environmental footprint
    of data centers in the United States. *Environmental Research Letters*
    **16**, 064017 (2021). https://doi.org/10.1088/1748-9326/abfba1
11. Ristic, B., Madani, K. & Makuch, Z. The water footprint of data centers.
    *Sustainability* **7**, 11260-11284 (2015).
    https://doi.org/10.3390/su70811260
12. Isler-Kaya, A. & Karaosmanoglu, F. Life cycle assessment of a
    climate-friendly data center cooling device. *Energy and Buildings*
    **288**, 113006 (2023).
    https://doi.org/10.1016/j.enbuild.2023.113006
13. Wenzel, P. M. & Radgen, P. Extending effectiveness to efficiency:
    comparing energy and environmental assessment methods for a wet cooling
    tower. *Journal of Industrial Ecology* **27**, 693-706 (2023).
    https://doi.org/10.1111/jiec.13396
14. Alissa, H. et al. Using life cycle assessment to drive innovation for
   sustainable cool clouds. *Nature* **641**, 331-338 (2025).
   https://doi.org/10.1038/s41586-025-08832-3
15. Alissa, H. et al. Data and model archive for “Using life cycle assessment
   to drive innovation for sustainable cool clouds.” Zenodo record 14268168
   (2024). https://doi.org/10.5281/zenodo.14268168
16. d'Orgeval, A., Sheehan, S., Avenas, Q., Assoumou, E. & Sessa, V.
    Generative AI impact assessment through a life cycle analysis of multiple
    data center typologies. *Applied Energy* **406**, 127288 (2026).
    https://doi.org/10.1016/j.apenergy.2025.127288
17. Wu, S., Zheng, W., Wang, Z., Chen, G., Yang, P., Yue, S., Li, D. & Wu, Y.
    AlphaDataCenterCooling: A new computational model for data center cooling
    system evaluation. *Applied Energy* **380**, 125100 (2025).
    https://doi.org/10.1016/j.apenergy.2024.125100
18. International Telecommunication Union. ITU-T Recommendation L.1410:
    Methodology for environmental life cycle assessments of information and
    communication technology goods, networks and services (2024).
    https://handle.itu.int/11.1002/1000/16010
19. Zhang, M., Carbajales-Dale, M., Ma, X., Guo, L. & Fan, C. Cleaner grid or
    smarter cooling? Environmental impact trade-offs of a data center using
    the life cycle assessment method. *Cleaner Energy Systems* **12**, 100223
    (2025). https://doi.org/10.1016/j.cles.2025.100223
20. Boyd, S. B., Horvath, A. & Dornfeld, D. Life-cycle assessment of
    computational logic produced from 1995 through 2010. *Environmental
    Science & Technology* **47**, 2947-2954 (2013).
    https://doi.org/10.1021/es303012r
21. Malmodin, J. & Lundén, D. The energy and carbon footprint of the global
    ICT and E&M sectors 2010-2015. *Sustainability* **10**, 3027 (2018).
    https://doi.org/10.3390/su10093027
22. Holzapfel, P., Bach, V. & Finkbeiner, M. Electricity accounting in life
    cycle assessment: the challenge of double counting. *International Journal
    of Life Cycle Assessment* **28**, 771-787 (2023).
    https://doi.org/10.1007/s11367-023-02158-w
23. Holzapfel, P., Bunsen, J., Schmidt-Sierra, I., Bach, V. & Finkbeiner, M.
    Replacing location-based electricity consumption with market-based
    residual mixes in background data to avoid possible double counting.
    *International Journal of Life Cycle Assessment* **29**, 1279-1289
    (2024). https://doi.org/10.1007/s11367-024-02294-x
24. Dandres, T., Farrahi Moghaddam, R., Nguyen, K. K., Lemieux, Y., Samson,
    R. & Cheriet, M. Consideration of marginal electricity in real-time
    minimization of distributed data centre emissions. *Journal of Cleaner
    Production* **143**, 116-124 (2017).
    https://doi.org/10.1016/j.jclepro.2016.12.143
25. Sohn, J., Kalbar, P., Goldstein, B. & Birkved, M. Defining temporally
    dynamic life cycle assessment: a review. *Integrated Environmental
    Assessment and Management* **16**, 314-323 (2020).
    https://doi.org/10.1002/ieam.4235
26. Beloin-Saint-Pierre, D. et al. Addressing temporal considerations in life
    cycle assessment. *Science of the Total Environment* **743**, 140700
    (2020). https://doi.org/10.1016/j.scitotenv.2020.140700
27. Cardellini, G., Mutel, C. L., Vial, E. & Muys, B. Temporalis, a generic
    method and tool for dynamic life cycle assessment. *Science of the Total
    Environment* **645**, 585-595 (2018).
    https://doi.org/10.1016/j.scitotenv.2018.07.044
28. Müller, A. et al. Time-explicit life cycle assessment: a flexible
    framework for coherent consideration of temporal dynamics.
    *International Journal of Life Cycle Assessment* (2025).
    https://doi.org/10.1007/s11367-025-02539-3
29. Diepers, T., Müller, A. & Jakobs, A. bw_timex: a Python package for
    time-explicit life cycle assessment. *Journal of Open Source Software*
    **11**, 9621 (2026). https://doi.org/10.21105/joss.09621
30. Groen, E. A. & Heijungs, R. Ignoring correlation in uncertainty and
    sensitivity analysis in life cycle assessment: what is the risk?
    *Environmental Impact Assessment Review* **62**, 98-109 (2017).
    https://doi.org/10.1016/j.eiar.2016.10.006
31. Michiels, F. & Geeraerd, A. How to decide and visualize whether
    uncertainty or variability is dominating in life cycle assessment
    results: a systematic review. *Environmental Modelling & Software*
    **133**, 104841 (2020).
    https://doi.org/10.1016/j.envsoft.2020.104841
32. Lloyd, S. M. & Ries, R. Characterizing, propagating, and analyzing
    uncertainty in life-cycle assessment: a survey of quantitative approaches.
    *Journal of Industrial Ecology* **11**, 161-179 (2007).
    https://doi.org/10.1162/jiec.2007.1136
33. Edelen, A. & Ingwersen, W. Guidance on Data Quality Assessment for Life
    Cycle Inventory Data. U.S. EPA, EPA/600/R-16/096 (2016).
    https://cfpub.epa.gov/si/si_public_record_report.cfm?Lab=NRMRL&dirEntryId=321834
34. Marchese, D. C., Bates, M. E., Keisler, J. M., Alcaraz, M. L., Linkov, I.
    & Olivetti, E. A. Value of information analysis for life cycle assessment:
    uncertain emissions in green manufacturing of electronic tablets.
    *Journal of Cleaner Production* **197**, 1540-1545 (2018).
    https://doi.org/10.1016/j.jclepro.2018.06.113
35. International Organization for Standardization. ISO 14040:2006,
   Environmental management - Life cycle assessment - Principles and
   framework; and ISO 14044:2006, Environmental management - Life cycle
   assessment - Requirements and guidelines.
   https://www.iso.org/committee/54854/x/catalogue/;
   https://www.iso.org/standard/38498.html (accessed 11 August 2026).
36. International Organization for Standardization. ISO 14071:2024,
   Environmental management - Life cycle assessment - Critical review
   processes and reviewer competencies (2024).
   https://www.iso.org/standard/82464.html (accessed 11 August 2026).
37. GreenDelta. openLCA: open source life cycle assessment software.
   https://www.openlca.org/ (accessed 11 August 2026).
38. Mutel, C. Brightway: an open source framework for life cycle assessment.
    *Journal of Open Source Software* **2**, 236 (2017).
    https://doi.org/10.21105/joss.00236
39. UARK-NED3. OpenDC-LCA version 1.1.0.
   https://github.com/UARK-NED3/OpenDC-LCA (accessed 11 August 2026).
40. U.S. Environmental Protection Agency. Emissions & Generation Resource
   Integrated Database (eGRID), detailed data.
   https://www.epa.gov/egrid/detailed-data (accessed 11 August 2026).
41. U.S. Environmental Protection Agency. Frequent questions about eGRID:
   global warming potentials and methodology changes.
   https://www.epa.gov/egrid/frequent-questions-about-egrid
   (accessed 11 August 2026).
42. National Energy Technology Laboratory. U.S. Electricity Baseline, 2023
    data release, version 03.00.000. Federal LCA Commons (2026).
    https://www.lcacommons.gov/lca-collaboration/Federal_LCA_Commons/US_electricity_baseline
    (accessed 11 August 2026).
43. Boavizta. BoaviztAPI data repository.
    https://github.com/Boavizta/boaviztapi (accessed 11 August 2026).
44. Bundesinstitut für Bau-, Stadt- und Raumforschung. ÖKOBAUDAT 2024-II.
    https://www.oekobaudat.de/ (accessed 11 August 2026).
45. National Centers for Environmental Information. Typical Meteorological
   Year data. https://www.ncei.noaa.gov/access/typical-meteorological-year/
   (accessed 11 August 2026).
46. National Renewable Energy Laboratory. U.S. Life Cycle Inventory Database,
   version 1.2026-06.0. Federal LCA Commons.
   https://www.lcacommons.gov/ (accessed 11 August 2026).
47. United Nations Environment Programme. Global LCA Data Access network.
    https://www.globallcadataaccess.org/ (accessed 11 August 2026).
48. U.S. Geological Survey. Watershed Boundary Dataset.
    https://www.usgs.gov/national-hydrography/watershed-boundary-dataset
    (accessed 11 August 2026).
