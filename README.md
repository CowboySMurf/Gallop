# Conductor Galloping with Bi-Stable Dampers
## Phase A: Feasibility Model

**Project:** Anti-Galloping Device Development for PRECorp Distribution Feeders
**Purpose:** Quick feasibility assessment of bi-stable damping concept
**Timeline:** 2 weeks development + analysis
**Status:** Phase A Implementation Complete

---

## Overview

This repository contains a Python-based simulation model for assessing the feasibility of bi-stable damping devices to mitigate conductor galloping on high-voltage transmission lines. The model simulates galloping oscillations on 336.4 kcmil Merlin ACSR conductors under icing conditions and evaluates the effectiveness of attached bi-stable spring devices in reducing oscillation amplitude.

### Key Features

- **Aerodynamic Forcing:** Den Hartog galloping criterion for iced conductors
- **Bi-Stable Device Mechanics:** Snap-through behavior with energy dissipation
- **Time Integration:** Adaptive RK45 solver via scipy
- **Energy Tracking:** Full energy balance monitoring
- **Parametric Studies:** Automated optimization of device count and parameters
- **Comprehensive Visualization:** Professional plots and analysis outputs

---

## Physical System

### Conductor Properties (336.4 kcmil Merlin ACSR)
- Diameter: 0.721 inches (0.0183 m)
- Mass: 0.644 lb/ft (0.958 kg/m)
- Span: 300 ft (91.44 m)
- Tension: 4000 lbs (17,792 N)

### Environmental Conditions
- Ice thickness: 0.5 inches (moderate icing)
- Wind speed: 30 mph (13.4 m/s)
- Iced diameter: 1.721 inches (0.0437 m)
- Ice shape: Asymmetric crescent (creates instability)

### Bi-Stable Devices
- Number: 2-6 devices (optimized)
- Snap threshold: 0.10-0.25 m (tunable)
- Snap force: 200 N
- Energy per snap: 15 J
- Placement: Equally spaced along span

---

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Gallop
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Dependencies:
- numpy >= 1.21.0
- scipy >= 1.7.0
- matplotlib >= 3.4.0

---

## Usage

### Quick Start

Run the complete Phase A analysis (baseline, devices, parametric studies):

```bash
python run_analysis.py
```

This will:
1. Run baseline simulation (no devices)
2. Run simulation with 4 bi-stable devices
3. Perform parametric studies (device count, snap threshold)
4. Generate all plots and save to `results/` directory
5. Create final report with recommendations

### Results Output

All results are saved to the `results/` directory:

**Plots:**
- `baseline_time_history.png` - Baseline galloping behavior
- `device_time_history.png` - Behavior with devices
- `comparison_time_history.png` - Side-by-side comparison
- `baseline_phase_portrait.png` - Phase space (baseline)
- `device_phase_portrait.png` - Phase space (with devices)
- `baseline_energy.png` - Energy evolution (baseline)
- `device_energy.png` - Energy evolution (with devices)
- `device_activity.png` - Snap event timeline and statistics
- `summary_figure.png` - Comprehensive 6-panel summary
- `parametric_num_devices.png` - Effectiveness vs device count
- `parametric_snap_threshold.png` - Effectiveness vs threshold

**Data Files:**
- `results_summary.txt` - Numerical comparison metrics
- `PHASE_A_FINAL_REPORT.txt` - Complete findings and recommendations

### Custom Simulations

Run individual simulations with custom parameters:

```python
from src import get_full_parameters, GallopingSimulation, compare_results

# Configure parameters
params = get_full_parameters(
    num_devices=5,           # Number of devices
    snap_threshold=0.18,     # Snap threshold (m)
    snap_force=250,          # Snap force (N)
    device_placement='uniform'  # Placement strategy
)

# Run baseline
baseline_sim = GallopingSimulation(params, use_devices=False)
baseline_results = baseline_sim.run_simulation(A0=0.01)

# Run with devices
device_sim = GallopingSimulation(params, use_devices=True)
device_results = device_sim.run_simulation(A0=0.01)

# Compare
comparison = compare_results(baseline_results, device_results)
```

---

## Project Structure

```
Gallop/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── run_analysis.py          # Main analysis script
├── src/
│   ├── __init__.py          # Package initialization
│   ├── parameters.py        # Physical parameter calculations
│   ├── galloping_model.py   # Core simulation engine
│   └── visualization.py     # Plotting and analysis functions
└── results/                 # Output directory (generated)
    ├── *.png                # All generated plots
    ├── results_summary.txt  # Numerical results
    └── PHASE_A_FINAL_REPORT.txt  # Final report
```

---

## Model Details

### Mathematical Formulation

The model uses a single-degree-of-freedom modal approach for the fundamental mode:

**Equation of Motion:**
```
M·d²A/dt² + C·dA/dt + K·A = Q_aero + Q_devices
```

Where:
- `A(t)` = modal amplitude (m)
- `M` = modal mass (kg)
- `C` = modal damping (N·s/m)
- `K` = modal stiffness (N/m)
- `Q_aero` = generalized aerodynamic force (N)
- `Q_devices` = generalized device forces (N)

**Aerodynamic Forcing (Den Hartog):**
```
Q_aero = F0 · [1 - α·(dA/dt)/V] · sign(dA/dt)
```

**Bi-Stable Device Forces:**
Devices snap when local displacement exceeds threshold, dissipating energy and applying impulse force.

### Assumptions and Simplifications

**Included:**
- Single span vertical oscillation (primary galloping mode)
- Aerodynamic forcing based on Den Hartog criterion
- Bi-stable device snap-through mechanics
- Energy dissipation tracking

**Simplified (Phase A only):**
- 3D motion (only vertical displacement)
- Conductor torsion
- Detailed ice shape aerodynamics
- Temperature effects
- Multiple mode shapes

---

## Success Criteria

The Phase A model evaluates feasibility based on:

✓ **Max amplitude reduction > 30%**
✓ **RMS amplitude reduction > 25%**
✓ Device snaps occur regularly (active damping)
✓ Energy dissipated > 20% of total energy

### Decision Matrix

| Reduction (%) | Assessment | Recommendation |
|--------------|------------|----------------|
| > 30% | **FEASIBLE** | Proceed to Phase B (Detailed FEA) |
| 10-30% | **MARGINAL** | Optimize parameters before Phase B |
| < 10% | **INEFFECTIVE** | Reconsider concept |

---

## Expected Results

Based on similar damping systems in literature:

**Baseline (No Devices):**
- Amplitude growth from 0.01 m to 2-4 m in 20-40 seconds
- Steady-state amplitude: 2-5 m
- Frequency: ~0.5 Hz
- Sustained limit-cycle oscillation

**With 4 Bi-Stable Devices:**
- Amplitude limited to 1-2 m
- Snap events every 2-5 seconds
- Expected reduction: 40-60%
- More irregular oscillation (disrupts resonance)

---

## Troubleshooting

### Model doesn't show galloping
- Check aerodynamic coefficient is negative (C_eff < 0)
- Ensure structural damping is very low (ζ < 0.005)
- Verify F0 calculation and units
- Try higher initial disturbance (A0 = 0.1 m)

### Numerical instability
- Reduce timestep in parameters (dt = 0.0005 s)
- Check units on all parameters
- Verify integration method settings

### Devices have no effect
- Check snap threshold isn't too high
- Verify device forces applied correctly
- Try increasing snap force or decreasing threshold
- Ensure mode shape factor included

---

## Next Steps After Phase A

### If Results Are Positive (>30% reduction):
1. ✓ Document findings in technical memo
2. → Proceed to Phase B: Detailed FEA of beam mechanics
3. → Begin conversations with universities for collaboration
4. → Consider provisional patent application
5. → Prepare budget for prototype fabrication

### If Results Are Marginal (10-30% reduction):
1. → Identify limiting factors in simulation
2. → Explore parameter optimization more thoroughly
3. → Consider hybrid approaches (devices + other methods)
4. → Evaluate cost-benefit of marginal improvement

### If Results Are Negative (<10% reduction):
1. → Analyze why concept didn't work
2. → Revisit assumptions (3D motion importance?)
3. → Consider alternative concepts
4. → Document lessons learned

---

## References

### Galloping Mechanics
- Den Hartog, J.P. (1932). "Transmission Line Vibration Due to Sleet"
- Blevins, R.D. (2001). "Flow-Induced Vibration"
- EPRI (2006). "Transmission Line Reference Book: Wind-Induced Conductor Motion"

### Bi-Stable Systems
- Virgin, L.N. (2000). "Introduction to Experimental Nonlinearity"
- Pellegrini, S.P. et al. (2013). "Bistable vibration energy harvesters"

### Application
- PRECorp Distribution Feeder Requirements
- IEEE Std 524-2016: Guide to Installation of Overhead Transmission Line Conductors

---

## Contact

**Project:** PRECorp Anti-Galloping Device Development
**Phase:** A - Feasibility Modeling
**Timeline:** 2 weeks development + analysis

For questions or collaboration inquiries, contact the project team.

---

## License

Proprietary - PRECorp Internal Development

---

## Revision History

**Version 1.0** - Initial Phase A implementation
- Complete simulation engine
- Baseline and device simulations
- Parametric studies
- Comprehensive visualization
- Automated reporting

**Status:** Ready for Phase A analysis and decision making

---

**END OF README**
