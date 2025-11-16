# Codebase Architecture & Analysis Report

## Project Context
- **Repository**: Gallop (Anti-Galloping Device Development)
- **Current Branch**: `claude/reconcile-nisc-work-orders-01WY8EUYfA7vKLqUex9FK2hE`
- **Status**: Clean working tree (ready for new development)
- **Commit HEAD**: b983189 - Add implementation summary document

## 1. PROGRAMMING LANGUAGES & FRAMEWORKS

### Primary Language: Python 3
- **Version**: 3.7+ required
- **Paradigm**: Object-oriented with functional patterns
- **Total LOC**: ~1,753 lines of production code

### Core Dependencies
```
numpy >= 1.21.0      # Numerical computing
scipy >= 1.7.0       # Scientific functions (ODE integration)
matplotlib >= 3.4.0  # Visualization & plotting
```

### Key Technologies
- **ODE Integration**: `scipy.integrate.solve_ivp` (RK45 adaptive solver)
- **Data Structures**: NumPy arrays, dictionaries
- **Visualization**: Matplotlib for professional plotting

## 2. PROJECT STRUCTURE & ORGANIZATION

```
Gallop/
├── README.md                     # Complete documentation (489 lines)
├── IMPLEMENTATION_SUMMARY.md     # Phase A implementation details (318 lines)
├── requirements.txt              # Python dependencies
├── .gitignore                    # Python/results exclusions
├── run_analysis.py               # Main analysis entry point (411 lines)
└── src/                          # Core package (1,307 lines total)
    ├── __init__.py              # Package exports (35 lines)
    ├── parameters.py            # Physical parameter calculations (353 lines)
    ├── galloping_model.py       # Core simulation engine (398 lines)
    └── visualization.py         # Plotting and analysis (556 lines)
```

### Module Organization

**parameters.py** - Data Models & Parameters
- `ConductorParameters` class: 336.4 kcmil Merlin ACSR specs
- `EnvironmentalParameters` class: Ice and wind conditions
- `DeviceParameters` class: Bi-stable device properties
- Helper functions: `calculate_ice_mass()`, `calculate_modal_properties()`
- `get_full_parameters()`: Main configuration factory function

**galloping_model.py** - Core Simulation Engine
- `GallopingSimulation` class: Main simulation orchestrator
  - `calculate_aerodynamic_force()`: Den Hartog criterion implementation
  - `calculate_device_forces()`: Bi-stable device mechanics
  - `equations_of_motion()`: ODE system definition
  - `run_simulation()`: Execute simulation and collect results
- `compare_results()`: Comparative analysis between baseline and device scenarios
- `print_comparison()`: Formatted reporting

**visualization.py** - Analysis & Reporting
- `setup_plot_style()`: Matplotlib configuration
- `plot_time_history()`: Amplitude vs time
- `plot_phase_portrait()`: State-space visualization
- `plot_energy_history()`: Energy evolution tracking
- `plot_device_activity()`: Snap event timeline
- `plot_parametric_study()`: Sensitivity analysis
- `create_summary_figure()`: Multi-panel summary
- `save_results_to_file()`: Text-based reporting

**run_analysis.py** - Main Orchestrator
- `run_baseline_and_device_comparison()`: Primary simulation workflow
- `parametric_study_num_devices()`: Device count optimization
- `parametric_study_snap_threshold()`: Threshold parameter sensitivity
- `generate_final_report()`: Final report generation
- `main()`: Execution pipeline

## 3. EXISTING DOMAIN CODE (Work Orders, Billing, Accounting)

**STATUS**: NONE FOUND

Current codebase is exclusively dedicated to conductor galloping simulation:
- No work order models or tracking
- No billing or invoicing code
- No accounting ledgers or reconciliation
- No NISC integration
- No ABS interfaces

The branch name suggests this is a NEW initiative to add work order reconciliation functionality.

## 4. NISC & ABS RELATED CODE

**STATUS**: NONE FOUND

No existing integrations with:
- NISC (Network Item Service Controller or similar)
- ABS (Asset-Based Services or similar)
- Any external accounting systems
- API connectors for third-party services

## 5. DATA MODELS & DATABASE SCHEMA

### Current Data Model Architecture

**Hierarchical Configuration Objects**
```python
Parameters Dictionary Structure:
{
  # Conductor specs (scalars)
  'conductor_diameter': float,
  'conductor_mass': float,
  'tension': float,
  'span_length': float,
  
  # Ice accumulation (scalars)
  'ice_thickness': float,
  'ice_mass': float,
  'iced_diameter': float,
  
  # Modal properties (scalars)
  'M': float,          # modal mass
  'K': float,          # modal stiffness
  'C': float,          # modal damping
  'omega_n': float,    # natural frequency (rad/s)
  'f_n': float,        # natural frequency (Hz)
  'zeta': float,       # damping ratio
  
  # Aerodynamic (scalars)
  'wind_speed': float,
  'air_density': float,
  'F0': float,         # base aerodynamic force
  'alpha': float,      # coupling coefficient
  'C_eff': float,      # combined aero coefficient
  
  # Devices (list of dicts)
  'devices': [
    {
      'id': int,
      'position': float,          # x-coordinate on span
      'mass': float,
      'snap_threshold': float,
      'snap_force': float,
      'snap_energy': float,
      'state': int,               # +1 or -1 (bi-stable state)
      'last_position': float,
      'snap_count': int
    },
    ...
  ],
  'num_devices': int,
  
  # Simulation control (scalars)
  'dt': float,         # timestep
  'T_sim': float       # simulation duration
}
```

**Results Data Structure**
```python
Results Dictionary:
{
  # Time series (numpy arrays)
  'time': ndarray,                 # shape (n_samples,)
  'amplitude': ndarray,            # shape (n_samples,)
  'velocity': ndarray,             # shape (n_samples,)
  'kinetic_energy': ndarray,       # shape (n_samples,)
  'potential_energy': ndarray,     # shape (n_samples,)
  'total_energy': ndarray,         # shape (n_samples,)
  
  # Snap events (list of dicts)
  'snap_events': [
    {
      'time': float,
      'device_id': int,
      'amplitude': float,
      'velocity': float,
      'new_state': int,
      'position': float
    },
    ...
  ],
  
  # Metrics (scalars)
  'A_max_steady': float,
  'A_rms_steady': float,
  'A_mean_steady': float,
  'A_max_overall': float,
  'max_velocity': float,
  'max_energy': float,
  'num_snaps': int,
  'snap_rate': float,
  'energy_dissipated': float,
  
  # Metadata
  'use_devices': bool,
  'num_devices': int,
  'success': bool,
  'message': str
}
```

**NO DATABASE**: All operations are in-memory; results saved to files

### File-Based Outputs
- PNG plots: High-resolution visualization outputs
- TXT files: Numerical summaries and reports
- No persistent database (SQLite, PostgreSQL, etc.)
- No ORM (SQLAlchemy, Django ORM, etc.)

## 6. TESTING FRAMEWORK & PATTERNS

### Current Testing Status
**NO FORMAL TESTING FRAMEWORK**

- No pytest, unittest, or similar
- No test directories
- No CI/CD configuration
- No automated test suites

### Validation Approach
- **Manual validation** via parameter summary printing
- **Output inspection** via generated plots
- **Success criteria checking**: Hardcoded thresholds in `compare_results()`
- **Smoke tests** in `if __name__ == "__main__"` blocks

### Success Criteria (Embedded in Code)
```python
# From galloping_model.py::compare_results()
if reduction_max > 30 and reduction_rms > 25:
    effectiveness = "FEASIBLE"
elif reduction_max > 10 or reduction_rms > 10:
    effectiveness = "MARGINAL"
else:
    effectiveness = "INEFFECTIVE"
```

## 7. ARCHITECTURE SUMMARY

### Design Patterns
1. **Factory Pattern**: `get_full_parameters()` creates configuration objects
2. **Encapsulation**: Separate concerns (parameters, simulation, visualization)
3. **Functional Style**: Pure functions for calculations (aerodynamics, ice mass)
4. **Data-Driven**: Configuration drives simulation behavior

### Code Organization Principles
- **Modular**: Clear separation of concerns
- **Documented**: Comprehensive docstrings and comments
- **Parametric**: All physics constants configurable
- **Reproducible**: Seed-able, deterministic ODE solver

### Computational Flow
```
User Input (run_analysis.py)
    ↓
Parameter Factory (parameters.py::get_full_parameters)
    ↓
Simulation Instance (galloping_model.py::GallopingSimulation)
    ↓
ODE Integration (scipy.integrate.solve_ivp)
    ↓
Post-Processing (results extraction, metrics calculation)
    ↓
Comparison Analysis (galloping_model.py::compare_results)
    ↓
Visualization (visualization.py - 10 different plot types)
    ↓
File Output (PNG plots + TXT reports)
```

## 8. BEST LOCATION FOR WORK ORDER RECONCILIATION SYSTEM

### Recommended Architecture

#### Option A: Parallel Module (RECOMMENDED)
```
Gallop/
├── src/
│   ├── galloping_model/       # Existing physics simulation
│   │   ├── __init__.py
│   │   ├── parameters.py
│   │   ├── galloping_model.py
│   │   └── visualization.py
│   │
│   ├── workorder_system/      # NEW: Work order reconciliation
│   │   ├── __init__.py
│   │   ├── models.py          # Work order data models
│   │   ├── reconciler.py      # Reconciliation logic
│   │   ├── nisc_connector.py  # NISC API integration
│   │   ├── storage.py         # Database/persistence
│   │   └── validators.py      # Business rule validation
│   │
│   └── shared/                # NEW: Common utilities
│       ├── __init__.py
│       ├── config.py          # Global configuration
│       ├── logging.py         # Centralized logging
│       └── exceptions.py      # Custom exceptions
│
├── tests/                     # NEW: Test suite
│   ├── test_workorder_models.py
│   ├── test_reconciliation.py
│   ├── test_nisc_integration.py
│   └── test_galloping_model.py
│
├── migrations/                # NEW: Database migrations (if using SQL)
│
├── config/                    # NEW: Configuration files
│   ├── development.yaml
│   ├── production.yaml
│   └── test.yaml
│
├── data/                      # NEW: Data files
│   ├── workorder_imports/     # NISC/ABS input files
│   └── reconciliation_logs/   # Audit trail
│
├── docs/                      # NEW: Documentation
│   ├── workorder_system.md
│   ├── nisc_integration.md
│   └── database_schema.md
│
└── requirements.txt           # Updated with new dependencies
```

#### Option B: Integrated System (if tight coupling needed)
- Single unified application
- Shared data model between simulation and work orders
- Shared database backend
- Less recommended due to domain separation

### Recommended Database Technology

**SQLAlchemy ORM + PostgreSQL** (recommended for enterprise use)
- Scalable
- ACID compliance
- Native JSON support for nested work order data
- Excellent Python integration
- Audit trail capabilities

Alternatively: **SQLite** for simpler deployments

### Key New Components Needed

1. **Work Order Models** (`workorder_system/models.py`)
   - WorkOrder entity
   - LineItem entity
   - ReconciliationRecord entity
   - AuditLog entity

2. **NISC Connector** (`workorder_system/nisc_connector.py`)
   - API client for NISC/ABS
   - Data transformer/mapper
   - Error handling and retry logic
   - Rate limiting

3. **Reconciliation Engine** (`workorder_system/reconciler.py`)
   - Match algorithms
   - Difference detection
   - Discrepancy reporting
   - State management

4. **Data Persistence** (`workorder_system/storage.py`)
   - ORM repository pattern
   - Query builders
   - Transaction management

5. **Validation Framework** (`workorder_system/validators.py`)
   - Business rule checkers
   - Schema validators
   - Consistency checkers

### Testing Strategy Needed

```python
# tests/test_reconciliation.py structure
- TestWorkOrderModels
  - test_work_order_creation
  - test_line_item_validation
  - test_total_calculation

- TestNISCConnector
  - test_api_connection
  - test_data_mapping
  - test_error_handling

- TestReconciliation
  - test_matching_algorithm
  - test_discrepancy_detection
  - test_bulk_reconciliation

- TestPersistence
  - test_save_and_retrieve
  - test_transaction_rollback
```

## 9. IMMEDIATE NEXT STEPS

### Phase 0: Foundation (Week 1-2)
1. [ ] Set up database schema (PostgreSQL + SQLAlchemy)
2. [ ] Create WorkOrder and LineItem models
3. [ ] Implement basic CRUD operations
4. [ ] Set up testing framework (pytest)
5. [ ] Document NISC API requirements

### Phase 1: NISC Integration (Week 2-3)
1. [ ] Build NISC connector module
2. [ ] Implement data mapping/transformation
3. [ ] Create import pipeline
4. [ ] Add validation rules

### Phase 2: Reconciliation Engine (Week 3-4)
1. [ ] Implement matching algorithms
2. [ ] Create discrepancy detection
3. [ ] Build audit logging
4. [ ] Implement state management

### Phase 3: Reporting & UI (Week 4+)
1. [ ] Create reconciliation reports
2. [ ] Build CLI tools
3. [ ] Optional: Add web interface
4. [ ] Documentation and training

