# Local graphical interface

Launch the zero-dependency GUI with:

```bash
opendc-lca gui
```

It opens `http://127.0.0.1:8765/` and provides:

- scenario JSON loading, validation, analysis, and audit;
- normalized GHG, primary-energy, and water KPIs;
- visible scientific-quality findings;
- performance-map CSV summaries; and
- JSON result export.

The GUI is a view over the same engine used by Python and the command line. It
does not contain separate equations or impact factors.

## Security and privacy

- The default server binds only to the local computer.
- Files are read by the browser and sent only to the local process.
- Responses are not cached.
- Requests larger than 2 MB are rejected.
- Remote binding is refused unless `--allow-remote` is supplied explicitly.

The GUI has no authentication and should not be exposed to a network. Do not
use `--allow-remote` with confidential data.

## Scientific interpretation

The GUI always returns audit findings with scenario results. A successful
calculation is not proof of functional equivalence, data quality, critical
review, or authorization for a public comparative claim.
