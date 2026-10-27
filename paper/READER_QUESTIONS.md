# Reader questions

This file records questions that a technical reader, facility practitioner, or life-cycle assessment reviewer may reasonably ask after reading the manuscript. The companion file provides evidence-bounded responses.

## Scope and contribution

1. What engineering decision does this paper help inform?
2. Is this paper a new comparative life-cycle assessment of data-center cooling architectures?
3. What is the paper's principal contribution beyond a review of prior data-center LCAs?
4. Why does the analysis focus on the released Microsoft and WSP workbook?
5. Does the paper present any new facility measurements or a new foreground cooling inventory?
6. Which conclusions are independently supported by the authors' calculations, and which remain numerical screens based on the released workbook?

## Model reconstruction

7. How were the 24 published total results reconstructed, and how closely do the reconstructed values match the source workbook?
8. Why do the published workbook's GTP100 and GWP100 endpoint labels require special attention?
9. What does the eGRID harmonization represent, and what does it not represent?
10. What does the Federal LCA Commons electricity calculation add beyond the eGRID comparison?
11. Why is the Federal LCA Commons result described as a partial linked-system screen rather than a full life-cycle electricity factor?
12. Why were 71 ordinary non-residual product systems used, and do they represent 71 independent data-center scenarios?

## Interpretation

13. Why does the manuscript avoid declaring a universally preferable cooling architecture?
14. What does the 1.32 percent all-block rank-robustness threshold mean?
15. Are the rank-robustness thresholds probabilities that one architecture will outperform another?
16. Why can service life, use-phase energy, and embodied impacts have different threshold values?
17. What does the analysis indicate about server hardware and construction impacts?
18. How do grid decarbonization and the selected electricity accounting boundary affect the conclusions?

## Functional equivalence

19. What is the functional unit, and why is a Vcore-year used?
20. Why is functional equivalence the central unresolved issue in comparative data-center LCAs?
21. Which measured quantities are needed before a cooling-architecture superiority claim can be made?
22. Can the framework use a common workload when servers, racks, or service levels differ?

## Facility application

23. Can this framework be applied to the Arkansas High Performance Computing Center?
24. Does the manuscript report an AHPCC energy, carbon, water, or PUE result?
25. What boundary should a facility use when its data-center load shares building infrastructure with other occupants?
26. How do PUE and a dedicated-support electricity ratio differ?
27. What minimum meter data would provide the greatest value for an operational assessment?

## Reproducibility and use

28. What code, data, and execution records are available for audit or reuse?
29. Can a reader reproduce the full foreground cooling comparison in openLCA or Brightway today?
30. What datasets or permissions are needed to extend the analysis without violating source or facility-data restrictions?
31. Is there an immutable archived release with a DOI for the exact analyzed version?
32. What are the most important next steps for research, software development, and facility engagement?

## Applied assessment

33. For a shared building that contains a data center and non-data-center occupants, how would you draw the electrical and thermal boundaries for an operational assessment?
34. Which meter locations would allow you to separate IT energy, UPS losses, dedicated cooling-support energy, and shared building energy?
35. If UPS input energy and UPS output energy are available, how would you calculate UPS losses and avoid counting the same energy twice?
36. Under what conditions could you report PUE, and when should you report a dedicated-support electricity ratio instead?
37. How would you establish whether a chilled-door retrofit changes the cooling energy required for a common HPC workload?
38. What operating measurements are needed to relate chilled-water or glycol-loop conditions to cooling energy and IT heat rejection?
39. How could supply-air, return-air, rack-inlet, and water temperatures be used to identify a potential airflow or control problem without claiming causation prematurely?
40. What time resolution, operating period, and maintenance annotations would make an initial meter campaign useful for LCA and energy analysis?
41. How would you define a functionally equivalent service for comparing a largely CPU-based rack with a GPU-intensive rack?
42. Which foreground inventory items would you request for an architecture-specific cooling LCA, and which omissions could materially change the result?
43. How would you distinguish a sensitivity range from a statistical uncertainty interval when presenting an operational scenario analysis?
44. A facility manager asks whether this framework can provide a free energy audit. What can be offered now, and what evidence is needed before reporting an audit result or investment recommendation?
45. What quality-control checks would you perform before accepting a month of interval meter data for analysis?
46. After completing the measurement campaign, what evidence would be needed to convert this transferability assessment into a defensible comparative cooling LCA?
