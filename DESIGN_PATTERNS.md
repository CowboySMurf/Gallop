# Design Patterns & Best Practices for Work Order System Implementation

## Overview
This document outlines design patterns and best practices observed in the existing galloping simulation codebase that should be followed when implementing the new work order reconciliation system.

## 1. EXISTING DESIGN PATTERNS TO FOLLOW

### 1.1 Factory Pattern
**Current Usage**: `parameters.py::get_full_parameters()`

```python
# EXISTING PATTERN - Should replicate for WorkOrder creation
def get_full_parameters(num_devices: int = 4, snap_threshold: float = 0.15,
                        snap_force: float = 200) -> Dict:
    # Build configuration from components
    conductor = ConductorParameters()
    environment = EnvironmentalParameters()
    device = DeviceParameters()
    
    # Compose into complete parameter set
    params = {
        'conductor_diameter': conductor.diameter,
        'tension': conductor.tension,
        # ... more fields
    }
    return params
```

**Application to Work Order System**:
```python
# RECOMMENDED PATTERN
def create_workorder(order_id: str, vendor_id: str, items: List[Dict]) -> WorkOrder:
    """Factory function to create properly initialized WorkOrder"""
    wo = WorkOrder(order_id=order_id, vendor_id=vendor_id)
    
    for item_data in items:
        item = LineItem.from_dict(item_data)
        item.validate()  # Fail fast
        wo.add_line_item(item)
    
    wo.calculate_totals()
    return wo
```

### 1.2 Class-Based Organization with Data Classes
**Current Usage**: `ConductorParameters`, `EnvironmentalParameters`, `DeviceParameters`

```python
# EXISTING PATTERN
class ConductorParameters:
    """336.4 kcmil Merlin ACSR conductor properties"""
    diameter_inches = 0.721
    diameter = 0.721 * 0.0254
    mass_per_length_imperial = 0.644
    mass_per_length = 0.644 * 1.48816
```

**Application to Work Order System**:
```python
# RECOMMENDED PATTERN - Use Python 3.7+ dataclasses
from dataclasses import dataclass
from typing import List
from enum import Enum

class WorkOrderStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    RECEIVED = "received"
    RECONCILED = "reconciled"
    FLAGGED = "flagged"

@dataclass
class LineItem:
    """Work order line item"""
    item_id: str
    description: str
    quantity: float
    unit_price: float
    tax_rate: float = 0.0
    
    def calculate_total(self) -> float:
        return self.quantity * self.unit_price * (1 + self.tax_rate)
    
    def validate(self) -> List[str]:
        """Return list of validation errors"""
        errors = []
        if self.quantity <= 0:
            errors.append("Quantity must be positive")
        if self.unit_price < 0:
            errors.append("Unit price cannot be negative")
        return errors

@dataclass
class WorkOrder:
    """Main work order entity"""
    order_id: str
    vendor_id: str
    order_date: datetime
    line_items: List[LineItem] = field(default_factory=list)
    status: WorkOrderStatus = WorkOrderStatus.DRAFT
    notes: str = ""
    
    def add_line_item(self, item: LineItem) -> None:
        """Add validated item"""
        errors = item.validate()
        if errors:
            raise ValueError(f"Invalid line item: {errors}")
        self.line_items.append(item)
    
    def calculate_total(self) -> float:
        """Calculate order total"""
        return sum(item.calculate_total() for item in self.line_items)
```

### 1.3 Type Hints (Strongly Enforced in Existing Code)
**Current Usage**: Throughout all modules

```python
# EXISTING PATTERN
def calculate_ice_mass(conductor_diameter: float, ice_thickness: float,
                       ice_density: float) -> float:
    """docstring"""
    area_ice = np.pi * ((d/2 + t)**2 - (d/2)**2)
    return ice_density * area_ice

def calculate_modal_properties(m_total: float, span_length: float,
                                tension: float, damping_ratio: float = 0.001) -> Dict:
    """Return dictionary with modal properties"""
    return {
        'M': M,
        'K': K,
        'C': C,
    }
```

**Application to Work Order System**:
```python
# RECOMMENDED PATTERN
from typing import Dict, List, Optional, Tuple

def validate_and_transform_nisc_data(
    raw_data: Dict[str, Any],
    validator: WorkOrderValidator
) -> Tuple[List[WorkOrder], List[Dict]]:
    """
    Transform raw NISC data to WorkOrder objects.
    
    Args:
        raw_data: Raw API response
        validator: Validator instance for business rules
    
    Returns:
        Tuple of (valid_workorders, validation_errors)
    """
    valid_orders = []
    errors = []
    
    for record in raw_data['workorders']:
        try:
            validated = validator.validate_record(record)
            wo = WorkOrder.from_dict(validated)
            valid_orders.append(wo)
        except ValidationError as e:
            errors.append({
                'record_id': record.get('id'),
                'error': str(e)
            })
    
    return valid_orders, errors

def get_reconciliation_report(
    internal_orders: List[WorkOrder],
    nisc_orders: List[WorkOrder],
    config: ReconciliationConfig
) -> ReconciliationReport:
    """Generate reconciliation report"""
    # Implementation
    pass
```

### 1.4 Results Dictionary Pattern
**Current Usage**: `run_simulation()` returns comprehensive results dict

```python
# EXISTING PATTERN
results = {
    'time': time,                      # numpy array
    'amplitude': amplitude,            # numpy array
    'snap_events': self.snap_events,  # list of dicts
    'A_max_steady': A_max,            # scalar
    'A_rms_steady': A_rms,
    'use_devices': self.use_devices,
    'success': solution.success,
    'message': solution.message
}
```

**Application to Work Order System**:
```python
# RECOMMENDED PATTERN
def reconcile_workorders(internal: List[WorkOrder],
                        nisc: List[WorkOrder]) -> ReconciliationResult:
    """
    Comprehensive reconciliation with all relevant metrics.
    
    Returns: ReconciliationResult with:
        - matched_pairs: List of (internal, nisc) tuples
        - unmatched_internal: WorkOrders only in internal system
        - unmatched_nisc: WorkOrders only in NISC
        - discrepancies: List of found differences
        - total_matched: Count
        - total_unmatched: Count
        - match_percentage: Ratio
    """
    return ReconciliationResult(
        matched_pairs=matches,
        unmatched_internal=internal_only,
        unmatched_nisc=nisc_only,
        discrepancies=diffs,
        total_matched=len(matches),
        total_unmatched=len(internal_only) + len(nisc_only),
        match_percentage=(len(matches) / (len(internal) + len(nisc))) * 100,
        timestamp=datetime.now(),
        config_used=config
    )
```

### 1.5 Comprehensive Documentation Pattern
**Current Usage**: Docstrings, type hints, parameter summaries

```python
# EXISTING PATTERN
def calculate_aerodynamic_parameters(air_density: float, wind_speed: float,
                                     iced_diameter: float, C_eff: float,
                                     span_length: float) -> Dict:
    """
    Calculate aerodynamic forcing parameters.

    Args:
        air_density: Air density (kg/m³)
        wind_speed: Wind speed (m/s)
        iced_diameter: Effective diameter with ice (m)
        C_eff: Combined aerodynamic coefficient (dimensionless)
        span_length: Span length (m)

    Returns:
        Dictionary with aerodynamic parameters
    """
```

**Application to Work Order System**:
```python
# RECOMMENDED PATTERN
def match_workorders(internal_orders: List[WorkOrder],
                     nisc_orders: List[WorkOrder],
                     match_strategy: str = 'exact') -> List[Tuple[WorkOrder, WorkOrder]]:
    """
    Match work orders between internal system and NISC.
    
    This function attempts to match WorkOrders using various strategies:
    - 'exact': Order ID and vendor match exactly (fastest, most reliable)
    - 'fuzzy': Allows minor variations in vendor names (slower, finds more)
    - 'semantic': Analyzes line items for content similarity (slowest, most flexible)
    
    Args:
        internal_orders: List of work orders from internal system
        nisc_orders: List of work orders from NISC API
        match_strategy: One of 'exact', 'fuzzy', 'semantic'. Default: 'exact'
    
    Returns:
        List of matched (internal, nisc) tuples
    
    Raises:
        ValueError: If match_strategy is invalid
        TypeError: If input lists contain non-WorkOrder objects
    
    Examples:
        >>> internal = [wo1, wo2, wo3]
        >>> nisc = [wo_a, wo_b, wo_c]
        >>> matches = match_workorders(internal, nisc, 'exact')
        >>> len(matches)
        2
    """
```

## 2. CODE STYLE GUIDELINES (From Existing Code)

### 2.1 Naming Conventions
- **Classes**: PascalCase (`WorkOrder`, `LineItem`, `ReconciliationEngine`)
- **Functions**: snake_case (`validate_workorder()`, `match_orders()`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_TIMEOUT = 30`, `MAX_RETRIES = 3`)
- **Private methods**: Leading underscore (`_validate_format()`)

### 2.2 Line Length
- Max 100 characters (enforced in existing code)
- Break long function signatures across multiple lines

### 2.3 Import Organization
```python
# PATTERN from existing code
import numpy as np                          # Standard library
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp       # Third-party
from typing import Dict, List, Optional     # Imports from packages

from .parameters import get_full_parameters # Relative imports
from .galloping_model import GallopingSimulation
```

**Apply to new code**:
```python
import os                                    # Standard library
import sys
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Tuple

import sqlalchemy as sa                      # Third-party
from sqlalchemy.orm import Session
import requests

from ..shared.config import get_config      # Relative imports
from ..shared.logging import get_logger
from .models import WorkOrder, LineItem
```

## 3. TESTING PATTERNS (To Establish)

While existing code lacks formal testing, the new system MUST include:

### 3.1 Test Structure
```
tests/
├── __init__.py
├── conftest.py                    # Shared fixtures
├── test_models.py                 # Entity tests
├── test_nisc_connector.py         # Integration tests
├── test_reconciliation.py         # Business logic tests
├── test_storage.py                # Database tests
└── fixtures/
    ├── sample_workorders.json
    └── sample_nisc_response.json
```

### 3.2 Test Pattern (Pytest)
```python
# tests/test_reconciliation.py
import pytest
from datetime import datetime

@pytest.fixture
def sample_internal_orders():
    """Fixture for internal work orders"""
    return [
        WorkOrder(order_id="WO-001", vendor_id="V123", order_date=datetime.now()),
        WorkOrder(order_id="WO-002", vendor_id="V456", order_date=datetime.now()),
    ]

@pytest.fixture
def sample_nisc_orders():
    """Fixture for NISC orders"""
    return [
        WorkOrder(order_id="WO-001", vendor_id="V123", order_date=datetime.now()),
    ]

class TestReconciliation:
    def test_exact_match(self, sample_internal_orders, sample_nisc_orders):
        """Test exact matching algorithm"""
        matches = match_workorders(sample_internal_orders, sample_nisc_orders, 'exact')
        assert len(matches) == 1
        assert matches[0][0].order_id == "WO-001"
    
    def test_unmatched_detection(self, sample_internal_orders, sample_nisc_orders):
        """Test detection of unmatched orders"""
        matches = match_workorders(sample_internal_orders, sample_nisc_orders, 'exact')
        unmatched_internal = [wo for wo in sample_internal_orders 
                             if wo not in [m[0] for m in matches]]
        assert len(unmatched_internal) == 1
        assert unmatched_internal[0].order_id == "WO-002"

    @pytest.mark.parametrize("strategy", ['exact', 'fuzzy', 'semantic'])
    def test_all_strategies(self, sample_internal_orders, sample_nisc_orders, strategy):
        """Test that all strategies run without error"""
        matches = match_workorders(sample_internal_orders, sample_nisc_orders, strategy)
        assert isinstance(matches, list)
```

## 4. CONFIGURATION MANAGEMENT (To Establish)

Following the principle of parametric configuration:

```python
# config/base_config.yaml
database:
  host: localhost
  port: 5432
  name: gallop_workorders
  user: ${DB_USER}          # Environment variable
  password: ${DB_PASSWORD}

nisc:
  api_url: https://api.nisc.example.com
  api_key: ${NISC_API_KEY}
  timeout: 30
  max_retries: 3

reconciliation:
  match_strategy: exact
  discrepancy_threshold: 0.01  # 1% variance
  chunk_size: 100              # Process in batches

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

## 5. ERROR HANDLING PATTERN

```python
# shared/exceptions.py
class GallopException(Exception):
    """Base exception for all Gallop errors"""
    pass

class WorkOrderException(GallopException):
    """Base for work order system errors"""
    pass

class ValidationError(WorkOrderException):
    """Raised when validation fails"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"Validation error in {field}: {message}")

class NISCException(WorkOrderException):
    """Raised when NISC integration fails"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        super().__init__(f"NISC API error {status_code}: {message}")

class ReconciliationException(WorkOrderException):
    """Raised during reconciliation failures"""
    pass
```

## 6. LOGGING PATTERN

Following Python's logging best practices:

```python
# shared/logging.py
import logging

def get_logger(name: str) -> logging.Logger:
    """Get configured logger for module"""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

# Usage in modules
# workorder_system/reconciler.py
logger = get_logger(__name__)

def reconcile_workorders(internal: List[WorkOrder], nisc: List[WorkOrder]):
    logger.info(f"Starting reconciliation: {len(internal)} internal, {len(nisc)} NISC")
    
    try:
        matches = match_workorders(internal, nisc)
        logger.info(f"Found {len(matches)} matches")
    except Exception as e:
        logger.error(f"Reconciliation failed: {str(e)}", exc_info=True)
        raise
```

## Summary

The new work order reconciliation system should:

1. **Maintain clarity** through strong typing and comprehensive docstrings
2. **Modularize concerns** following the existing pattern of separated modules
3. **Use factory patterns** for object creation and initialization
4. **Include comprehensive testing** from the start (unlike existing code)
5. **Follow naming conventions** consistently
6. **Provide detailed error messages** with custom exceptions
7. **Log comprehensively** for auditability and debugging
8. **Manage configuration** externally through YAML files
9. **Validate early** with fail-fast approach
10. **Document abundantly** with usage examples

This ensures the new system is maintainable, extensible, and follows Python best practices while remaining consistent with the existing galloping simulation codebase style.

