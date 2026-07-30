# Load-temperature performance-surface protocol

## Purpose

Version 0.6 defines the measurement interface needed to replace the
hypothesis-based PUE curves in the hourly research preview.

## Required test grid

Each architecture dataset must contain every combination of declared IT load
and ambient dry-bulb temperature. A practical initial design is:

- IT load: 25%, 50%, 75%, and 100% of rated load;
- ambient or heat-rejection inlet condition: at least four values spanning the
  intended application climate;
- replicated steady-state observations at each combination; and
- clearly identified transient tests stored separately.

Wet-bulb temperature, coolant supply and return temperature, flow, pressure
drop, component electrical power, heat removed, on-site water, duration,
measurement uncertainty, and provenance are already required by the common CSV
format.

## Interpolation and validity

The reference engine uses bilinear interpolation within a complete rectangular
load-temperature grid. It does not extrapolate. A weather or workload hour
outside the measured envelope fails validation instead of silently extending
the model.

## Uncertainty

The v0.6 screening interval applies the interpolated percentage measurement
uncertainty to cooling power. This is deliberately conservative and simple.
Publication-quality analysis should retain instrument-level uncertainties,
replicate variability, parameter correlations, and model-form error.

## Evidence statuses

- `synthetic`: validates software and experimental design only;
- `measured`: traceable observations with documented calibration and QA;
- `reviewed`: measured dataset and processing reviewed for the intended claim.

Comparative environmental claims must not use `synthetic` performance maps.
