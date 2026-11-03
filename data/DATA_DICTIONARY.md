# Dataset and labels
All included sensor readings and 180 training examples are **synthetic**.
No real farms, patients, identifiers, geospatial boundaries, or forecasts are used.

## Input columns
- `plot_id`: synthetic unique identifier.
- `soil_moisture_pct`: percentage [0,100].
- `temperature_c`: Celsius [-5,60].
- `rainfall_forecast_mm`: simulated forecast [0,250].
- `growth_stage`: Germination, Tillering, Grand Growth, or Maturity.

## Training labels (not agronomic ground truth)
- `0`: NO_IRRIGATION; synthetic rule: rain >= 18 mm or moisture >= 64%.
- `2`: IRRIGATION_REVIEW; synthetic rule: moisture <= 32% and rain <= 8 mm, or moisture <= 40%, rain <= 5 mm, and temperature >= 33 C.
- `1`: MONITOR otherwise.

**Important**: The durations and thresholds are placeholders for teaching OS concepts, not expert recommendations.
Training data was generated with Python's fixed `random.seed(42)` in the project build generator, using 180 random samples in the stated ranges. Model evaluates on an 80/20 deterministic split, then fits on all 180 for output predictions. Accuracy only measures agreement with the synthetic rule on held-out synthetic rows.
