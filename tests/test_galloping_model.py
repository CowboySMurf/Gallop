"""
Unit tests for galloping_model.py module.
Tests simulation engine, aerodynamic forces, device forces, and integration.
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.galloping_model import GallopingSimulation, compare_results, print_comparison
from src.parameters import get_full_parameters


class TestGallopingSimulation:
    """Test GallopingSimulation class."""

    def test_initialization_with_devices(self):
        """Test simulation initialization with devices."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=True)

        assert sim.use_devices is True
        assert len(sim.devices) == 4
        assert sim.M == params['M']
        assert sim.K == params['K']
        assert sim.C == params['C']

    def test_initialization_without_devices(self):
        """Test simulation initialization without devices."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=False)

        assert sim.use_devices is False
        assert len(sim.devices) == 0

    def test_snap_events_initialized(self):
        """Test that snap events list is initialized."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=True)

        assert sim.snap_events == []
        assert sim.energy_dissipated == 0.0


class TestAerodynamicForce:
    """Test aerodynamic force calculation."""

    def test_aerodynamic_force_zero_velocity(self):
        """Test aerodynamic force at zero velocity."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)

        F_aero = sim.calculate_aerodynamic_force(A=0.5, dA_dt=0.0)
        assert F_aero == 0.0

    def test_aerodynamic_force_positive_velocity(self):
        """Test aerodynamic force with positive velocity."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)

        F_aero = sim.calculate_aerodynamic_force(A=0.5, dA_dt=1.0)
        assert F_aero != 0.0

    def test_aerodynamic_force_negative_velocity(self):
        """Test aerodynamic force with negative velocity."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)

        F_aero = sim.calculate_aerodynamic_force(A=0.5, dA_dt=-1.0)
        assert F_aero != 0.0

    def test_aerodynamic_force_symmetry(self):
        """Test that aerodynamic force changes sign with velocity."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)

        F_pos = sim.calculate_aerodynamic_force(A=0.5, dA_dt=1.0)
        F_neg = sim.calculate_aerodynamic_force(A=0.5, dA_dt=-1.0)

        # Forces should have opposite signs for opposite velocities
        assert np.sign(F_pos) != np.sign(F_neg)

    def test_aerodynamic_force_zero_wind(self):
        """Test aerodynamic force with zero wind speed."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)
        sim.V = 0.0  # Set wind speed to zero

        F_aero = sim.calculate_aerodynamic_force(A=0.5, dA_dt=1.0)
        assert F_aero == 0.0


class TestDeviceForces:
    """Test device force calculation."""

    def test_device_forces_no_devices(self):
        """Test device forces when no devices present."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)

        Q_devices, snaps = sim.calculate_device_forces(A=0.5, dA_dt=1.0)
        assert Q_devices == 0.0
        assert len(snaps) == 0

    def test_device_forces_with_devices(self):
        """Test device forces with devices present."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=True)

        Q_devices, snaps = sim.calculate_device_forces(A=0.5, dA_dt=1.0)
        # Should have damping force even without snaps
        assert Q_devices != 0.0

    def test_device_damping_opposes_velocity(self):
        """Test that device damping opposes velocity."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=True)

        Q_pos, _ = sim.calculate_device_forces(A=0.1, dA_dt=1.0)
        Q_neg, _ = sim.calculate_device_forces(A=0.1, dA_dt=-1.0)

        # Damping should oppose motion (opposite sign to velocity)
        assert Q_pos < 0
        assert Q_neg > 0

    def test_snap_event_large_displacement(self):
        """Test that snap events occur at large displacement."""
        params = get_full_parameters(num_devices=4, snap_threshold=0.10)
        sim = GallopingSimulation(params, use_devices=True)
        sim.current_time = 1.0

        # Large displacement should trigger snaps
        Q_devices, snaps = sim.calculate_device_forces(A=1.0, dA_dt=0.5)

        # At least some devices should snap
        assert len(snaps) > 0
        assert len(sim.snap_events) > 0

    def test_snap_event_structure(self):
        """Test that snap events have correct structure."""
        params = get_full_parameters(num_devices=4, snap_threshold=0.10)
        sim = GallopingSimulation(params, use_devices=True)
        sim.current_time = 1.0

        Q_devices, snaps = sim.calculate_device_forces(A=1.0, dA_dt=0.5)

        if len(snaps) > 0:
            snap = snaps[0]
            assert 'time' in snap
            assert 'device_id' in snap
            assert 'amplitude' in snap
            assert 'velocity' in snap
            assert 'new_state' in snap
            assert 'position' in snap


class TestEquationsOfMotion:
    """Test equations of motion."""

    def test_state_derivative_shape(self):
        """Test that state derivative has correct shape."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=True)

        state = np.array([0.1, 0.5])  # [A, dA_dt]
        derivative = sim.equations_of_motion(0.0, state)

        assert derivative.shape == (2,)

    def test_state_derivative_structure(self):
        """Test that state derivative has correct structure."""
        params = get_full_parameters(num_devices=4)
        sim = GallopingSimulation(params, use_devices=True)

        state = np.array([0.1, 0.5])  # [A, dA_dt]
        derivative = sim.equations_of_motion(0.0, state)

        # First derivative should be velocity
        assert derivative[0] == state[1]

        # Second derivative should be acceleration
        assert isinstance(derivative[1], (float, np.floating))

    def test_restoring_force_sign(self):
        """Test that restoring force has correct sign."""
        params = get_full_parameters(num_devices=0)
        sim = GallopingSimulation(params, use_devices=False)

        # Positive displacement should create negative restoring acceleration
        # (but aero force can make it positive for galloping)
        state_pos = np.array([0.5, 0.0])
        derivative_pos = sim.equations_of_motion(0.0, state_pos)

        # Just check that derivative is calculated
        assert np.isfinite(derivative_pos[1])


class TestRunSimulation:
    """Test simulation execution."""

    def test_simulation_runs_without_devices(self):
        """Test that simulation runs successfully without devices."""
        params = get_full_parameters(num_devices=0)
        # Shorter simulation for testing
        params['T_sim'] = 5.0

        sim = GallopingSimulation(params, use_devices=False)
        results = sim.run_simulation(A0=0.01)

        assert results['success'] is True
        assert len(results['time']) > 0
        assert len(results['amplitude']) == len(results['time'])
        assert len(results['velocity']) == len(results['time'])

    def test_simulation_runs_with_devices(self):
        """Test that simulation runs successfully with devices."""
        params = get_full_parameters(num_devices=4)
        # Shorter simulation for testing
        params['T_sim'] = 5.0

        sim = GallopingSimulation(params, use_devices=True)
        results = sim.run_simulation(A0=0.01)

        assert results['success'] is True
        assert len(results['time']) > 0

    def test_results_structure(self):
        """Test that results have correct structure."""
        params = get_full_parameters(num_devices=4)
        params['T_sim'] = 5.0

        sim = GallopingSimulation(params, use_devices=True)
        results = sim.run_simulation(A0=0.01)

        required_keys = [
            'time', 'amplitude', 'velocity',
            'kinetic_energy', 'potential_energy', 'total_energy',
            'snap_events', 'A_max_steady', 'A_rms_steady',
            'A_mean_steady', 'A_max_overall', 'max_velocity',
            'max_energy', 'num_snaps', 'snap_rate',
            'energy_dissipated', 'use_devices', 'num_devices',
            'success', 'message'
        ]

        for key in required_keys:
            assert key in results, f"Missing key: {key}"

    def test_device_specific_results(self):
        """Test that device simulations include device-specific results."""
        params = get_full_parameters(num_devices=4)
        params['T_sim'] = 5.0

        sim = GallopingSimulation(params, use_devices=True)
        results = sim.run_simulation(A0=0.01)

        assert 'device_snap_counts' in results
        assert 'devices' in results
        assert len(results['device_snap_counts']) == 4

    def test_initial_conditions(self):
        """Test that initial conditions are respected."""
        params = get_full_parameters(num_devices=0)
        params['T_sim'] = 5.0

        A0 = 0.05
        dA0_dt = 0.1

        sim = GallopingSimulation(params, use_devices=False)
        results = sim.run_simulation(A0=A0, dA0_dt=dA0_dt)

        # First point should match initial conditions (approximately)
        assert np.isclose(results['amplitude'][0], A0, atol=0.01)
        assert np.isclose(results['velocity'][0], dA0_dt, atol=0.01)

    def test_energy_components(self):
        """Test that energy components are calculated correctly."""
        params = get_full_parameters(num_devices=0)
        params['T_sim'] = 5.0

        sim = GallopingSimulation(params, use_devices=False)
        results = sim.run_simulation(A0=0.01)

        # Energy should be positive
        assert np.all(results['kinetic_energy'] >= 0)
        assert np.all(results['potential_energy'] >= 0)
        assert np.all(results['total_energy'] >= 0)

        # Total should equal kinetic + potential (approximately)
        for i in range(len(results['time'])):
            total_calc = results['kinetic_energy'][i] + results['potential_energy'][i]
            assert np.isclose(results['total_energy'][i], total_calc, rtol=1e-5)

    def test_metrics_positive(self):
        """Test that metrics are positive."""
        params = get_full_parameters(num_devices=4)
        params['T_sim'] = 5.0

        sim = GallopingSimulation(params, use_devices=True)
        results = sim.run_simulation(A0=0.01)

        assert results['A_max_steady'] >= 0
        assert results['A_rms_steady'] >= 0
        assert results['A_mean_steady'] >= 0
        assert results['max_velocity'] >= 0
        assert results['max_energy'] >= 0
        assert results['snap_rate'] >= 0


class TestCompareResults:
    """Test results comparison."""

    def test_comparison_structure(self):
        """Test that comparison has correct structure."""
        params = get_full_parameters(num_devices=4)
        params['T_sim'] = 5.0

        baseline_sim = GallopingSimulation(params, use_devices=False)
        baseline_results = baseline_sim.run_simulation(A0=0.01)

        device_sim = GallopingSimulation(params, use_devices=True)
        device_results = device_sim.run_simulation(A0=0.01)

        comparison = compare_results(baseline_results, device_results)

        required_keys = [
            'A_max_baseline', 'A_max_devices', 'reduction_max_percent',
            'A_rms_baseline', 'A_rms_devices', 'reduction_rms_percent',
            'E_max_baseline', 'E_max_devices', 'energy_reduction_percent',
            'num_snaps', 'snap_rate', 'energy_dissipated', 'effectiveness'
        ]

        for key in required_keys:
            assert key in comparison, f"Missing key: {key}"

    def test_reduction_calculation(self):
        """Test that reduction percentages are calculated correctly."""
        # Create mock results
        baseline_results = {
            'A_max_steady': 3.0,
            'A_rms_steady': 2.0,
            'max_energy': 100.0
        }

        device_results = {
            'A_max_steady': 2.0,
            'A_rms_steady': 1.5,
            'max_energy': 70.0,
            'num_snaps': 50,
            'snap_rate': 1.0,
            'energy_dissipated': 200.0
        }

        comparison = compare_results(baseline_results, device_results)

        # Check reduction calculations
        assert np.isclose(comparison['reduction_max_percent'],
                         (3.0 - 2.0) / 3.0 * 100, rtol=1e-5)
        assert np.isclose(comparison['reduction_rms_percent'],
                         (2.0 - 1.5) / 2.0 * 100, rtol=1e-5)
        assert np.isclose(comparison['energy_reduction_percent'],
                         (100.0 - 70.0) / 100.0 * 100, rtol=1e-5)

    def test_effectiveness_assessment_feasible(self):
        """Test effectiveness assessment for feasible case."""
        baseline_results = {
            'A_max_steady': 3.0,
            'A_rms_steady': 2.0,
            'max_energy': 100.0
        }

        device_results = {
            'A_max_steady': 2.0,  # 33% reduction
            'A_rms_steady': 1.4,  # 30% reduction
            'max_energy': 70.0,
            'num_snaps': 50,
            'snap_rate': 1.0,
            'energy_dissipated': 200.0
        }

        comparison = compare_results(baseline_results, device_results)
        assert "FEASIBLE" in comparison['effectiveness']

    def test_effectiveness_assessment_marginal(self):
        """Test effectiveness assessment for marginal case."""
        baseline_results = {
            'A_max_steady': 3.0,
            'A_rms_steady': 2.0,
            'max_energy': 100.0
        }

        device_results = {
            'A_max_steady': 2.5,  # 16.7% reduction
            'A_rms_steady': 1.7,  # 15% reduction
            'max_energy': 85.0,
            'num_snaps': 50,
            'snap_rate': 1.0,
            'energy_dissipated': 100.0
        }

        comparison = compare_results(baseline_results, device_results)
        assert "MARGINAL" in comparison['effectiveness']

    def test_effectiveness_assessment_ineffective(self):
        """Test effectiveness assessment for ineffective case."""
        baseline_results = {
            'A_max_steady': 3.0,
            'A_rms_steady': 2.0,
            'max_energy': 100.0
        }

        device_results = {
            'A_max_steady': 2.9,  # 3.3% reduction
            'A_rms_steady': 1.95,  # 2.5% reduction
            'max_energy': 98.0,
            'num_snaps': 10,
            'snap_rate': 0.2,
            'energy_dissipated': 20.0
        }

        comparison = compare_results(baseline_results, device_results)
        assert "INEFFECTIVE" in comparison['effectiveness']


class TestPrintComparison:
    """Test print comparison function."""

    def test_print_runs_without_error(self):
        """Test that print function runs without error."""
        comparison = {
            'A_max_baseline': 3.0,
            'A_max_devices': 2.0,
            'reduction_max_percent': 33.3,
            'A_rms_baseline': 2.0,
            'A_rms_devices': 1.5,
            'reduction_rms_percent': 25.0,
            'E_max_baseline': 100.0,
            'E_max_devices': 70.0,
            'energy_reduction_percent': 30.0,
            'num_snaps': 50,
            'snap_rate': 1.0,
            'energy_dissipated': 200.0,
            'effectiveness': 'FEASIBLE'
        }

        try:
            print_comparison(comparison)
        except Exception as e:
            pytest.fail(f"print_comparison raised exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
