# v0.6 measurement-ready demonstration

This result proves the data path from a complete load-temperature performance
surface through hourly NOAA weather and workload integration to operational
GHG. Both performance surfaces are synthetic and have
`evidence_status = synthetic`; comparative claims are therefore blocked.

The engine performs bilinear interpolation only inside the measured grid.
Extrapolation is rejected. The reported PUE interval applies the declared
measurement uncertainty to interpolated cooling power and is a screening
interval, not a full correlated uncertainty analysis.

See the paper package Figures 4-5 and Table 5.
