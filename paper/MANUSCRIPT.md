# OpenDC-LCA: an evidence-governed framework for transferable life-cycle assessment of data-center cooling

**Han Hu and Darin W. Nutter**

Department of Mechanical Engineering, University of Arkansas, Fayetteville,
Arkansas, USA

*Draft for coauthor review. Authorship, order, contributions, target journal,
and corresponding-author information must be confirmed before submission.*

## Abstract

Liquid cooling can reduce data-center operating energy and water use, yet the
preferred architecture depends on electricity supply, compute performance,
hardware and fluid inventories, service life, climate, and the functional unit
used for comparison. Existing studies establish the importance of these
effects but are difficult to update or transfer because foreground bills of
materials and background processes are often proprietary, operational
performance is represented by annual averages, water consumption is rarely
scarcity-weighted, and data-quality assessments are not connected to
measurement priorities. We present OpenDC-LCA, an open-source,
evidence-governed research layer that couples data-center cooling physics to
general life-cycle assessment (LCA) tools while preserving source identity,
functional unit, geography, transformation equations, uncertainty, and
evidence status. The framework supports openLCA JSON-LD and Brightway
interoperability, hourly weather-load-performance integration, discrete and
reliability-driven replacement, uncertainty analysis, and a machine-readable
claim gate. We use released Microsoft/WSP results, EPA eGRID 2023, 48 Boavizta
server product-carbon-footprint records, selected ÖKOBAUDAT construction
processes, NOAA weather data, and the released Microsoft pedigree assessment
to demonstrate analyses that cannot be obtained from any source alone. All 24
released normalized totals were independently reconciled to floating-point
precision. Re-basing the released greenhouse-gas contributions across 51
eGRID state records identified a cold-plate/one-phase-immersion crossover near
61 kg CO2e MWh−1: cold plate was lower only for Vermont among the observed
states, whereas two-phase immersion remained lowest under the released model.
Across the state range, embodied contributions increased from approximately
4% to 57-58% as electricity intensity declined. A contribution-weighted
pedigree diagnostic ranked use-phase performance first and server inventories
next as evidence-improvement priorities. Public server records showed a
manufacturing median of 1,215 kg CO2e per server and a 465-2,503 kg CO2e
range. ÖKOBAUDAT unit-process comparisons indicated 60% lower A1-A3 GHG for
high-scrap electric-arc-furnace steel than a blast-furnace route and 50% lower
GHG for CEM III than CEM II/A cement, but facility propagation is blocked
until quantities are disclosed. The results show that open data can support
new, decision-relevant deductions when incompatible units and evidence limits
are not hidden. OpenDC-LCA complements rather than replaces openLCA or
Brightway by supplying the cooling-specific engineering, evidence lineage, and
claim governance needed for reproducible comparative research.

**Keywords:** data center; cooling; life-cycle assessment; PUE; immersion
cooling; liquid cooling; reproducibility; open-source software

## 1. Introduction and literature review

### 1.1. Cooling is becoming a lifecycle design decision

Data-center electricity demand is increasing with cloud and artificial-
intelligence workloads even as energy per computation improves [14,15].
Simultaneously, processor heat flux and rack power density are moving beyond
the practical envelope of conventional air cooling. Cold plates transfer heat
from selected high-power devices to a liquid loop; single-phase immersion
submerges the server in a dielectric liquid; and two-phase immersion uses
boiling and condensation. Reviews document substantial differences in heat-
transfer coefficient, allowable chip temperature, parasitic power, heat-
rejection design, water use, maintainability and deployment maturity
[16,17]. Experimental work further shows that cooling can affect clock
frequency and compute density, meaning that equal IT electricity or equal
server count may not represent equal service [18,19].

These interactions make a cooling comparison fundamentally different from a
component efficiency comparison. A design that lowers fan energy can require
tanks, cold plates, coolant distribution units, pumps, piping or fluorinated
fluid. A design that permits overclocking may deliver more virtual cores but
alter power, server count and lifetime. A design that eliminates evaporative
cooling can reduce onsite water while changing electricity-mediated water.
Consequently, the comparison must connect thermal performance, facility
operation, equipment and fluid production, replacement, end of life, grid
conditions and a functionally equivalent computation unit.

### 1.2. What existing data-center LCAs establish

Early screening LCA work showed that operational metrics such as power usage
effectiveness (PUE) are insufficient because interventions can transfer
burdens between operation, construction and equipment production [20].
Facility-level studies subsequently quantified the importance of electricity,
servers, buildings and cooling systems. Siddik, Shehabi and Marston mapped the
energy, carbon and water footprint of U.S. data centers and demonstrated that
location changes the trade-off between energy- and water-related objectives
[21]. Ristic et al. separated onsite water from electricity-supply-chain water
and emphasized the uncertainty of water factors [22]. Product-focused work
used manufacturer inventories to assess the manufacturing of a cooling device
across multiple environmental categories [23], while Wenzel et al. compared
LCA with material-flow, exergy and life-cycle-exergy approaches for a
data-center cooling tower [24].

Alissa et al. provided the most comprehensive public comparison of air,
cold-plate, single-phase immersion and two-phase immersion cooling at
hyperscale [1]. Their cradle-to-grave model included buildings, supporting
equipment, servers, racks or tanks, cables, fluids, use-phase electricity and
water, replacements and end of life. Crucially, they used Vcore-year rather
than facility area or IT energy, allowing cooling-enabled overclocking and
packing density to enter the functional unit. The released results showed
15-21% GHG, 15-20% primary-energy and 31-52% blue-water reductions relative
to air cooling, depending on architecture and electricity case. The study also
released normalized component results, detailed equations and a pedigree
assessment, creating an unusually strong basis for independent secondary
analysis [2].

Recent work reinforces two conclusions. First, grid decarbonization and
cooling efficiency are complementary rather than interchangeable; improving
one can shift burdens or expose categories that the other does not address
[25]. Second, as operational electricity becomes cleaner, manufacturing and
replacement of servers and electronics become proportionally more important.
ICT LCAs report large embodied impacts and methodological dispersion among
products [26,27]. These results make data quality—not only model
completeness—a design concern.

### 1.3. Water, time and geography remain weakly connected

Blue-water consumption is a volume; water-scarcity impact depends on where and
when that volume is consumed. The AWARE consensus method characterizes
remaining water availability and its uncertainty [28,29]. Yet data-center
studies often combine onsite evaporation and power-sector water at annual,
national resolution, or use watershed boundaries without scarcity factors.
Likewise, annual-average PUE hides part-load, weather, humidity, economizer
availability and heat-rejection behavior. Hourly cooling studies show that
energy and onsite/source-water rankings can change by season and climate
[30,31]. A transferable cooling LCA therefore requires both a temporal
performance model and a geographically matched impact model; neither can be
substituted by a site name alone.

### 1.4. General LCA software does not close the domain gap

openLCA and Brightway provide transparent process-network calculation,
inventory exchange and life-cycle impact assessment [3,32]. Commercial tools
and databases provide additional curated processes. These engines are
necessary, but they do not determine whether two cooling systems deliver
equivalent computation, whether a measured performance surface covers all
operating hours, how reliability changes replacement burden, or whether
synthetic values may support a public comparative claim. Nor does importing a
dataset guarantee compatible geography, reference flow, allocation, system
model or impact method.

The literature therefore leaves six connected bottlenecks:

1. released totals are not readily updateable when foreground quantities,
   background mappings or licensed processes are unavailable;
2. annual-average results obscure grid, climate and part-load transferability;
3. Vcore-year, IT MWh, server-year, rack and kilogram-of-material units are
   frequently discussed together without a formal conversion;
4. old or proxy electronics, support-equipment and fluid inventories become
   more influential under grid decarbonization;
5. pedigree matrices describe weakness but do not identify which weak data
   most affect the decision; and
6. general LCA tools lack a cooling-specific evidence and comparative-claim
   contract.

### 1.5. Objectives and contribution

This work addresses those bottlenecks with an open, evidence-governed domain
layer rather than another background database or general LCA engine. The
objectives are to:

1. preserve source identifiers, functional units, transformations and evidence
   status across heterogeneous cooling evidence;
2. connect static lifecycle models to measured load-weather performance,
   replacement and general-purpose LCA inventories;
3. independently reconstruct the released Microsoft/WSP results and use them
   with public data to derive location-dependent rankings and burden shifts;
4. combine contribution magnitude with released pedigree scores to prioritize
   the next experiments and inventories; and
5. prevent numerical outputs from being communicated beyond the evidence that
   supports them.

## 2. Framework and methods

### 2.1. Software and evidence architecture

Figure 1 summarizes the OpenDC-LCA workflow. Evidence may originate from
published LCA results, public inventories, grid and climate datasets,
laboratory measurements, or simulations. Each source record preserves its
provider, persistent identifier, version, geography, reference year, declared
unit, system boundary, license or redistribution constraint, evidence status,
and local checksum. Harmonization is performed before calculation rather than
after results are generated. Scenario JSON and performance CSV files remain
human-readable and can be processed through the command line, a stable Python
API, or a local graphical interface. All interfaces call the same validated
calculation engine.

![Figure 1. OpenDC-LCA evidence-to-decision architecture. The evidence atlas identifies the numerical role and limits of each downloaded source; the harmonization spine preserves provenance, functional unit, bounded transformations, uncertainty and evidence status; decision-facing outputs expose arithmetic reconstruction, geographic crossover conditions, data-improvement priorities and the next experimental or inventory need.](figures/figure0_opendc_lca_workflow.svg)

The framework is implemented in Python 3.10 or later and distributed under the
MIT License [4]. Version 1.1 exposes validated scenario analysis,
performance-map summarization, scientific audit functions, report generation,
a local browser-based GUI, complete openLCA JSON-LD process exchange, and
Brightway database-write mappings. The GUI binds to the local host by default
and does not alter the data model or calculation path.

### 2.2. Goal, functional unit, and system boundary

The present functional unit is one MWh of electricity delivered to IT equipment
(`it_mwh`). This denominator is valid only when the alternatives provide
equivalent computational service, utilization, reliability, and hardware life.
If cooling changes compute performance, throttling, server configuration, or
replacement, an IT-energy denominator alone is insufficient and absolute
results plus a service-based unit should be reported.

The default `cooling_system_cradle_to_grave` boundary includes cooling and
heat-rejection equipment, fluids, represented maintenance and replacement,
operation, and end of life. A `facility_cradle_to_grave` option can include
building, electrical, and IT assets. Common systems may be excluded only when
their quantities, performance, lifetime, and end-of-life treatment are
unchanged between alternatives. Location-based and market-based electricity
results are kept separate. On-site water consumption and electricity
supply-chain water are also reported separately.

### 2.3. Static energy and lifecycle calculations

For IT capacity \(P_\mathrm{IT}\), capacity factor \(u\), and study duration of
one year, annual IT electricity is

\[
E_\mathrm{IT}=P_\mathrm{IT}u(8760).
\tag{1}
\]

Annual facility electricity is

\[
E_\mathrm{facility}=E_\mathrm{IT}\,\mathrm{PUE}.
\tag{2}
\]

For an operational impact factor \(EF_k\) for category \(k\), the operational
impact normalized by delivered IT electricity is

\[
I_{k,\mathrm{op}}=EF_k\,\mathrm{PUE}.
\tag{3}
\]

Equipment production and end-of-life burdens may be annualized with a discrete
replacement model:

\[
I_{k,\mathrm{eq}} =
\sum_i
\frac{q_i\left\lceil L_s/L_i\right\rceil
\,\left(I_{k,i}^{\mathrm{prod}}+I_{k,i}^{\mathrm{EOL}}\right)}
{L_s},
\tag{4}
\]

where \(q_i\) is component quantity, \(L_s\) is the study period, and \(L_i\)
is component service life. A linearized option is retained for screening.
Negative end-of-life factors are permitted only for explicitly documented
recovery or substitution credits.

For a cooling fluid with initial mass \(m_0\), facility life \(L_f\), annual
loss \(m_\mathrm{loss}\), production factor \(I_k^\mathrm{fluid}\), and direct
GWP \(GWP_\mathrm{direct}\),

\[
m_\mathrm{prod,annual}=\frac{m_0}{L_f}+m_\mathrm{loss},
\tag{5}
\]

\[
I_{k,\mathrm{fluid}}=m_\mathrm{prod,annual}I_k^\mathrm{fluid},
\qquad
GHG_\mathrm{direct}=m_\mathrm{loss}GWP_\mathrm{direct}.
\tag{6}
\]

### 2.4. Multi-source evidence synthesis

The Microsoft/WSP normalized GHG workbook reports use-phase and embodied
contributions for a U.S. grid case and a 100% renewable case. To test
geographic transferability without asserting access to the proprietary
background model, we used an affine re-basing. For technology \(j\), eGRID
state \(s\), and the generation-weighted national eGRID factor
\(EF_\mathrm{US}\),

\[
I_{j,s}=I_{j,\mathrm{RE}}+
\left(I_{j,\mathrm{grid}}-I_{j,\mathrm{RE}}\right)
\frac{EF_s}{EF_\mathrm{US}}.
\tag{7}
\]

The published grid and renewable endpoints are therefore reproduced at ratios
one and zero, respectively. This is a screening transformation, not a claim
that all upstream electricity impacts scale with direct eGRID CO2e. State
records with missing or nonpositive generation were excluded. The crossover
between technologies \(a\) and \(b\) follows by equating the two affine
relationships:

\[
r^*=
\frac{I_{b,\mathrm{RE}}-I_{a,\mathrm{RE}}}
{\left(I_{a,\mathrm{grid}}-I_{a,\mathrm{RE}}\right)
-\left(I_{b,\mathrm{grid}}-I_{b,\mathrm{RE}}\right)},
\qquad EF^*=r^*EF_\mathrm{US}.
\tag{8}
\]

To translate the released pedigree matrix into a research priority, each
component's mean grid-case GHG contribution share \(\bar{s}_c\) was multiplied
by its normalized mean pedigree weakness. With pedigree score \(q=1\) best
and \(q=5\) worst,

\[
P_c=\bar{s}_c\frac{\bar{q}_c-1}{4}.
\tag{9}
\]

\(P_c\) is a transparent screening diagnostic, not a formal expected value of
information. It ranks data that are simultaneously consequential in the
released model and weak according to the released assessment.

Boavizta records were filtered to `Datacenter/Server` products with total GHG,
manufacturing share and lifetime. Manufacturing GHG was calculated as total
product GHG multiplied by the reported manufacturing share and was not mixed
with the Microsoft Vcore-year results. ÖKOBAUDAT A1-A3 processes were compared
within matched product families using \(100(1-I_\mathrm{alt}/I_\mathrm{base})\).
These per-kilogram reductions were not propagated to a facility because the
necessary architecture-specific material quantities are not public.

### 2.5. Performance-map and temporal integration

Each performance-map row records architecture, test identifier, IT load, heat
removed, coolant temperatures, flow, pressure drop, pump power, fan power, CDU
power, heat-rejection power, on-site water rate, dry- and wet-bulb temperature,
duration, measurement uncertainty, and source identifier. Aggregate metrics are
energy-weighted rather than arithmetic averages of ratios.

The measurement-ready interface uses a complete rectangular surface over IT
load \(P\) and ambient dry-bulb temperature \(T\). For a query point inside one
cell of the measured grid, cooling power is evaluated by bilinear interpolation:

\[
Q_c(P,T) =
(1-\alpha)(1-\beta)Q_{11}
+\alpha(1-\beta)Q_{21}
+(1-\alpha)\beta Q_{12}
+\alpha\beta Q_{22},
\tag{10}
\]

where \(\alpha=(P-P_1)/(P_2-P_1)\) and
\(\beta=(T-T_1)/(T_2-T_1)\). The same operation is applied to on-site water
rate and declared measurement uncertainty. Queries outside the measured
domain are rejected; the software does not silently extrapolate.

For hour \(h\), partial PUE and normalized operational GHG are

\[
\mathrm{PUE}_h=1+\frac{Q_{c,h}}{P_{\mathrm{IT},h}},
\tag{11}
\]

\[
GHG_\mathrm{op}=
\frac{\sum_h E_{\mathrm{IT},h}\mathrm{PUE}_h EF_{\mathrm{grid},h}}
{\sum_h E_{\mathrm{IT},h}}.
\tag{12}
\]

The current public-data demonstration uses an annual location-based EPA eGRID
factor rather than an hourly or marginal factor. Weather observations are from
a NOAA typical meteorological year (TMY) file [5,6].

### 2.6. Uncertainty, sensitivity, and scientific audit

OpenDC-LCA supports seeded Monte Carlo screening with uniform, triangular,
normal, and lognormal distributions for selected continuous parameters.
Independent sampling improves reproducibility but does not represent
correlation, systematic measurement bias, or model-form uncertainty.
One-at-a-time elasticity identifies influential inputs but should not be
interpreted as a global sensitivity analysis.

The audit operates on scientific as well as numerical requirements. It checks
source completeness, duplicate identifiers, physical values, functional unit,
boundary description, evidence status, uncertainty disclosure, and comparative
assertion intent. Synthetic or illustrative data must set the comparative
assertion to false. A public comparative claim additionally requires
decision-grade provenance, consistent boundaries, quantified uncertainty, and
independent critical review consistent with the intent of ISO 14040 and ISO
14044 [7,8]. The automated audit supports review but is not an ISO conformity
assessment.

### 2.7. Inventory interoperability and reliability

OpenDC-LCA reads complete openLCA JSON-LD process exchanges, including flow and
provider identifiers, flow type, amount, unit, direction, and quantitative
reference. The same records map to dictionaries accepted by
`bw2data.Database.write`. Conversely, an OpenDC-LCA scenario can be exported as
an annual foreground unit process containing delivered IT service, facility
electricity, on-site water, and equipment exchanges. LCIA factors are not
misrepresented as elementary flows; background providers, elementary-flow
mapping, and impact methods remain explicit tasks in openLCA or Brightway.

For a component with Weibull characteristic life \(\eta\) and shape
\(\beta\), the first-failure distribution is

\[
F(t)=1-\exp[-(t/\eta)^\beta].
\tag{13}
\]

Expected failures after as-good-as-new replacement are obtained from the
renewal equation

\[
M(t)=F(t)+\int_0^t M(t-x)\,dF(x).
\tag{14}
\]

An optional Arrhenius acceleration adjusts characteristic life from reference
temperature \(T_\mathrm{ref}\) to operating temperature \(T_\mathrm{op}\):

\[
\eta_\mathrm{op}=\eta_\mathrm{ref}/
\exp\{E_a/k_B(1/T_\mathrm{ref}-1/T_\mathrm{op})\}.
\tag{15}
\]

The calculation reports expected failures and installations, scheduled
maintenance, maintenance impacts, downtime, and unserved-IT-energy exposure.
These are expectation values. Redundancy, common-cause failure, repair queues,
and backup-system energy are outside the present model.

## 3. Data and evaluation cases

### 3.1. Microsoft/Nature released source data

The validation case used the source data and model archive released with Alissa
et al. [1,2]. The tested claim was limited: for each architecture, electricity
scenario, and impact category, did the released normalized total equal the sum
of the seven released contributions for use phase, building, server, rack or
tank, cable, supporting equipment, and cooling fluid? The audit covered four
architectures, two electricity scenarios, and three metrics, for 24 totals.
It did not independently recreate licensed background inventories,
manufacturer data, confidential bills of materials, measured PUE values, or
the complete virtual-core model.

### 3.2. EPA eGRID geographic transfer case

The metric eGRID 2023 workbook supplied state net generation (`STNGENAN`) and
state annual CO2-equivalent total-output emission rate (`STC2ERTA`) [5]. The
analysis included 50 states and the District of Columbia. The
generation-weighted mean was 348.194 kg CO2e MWh−1 and the observed state
range was 23.696-893.079 kg CO2e MWh−1. These are annual, location-based
factors; they are not marginal, hourly or market-based. The factors were used
only in the affine re-basing of Eq. (7).

### 3.3. Boavizta server product-footprint case

The downloaded U.S. Boavizta table contained 1,226 ICT product records. We
retained 48 `Datacenter/Server` records having total GHG, manufacturing share
and declared lifetime [11]. Each record retains manufacturer, product, report
date and source URL. Product carbon footprints were developed by different
manufacturers and may differ in boundary, electricity, allocation and use
assumptions. The distribution therefore measures public-factor dispersion; it
is not a like-for-like server ranking.

### 3.4. ÖKOBAUDAT construction-process case

Six selected ÖKOBAUDAT 2024-II generic A1-A3 records retained UUID, product
name, geography, reference year, unit and URL [10]. Matched comparisons were
made between galvanized steel profiles using high-scrap electric-arc-furnace
and low-scrap blast-furnace routes, and between CEM III and CEM II/A cement.
Ready-mix concrete records were registered but not compared across mass units
because their reference unit is cubic metre. No construction factor was added
to a data-center total without a foreground quantity.

### 3.5. Released pedigree assessment

The Microsoft/WSP workbook contains five scores for each of nine component
groups: reliability, completeness, temporal correlation, geographical
correlation and technological correlation. Scores range from 1 (best) to 5
(worst). Forty-five component-criterion records were parsed with their full
released rationales and combined with mean grid-case GHG contribution shares
using Eq. (9).

### 3.6. Climate and measurement-surface software cases

NOAA TMY data for the station nearest Fayetteville supplied 8,760 hourly
weather observations [6]. The public preview combined these observations with
explicit piecewise-linear temperature-PUE hypotheses. Complete air-cooled and
direct-to-chip load-temperature surfaces were also generated as synthetic
fixtures to test input validation, bilinear interpolation, uncertainty bounds,
hourly workload-weather alignment and annual aggregation. These curves and
surfaces are not measurements.

Both datasets carry `evidence_status = synthetic`, and the machine-readable
output sets `comparative_claim_allowed = false`. Their difference is a software
test, not a finding about cooling technologies.

### 3.7. Registered but not numerically combined evidence

The source registry also documents USLCI v1.2026-06.0, ÖKOBAUDAT 2024-II,
seven NREL hydrogen datasets accessed through GLAD and the Federal LCA
Commons, and USGS watershed data [9,12,13]. These sources establish potential
inputs for equipment, backup power and water context.
The seven GLAD archives can now be read as complete openLCA JSON-LD inventories
and mapped to Brightway; the `.zolca` USLCI backup must first be exported from
openLCA as portable JSON-LD. Registration or successful exchange does not make
datasets automatically compatible;
geography, reference year, unit, product system, impact method, and allocation
must be harmonized for each study. No numerical LCIA result was calculated
from GLAD or USLCI because providers and characterization methods have not yet
been linked. The USGS HU12 archive supplies watershed boundaries, not water
consumption or AWARE factors, and therefore cannot support a scarcity result.

## 4. Results

### 4.1. Exact reconstruction of released normalized totals

All 24 Microsoft/Nature released totals were reconstructed by summing the seven
released contribution categories. The maximum absolute disagreement was
1.42 × 10⁻¹⁴ percentage points, consistent with floating-point representation.
Figure 2 summarizes the grid-scenario reductions relative to air cooling.

![Figure 2. Reconstructed reductions relative to the air-cooled case for the grid scenario in the released Microsoft/Nature source data. Values are derived from published normalized component contributions and validate arithmetic consistency, not proprietary background inventories or foreground bills of materials.](figures/figure1_microsoft_grid_reductions.svg)

For primary energy, the released data gave reductions of 14.98%, 15.33%, and
20.05% for cold plate, one-phase immersion, and two-phase immersion,
respectively. Corresponding GHG reductions were 15.18%, 16.41%, and 20.66%.
Blue-water reductions were larger: 30.64%, 44.94%, and 47.88%. Under the
released 100% renewable scenario, the normalized GHG results were substantially
lower for all architectures, while the relative ranking and contribution mix
remained dependent on embodied and non-electricity terms.

### 4.2. Grid intensity changes the cold-plate/one-phase ranking

Figure 3 applies Eq. (7) to the 51 eGRID state/DC records. The modeled
cold-plate and one-phase totals intersect at 60.8 kg CO2e MWh−1, within the
observed 23.7-893.1 kg CO2e MWh−1 state range. Cold plate was lower than
one-phase immersion only for Vermont (23.7 kg CO2e MWh−1); one-phase was lower
for the other 50 records. At the Arkansas factor (452.9 kg CO2e MWh−1),
one-phase was lower than cold plate by 0.617 kg CO2e Vcore−1 yr−1. Two-phase
immersion remained the lowest-GHG architecture in all 51 re-based cases under
the released assumptions.

![Figure 3. Screening re-basing of the released Microsoft/WSP GHG contributions across EPA eGRID 2023 state total-output intensities. The vertical dashed line marks the cold-plate/one-phase crossover near 61 kg CO2e MWh−1. Lines connect state scenarios and do not represent a dynamic grid trajectory. Two-phase immersion remains lowest under the released foreground assumptions.](figures/figure2_grid_crossover.svg)

The result has two implications. First, the statement that one liquid-cooling
architecture is categorically preferable does not follow from a national-
average case: at least one pair changes order within contemporary U.S. grids.
Second, grid intensity is not the only determinant. Two-phase immersion
remained lowest because the released model combined lower use-phase burden
with Vcore-normalized server and building effects. This ranking should not be
transferred to fluids, server designs or regulations outside the released
foreground assumptions.

### 4.3. Decarbonization transfers attention from operation to hardware

At the high end of the eGRID state range, embodied contributions were
approximately 4.0-4.2% of total GHG across architectures. At the lowest state
factor they increased to 56.9-58.2%. Thus, grid decarbonization does not make
cooling architecture irrelevant; it changes the evidence required to judge it.
PUE and IT power dominate high-carbon locations, whereas server quantity,
server lifetime, overclocking, electronics manufacturing and replacement
become co-dominant on low-carbon grids.

The released endpoints illustrate the same transition. In the grid case, use
phase contributed approximately 90% of mean GHG. In the renewable case, the
absolute use-phase term fell sharply while the embodied server terms were
unchanged. An operational-only comparison can therefore be directionally
useful on a carbon-intensive grid but becomes increasingly incomplete as
electricity decarbonizes.

### 4.4. Contribution-weighted pedigree scores identify the next evidence

The released pedigree assessment alone assigns the weakest average score to
networking equipment (3.6/5), followed by storage servers (2.8/5). Weakness
alone, however, would prioritize a small contributor. Multiplying weakness by
mean GHG contribution changed the order (Figure 4). Use phase ranked first
because its 90.3% mean contribution outweighed a relatively good 1.4/5
pedigree score. Storage, networking and compute-server evidence formed the
next tier with nearly equal priority indices (0.0127-0.0129).

![Figure 4. Contribution-weighted evidence-improvement priority derived from the released Microsoft/WSP grid-case GHG contributions and pedigree matrix. The diagnostic multiplies mean contribution share by normalized pedigree weakness; it is a transparent screening rank, not a formal expected value of information.](figures/figure3_data_priority.svg)

This result separates two research programs. Improving measured PUE, IT power,
utilization and water response has the greatest present consequence for
grid-powered facilities. Improving server inventories—especially storage and
networking proxies—becomes the next priority and grows in importance on
cleaner grids. Fluid data remain important for toxicity, regulation, leakage
and feasibility even though their released climate contribution is small; the
priority index is not a complete environmental, health and safety ranking.

### 4.5. Public product and construction data quantify uncertainty and leverage

The 48 usable Boavizta server records yielded manufacturing GHG values from
465 to 2,503 kg CO2e per server, with a median of 1,215 kg CO2e and an
interquartile range of 1,146-1,337 kg CO2e (Figure 5). Annualized by the
declared four-year lifetime, the median was 304 kg CO2e server−1 yr−1. The
approximately 5.4-fold full range is large relative to many reported cooling
savings. Because manufacturer PCFs differ in method and configuration, this
range is an evidence envelope rather than a product ranking.

![Figure 5. Distribution of manufacturing GHG for 48 Boavizta `Datacenter/Server` records having total product GHG and manufacturing share. Dashed lines show the 25th percentile, median and 75th percentile. Heterogeneous manufacturer methods and product configurations preclude a product ranking.](figures/figure4_server_epd_distribution.svg)

The selected ÖKOBAUDAT records identified large construction procurement
levers (Figure 6). High-scrap electric-arc-furnace galvanized steel had 59.9%
lower A1-A3 GHG, 47.9% lower nonrenewable primary energy and 52.0% lower
freshwater use than the selected low-scrap blast-furnace profile. CEM III
cement had 49.8% lower GHG, 12.1% lower nonrenewable primary energy and 23.5%
lower freshwater use than CEM II/A. Their facility significance cannot be
calculated without architecture-specific material quantities.

![Figure 6. Selected ÖKOBAUDAT 2024-II A1-A3 GHG factors for baseline and alternative steel and cement routes. The figure identifies unit-process procurement leverage; it does not quantify a data-center reduction because foreground quantities are unavailable.](figures/figure5_material_levers.svg)

### 4.6. Temporal and measurement pathways remain validation cases

The Fayetteville TMY and assumed temperature-PUE curves produced annual mean
PUE values of 1.0907, 1.0529, 1.0406 and 1.0352 for air, cold plate,
one-phase and two-phase cases, respectively. These are hypotheses, not
technology findings. Likewise, the synthetic measurement surfaces processed
8,760 hourly observations, rejected extrapolation and propagated declared
point uncertainty. Their role is to specify exactly how reviewed laboratory
data will enter the lifecycle calculation. The resulting climate and surface
figures are retained as Supplementary Figures rather than core evidence.

### 4.7. Capability and evidence matrix

Table 1 summarizes the implemented functions and the evidence required for
their defensible use. The distinguishing contribution is the continuity from
data registration through physics-informed temporal integration to an explicit
claim gate. Numerical outputs remain available for inspection even when the
audit blocks a comparative conclusion.

**Table 1. OpenDC-LCA capability and evidence matrix.**

| Capability | Input | Method | Output | Evidence requirement | Status |
|---|---|---|---|---|---|
| Source registration | Provider, ID, version, geography, unit, boundary, license | Schema validation and checksum manifest | Traceable record | Complete metadata and redistribution review | Implemented |
| Static lifecycle screening | Energy, PUE, grid factors, equipment, fluids, water | Annual energy balance and lifecycle annualization | Absolute and normalized impacts | Compatible unit and boundary | Implemented |
| Temporal operation | Hourly weather, workload, grid and cooling response | Hourly alignment and integration | PUE, energy, water, operational GHG | Full coverage and accounting basis | Implemented |
| Performance surface | Load-temperature grid, uncertainty, source IDs | Bounded bilinear interpolation | Hourly cooling response | Reviewed measurements; no extrapolation | Implemented |
| Inventory exchange | openLCA JSON-LD processes or OpenDC-LCA scenario | Exchange-preserving import/export and Brightway mapping | Foreground process network | Flow, provider, unit, system-model and LCIA compatibility review | Implemented |
| Reliability | Weibull/Arrhenius parameters, maintenance and downtime | Renewal equation and lifecycle annualization | Expected failures, replacements, downtime and impacts | Empirical failure model and uncertainty | Implemented |
| Uncertainty and sensitivity | Distributions, seed and perturbations | Monte Carlo and elasticity | Intervals and ranked drivers | Distribution and correlation review | Screening |
| Scientific claim gate | Scenario, sources, evidence status and intent | Automated blockers and warnings | Reviewable findings | Independent critical review for public claims | Implemented |
| Access | JSON or CSV | Shared engine through CLI, API and local GUI | JSON, tables, figures and reports | Same model version across interfaces | Implemented |

## 5. Discussion

### 5.1. The technology ranking is conditional, not universal

The geographic screening exposes a decision boundary that is hidden by a
single national-average scenario. Cold plate and one-phase immersion cross at
60.8 kg CO2e MWh−1: a small difference in their non-use-phase terms reverses
the ordering once grid emissions are sufficiently low. The practical
take-home message is not that Vermont should select cold plates. The affine
transfer holds the released foreground model fixed and changes only the
electricity-dependent term. Rather, the finding demonstrates that a cooling
ranking must be reported together with its grid range, foreground assumptions
and crossover conditions. The same principle applies to climate, workload,
water stress and equipment lifetime.

Two-phase immersion did not cross another architecture in the tested state
range. That result is stronger within the released model but is not universal.
It inherits the paper's assumptions concerning server count and performance,
fluid production and loss, cooling-system boundaries, equipment lifetime and
regulatory feasibility. A robust comparative claim should therefore report
both the observed no-crossover range and the untested assumptions that could
create one.

### 5.2. Decarbonization changes the research question

At the highest observed state grid intensity, embodied terms supplied only
about 4% of the re-based total; at the lowest, they supplied 57-58%. This
transition changes what constitutes adequate evidence. On a carbon-intensive
grid, improved PUE, reduced IT power and water-aware heat rejection are the
largest near-term levers. On a low-carbon grid, the comparison becomes
increasingly sensitive to useful computation per server, server count,
manufacturing, lifetime and replacement. Operational efficiency and embodied
impact are therefore not competing narratives but successive constraints along
a decarbonization pathway.

The 5.4-fold range in public Boavizta server manufacturing footprints shows why
a single generic server factor is inadequate for low-carbon scenarios. It
does not establish a probability distribution or rank products, because the
records are heterogeneous. It does establish scale: public foreground
dispersion can exceed the differences among cooling options. Reporting a
cooling saving to high precision while proxying the servers with one legacy
factor creates false confidence. Product-specific bills of materials,
functional performance and harmonized product-carbon-footprint rules are thus
central research data, not secondary documentation.

### 5.3. Evidence priority links LCA to experiments and procurement

The contribution-weighted pedigree analysis provides an actionable measurement
sequence. Present grid-powered comparisons should first improve hourly IT and
cooling electricity, utilization, part-load parasitics and on-site water
response. Storage, networking and compute-server inventories form the next
evidence tier. As grids decarbonize, this second tier moves upward. This
ranking is intentionally transparent and can be replaced by formal value-of-
information analysis when parameter distributions and decision losses become
available.

For electronics-cooling laboratories, the immediate contribution is a shared
performance-map protocol spanning heat load, ambient and coolant temperature,
flow, pressure drop, pump and fan power, heat-rejection power, water, duration,
uncertainty and calibration lineage. A complete bounded surface permits
annual integration without extrapolation. Comparative experiments should use
a common heat-load emulator and heat-rejection boundary and should separate
IT-integral fan power from facility parasitics. Those measurements would
replace the present synthetic fixtures through the same data contract.

The ÖKOBAUDAT comparison identifies a complementary procurement pathway.
Selected lower-impact steel and cement routes reduced cradle-to-gate GHG by
approximately 50-60% per kilogram. Whether this matters more than cooling
equipment or server replacement depends on an architecture-specific bill of
quantities, which is currently absent. The appropriate next step is therefore
not to apply the percentages to an assumed facility, but to obtain reviewed
quantities and preserve product geography, unit and module boundary.

### 5.4. Role relative to openLCA and Brightway

OpenDC-LCA is not a replacement for openLCA or Brightway [3,32]. Those
platforms manage process networks, databases and impact assessment. The
contribution here is a data-center-specific foreground and evidence layer:
cooling-performance surfaces, hourly operation, reliability and replacement,
functional-unit controls, source lineage and a comparative-claim gate. The
interoperability functions preserve identifiers and expose missing providers
or impact methods rather than silently treating an imported archive as a
complete product system.

This separation also explains why the downloaded GLAD hydrogen inventories and
USLCI database were not forced into the reported totals. They are relevant to
backup power and equipment supply chains, but numerical combination without
provider linking, a shared system model and a selected LCIA method would create
an apparently comprehensive but irreproducible result. Evidence registration,
successful exchange and impact calculation are three distinct stages.

### 5.5. Limitations and decision-grade next steps

The state analysis is a screening re-basis between two released endpoints, not
a 51-state process LCA. It uses annual location-based eGRID factors and omits
hourly or marginal emissions, procurement contracts and transmission effects.
The exact reconstruction verifies released arithmetic, not licensed ecoinvent
or LCA for Experts inventories, confidential bills of materials or measured
PUE. The Boavizta sample mixes manufacturers and methods; the ÖKOBAUDAT factors
are German product-stage proxies without data-center quantities. The USGS file
contains watershed geometry rather than withdrawal, consumption or scarcity
characterization, so no watershed-level water claim is made.

The temporal examples use TMY weather and declared hypothetical or synthetic
performance curves. They exclude humidity-sensitive heat rejection, extreme
events and correlated measurement or model-form error. Reliability results are
expectations from Weibull renewal and optional Arrhenius acceleration; they
exclude redundancy, dependent failures and repair queues. Vcore-year improves
on rack- or facility-level comparisons but does not fully represent useful
computation, workload quality or rebound effects. Automated checks cannot
replace an ISO-aligned critical review.

Four additions would enable a decision-grade multi-location comparison:
(i) reviewed architecture-specific performance surfaces and water measurements;
(ii) server, network, storage, facility and cooling-system bills of quantities
with uncertainty and lifetime data; (iii) hourly electricity and watershed
scarcity characterization; and (iv) harmonized background product systems in
openLCA or Brightway. Dr. Nutter's independent review should assess the
recorded methodological decisions, dataset mappings and claim-gate findings as
a coherent package before public comparative assertions are made.

## 6. Conclusions

OpenDC-LCA converts heterogeneous cooling, grid, server, construction and data-
quality evidence into conditional, auditable lifecycle comparisons. It exactly
reconstructed 24 released Microsoft/Nature totals and then exposed a result
that a single reference scenario cannot show: cold plate and one-phase
immersion cross near 60.8 kg CO2e MWh−1 within the observed U.S. state range.
Across that range, the embodied share rose from about 4% to 57-58%, shifting
the limiting evidence from operational electricity toward servers and
replacement. Forty-eight public server records spanned 465-2,503 kg CO2e of
manufacturing emissions, while selected lower-impact steel and cement routes
showed approximately 50-60% cradle-to-gate GHG leverage per kilogram.

These findings support three conclusions. First, cooling rankings should be
reported as decision surfaces with crossover conditions, not universal league
tables. Second, decarbonized operation makes server performance, manufacturing,
lifetime and architecture-specific material quantities first-order LCA data.
Third, contribution-weighted data quality can convert an LCA into a prioritized
experimental and data-acquisition program. OpenDC-LCA operationalizes these
principles through traceable source registration, temporal performance maps,
reliability, openLCA/Brightway exchange and machine-readable claim gates. The
remaining barrier to a public decision-grade benchmark is evidence: harmonized
bills of quantities, measured operating surfaces, time- and watershed-resolved
factors, and independent critical review.

## Data and code availability

OpenDC-LCA version 1.1 source code, examples, documentation, tests, and derived
paper tables and figures are available at
https://github.com/UARK-NED3/OpenDC-LCA. Provider-native raw files remain local
when redistribution permission has not been established. Released
Microsoft/Nature model files are available from Zenodo [2]. EPA eGRID and NOAA
TMY data are available from their respective public portals [5,6].

## Author contributions

**Draft taxonomy for confirmation:** Han Hu: conceptualization, methodology,
software supervision, thermal-management domain analysis, writing, and
visualization. Darin W. Nutter: LCA methodology review, validation, critical
review, and manuscript revision. Contributions must be confirmed before
submission.

## Competing interests

The authors must complete and approve the journal-specific competing-interest
statement before submission.

## Acknowledgments

Funding, facility, student-contributor, and data-provider acknowledgments must
be confirmed before submission.

## References

1. Alissa, H. et al. Using life cycle assessment to drive innovation for
   sustainable cool clouds. *Nature* **641**, 331-338 (2025).
   https://doi.org/10.1038/s41586-025-08832-3
2. Alissa, H. et al. Data and model archive for “Using life cycle assessment
   to drive innovation for sustainable cool clouds.” Zenodo record 14268168
   (2024). https://doi.org/10.5281/zenodo.14268168
3. GreenDelta. openLCA: open source life cycle assessment software.
   https://www.openlca.org/
4. UARK-NED3. OpenDC-LCA version 1.0.0.
   https://github.com/UARK-NED3/OpenDC-LCA
5. U.S. Environmental Protection Agency. Emissions & Generation Resource
   Integrated Database (eGRID), 2023 detailed data.
   https://www.epa.gov/egrid/detailed-data
6. National Centers for Environmental Information. Typical Meteorological
   Year data. https://www.ncei.noaa.gov/access/typical-meteorological-year/
7. International Organization for Standardization. ISO 14040:2006,
   Environmental management - Life cycle assessment - Principles and
   framework.
8. International Organization for Standardization. ISO 14044:2006,
   Environmental management - Life cycle assessment - Requirements and
   guidelines.
9. National Renewable Energy Laboratory. U.S. Life Cycle Inventory Database,
   version 1.2026-06.0. Federal LCA Commons.
   https://www.lcacommons.gov/
10. Bundesinstitut für Bau-, Stadt- und Raumforschung. ÖKOBAUDAT 2024-II.
    https://www.oekobaudat.de/
11. Boavizta. BoaviztAPI data repository.
    https://github.com/Boavizta/boaviztapi
12. United Nations Environment Programme. Global LCA Data Access network.
    https://www.globallcadataaccess.org/
13. U.S. Geological Survey. Watershed Boundary Dataset.
    https://www.usgs.gov/national-hydrography/watershed-boundary-dataset
14. Masanet, E., Shehabi, A., Lei, N., Smith, S. & Koomey, J. Recalibrating
    global data center energy-use estimates. *Science* **367**, 984-986
    (2020). https://doi.org/10.1126/science.aba3758
15. International Energy Agency. Data centres and data transmission networks.
    https://www.iea.org/energy-system/buildings/data-centres-and-data-transmission-networks
16. Khalaj, A. H. & Halgamuge, S. K. A review on efficient thermal management
    of air- and liquid-cooled data centers. *Applied Energy* **205**, 1165-1184
    (2017). https://doi.org/10.1016/j.apenergy.2017.08.037
17. Xu, S. et al. Thermal management and energy consumption in air, liquid,
    and free cooling systems for data centers: a review. *Energies* **16**,
    1279 (2023). https://doi.org/10.3390/en16031279
18. Kanbur, B. B. et al. A review of immersion cooling for data centers.
    *International Journal of Refrigeration* **118**, 290-301 (2020).
19. Ramakrishnan, B. et al. An experimentally validated model of immersion
    cooling for overclocked servers. *IEEE Transactions on Components,
    Packaging and Manufacturing Technology* **11**, 1313-1324 (2021).
    https://doi.org/10.1109/TCPMT.2021.3106026
20. Whitehead, B., Andrews, D., Shah, A. & Maidment, G. Assessing the
    environmental impact of data centres. Part 1: background, energy use and
    metrics. *Building and Environment* **82**, 151-159 (2014).
21. Siddik, M. A. B., Shehabi, A. & Marston, L. The environmental footprint
    of data centers in the United States. *Environmental Research Letters*
    **16**, 064017 (2021). https://doi.org/10.1088/1748-9326/abfba1
22. Ristic, B., Madani, K. & Makuch, Z. The water footprint of data centers.
    *Sustainability* **7**, 11260-11284 (2015).
    https://doi.org/10.3390/su70811260
23. Isler-Kaya, G., Colpan, C. O. & Kizilkan, O. Life cycle assessment of a
    data center cooling system. *Energy and Buildings* **295**, 113006 (2023).
    https://doi.org/10.1016/j.enbuild.2023.113006
24. Wenzel, H. et al. Comparative life cycle assessment of wet cooling towers.
    *Journal of Industrial Ecology* **27** (2023).
    https://doi.org/10.1111/jiec.13396
25. Cleaner grid or smarter cooling? A life cycle perspective on data center
    cooling strategies. *Cleaner Engineering and Technology* (2025).
    https://doi.org/10.1016/j.cles.2025.100223
26. Boyd, S. B., Horvath, A. & Dornfeld, D. Life-cycle assessment of
    computational logic produced from 1995 through 2010.
    *Environmental Science & Technology* **47**, 2947-2954 (2013).
    https://doi.org/10.1021/es303012r
27. Malmodin, J. & Lundén, D. The energy and carbon footprint of the global
    ICT and E&M sectors 2010-2015. *Sustainability* **10**, 3027 (2018).
    https://doi.org/10.3390/su10093027
28. Boulay, A.-M. et al. The WULCA consensus characterization model for water
    scarcity footprints: assessing impacts of water consumption based on
    available water remaining (AWARE). *International Journal of Life Cycle
    Assessment* **23**, 368-378 (2018).
    https://doi.org/10.1007/s11367-017-1333-8
29. Boulay, A.-M. et al. Analysis of water use impact assessment methods.
    *Journal of Industrial Ecology* **25** (2021).
    https://doi.org/10.1111/jiec.13173
30. Life-cycle environmental assessment of progressive chiller systems for
    data centers. *Building Simulation* (2024).
    https://doi.org/10.1007/s12273-024-1167-9
31. Hourly performance and environmental assessment of data-center cooling in
    hot-arid climates. *Applied Thermal Engineering* (2025).
    https://doi.org/10.1016/j.applthermaleng.2025.126802
32. Mutel, C. Brightway: an open source framework for life cycle assessment.
    *Journal of Open Source Software* **2**, 236 (2017).
    https://doi.org/10.21105/joss.00236
