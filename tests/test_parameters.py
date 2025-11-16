"""
Unit tests for parameters.py module.
Tests physical parameter calculations and device configuration.
"""

import pytest
import numpy as np
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parameters import (
    ConductorParameters,
    EnvironmentalParameters,
    DeviceParameters,
    calculate_ice_mass,
    calculate_modal_properties,
    calculate_aerodynamic_parameters,
    create_device_configuration,
    get_full_parameters,
    print_parameter_summary
)


class TestConductorParameters:
    """Test conductor parameter class."""

    def test_conductor_properties(self):
        """Test that conductor properties are reasonable."""
        conductor = ConductorParameters()

        # Check diameter is positive
        assert conductor.diameter > 0
        assert conductor.diameter_inches > 0

        # Check mass is positive
        assert conductor.mass_per_length > 0
        assert conductor.mass_per_length_imperial > 0

        # Check tension is positive
        assert conductor.tension > 0
        assert conductor.tension_lbs > 0

        # Check span length is positive
        assert conductor.span_length > 0
        assert conductor.span_length_ft > 0

    def test_unit_conversions(self):
        """Test that unit conversions are consistent."""
        conductor = ConductorParameters()

        # Test diameter conversion (inches to meters)
        assert np.isclose(conductor.diameter, conductor.diameter_inches * 0.0254, rtol=1e-10)

        # Test mass conversion (lb/ft to kg/m)
        assert np.isclose(conductor.mass_per_length,
                         conductor.mass_per_length_imperial * 1.48816, rtol=1e-5)

        # Test tension conversion (lbs to N)
        assert np.isclose(conductor.tension, conductor.tension_lbs * 4.44822, rtol=1e-5)

        # Test span conversion (ft to m)
        assert np.isclose(conductor.span_length, conductor.span_length_ft * 0.3048, rtol=1e-10)


class TestEnvironmentalParameters:
    """Test environmental parameter class."""

    def test_environmental_properties(self):
        """Test that environmental properties are reasonable."""
        env = EnvironmentalParameters()

        # Check ice properties
        assert env.ice_thickness > 0
        assert env.ice_density > 0
        assert env.ice_density < 1000  # Ice is less dense than water

        # Check wind properties
        assert env.wind_speed > 0
        assert env.wind_speed_mph > 0

        # Check air density is reasonable
        assert env.air_density > 0
        assert env.air_density < 2.0  # Reasonable for sea level

        # Check iced diameter is larger than base diameter
        assert env.iced_diameter > ConductorParameters().diameter

    def test_aerodynamic_coefficient(self):
        """Test that aerodynamic coefficient indicates galloping instability."""
        env = EnvironmentalParameters()

        # C_eff should be negative for galloping
        assert env.C_eff < 0


class TestDeviceParameters:
    """Test device parameter class."""

    def test_device_properties(self):
        """Test that device properties are reasonable."""
        device = DeviceParameters()

        # Check all properties are positive
        assert device.num_devices > 0
        assert device.device_mass > 0
        assert device.snap_threshold > 0
        assert device.snap_force > 0
        assert device.snap_energy > 0
        assert device.beam_frequency > 0


class TestCalculateIceMass:
    """Test ice mass calculation."""

    def test_ice_mass_positive(self):
        """Test that ice mass is positive."""
        m_ice = calculate_ice_mass(0.02, 0.01, 900)
        assert m_ice > 0

    def test_ice_mass_increases_with_thickness(self):
        """Test that ice mass increases with thickness."""
        m_ice_1 = calculate_ice_mass(0.02, 0.005, 900)
        m_ice_2 = calculate_ice_mass(0.02, 0.010, 900)
        assert m_ice_2 > m_ice_1

    def test_ice_mass_increases_with_density(self):
        """Test that ice mass increases with density."""
        m_ice_1 = calculate_ice_mass(0.02, 0.01, 800)
        m_ice_2 = calculate_ice_mass(0.02, 0.01, 900)
        assert m_ice_2 > m_ice_1

    def test_ice_mass_zero_thickness(self):
        """Test that zero ice thickness gives zero ice mass."""
        m_ice = calculate_ice_mass(0.02, 0.0, 900)
        assert np.isclose(m_ice, 0.0, atol=1e-10)


class TestCalculateModalProperties:
    """Test modal property calculations."""

    def test_modal_properties_positive(self):
        """Test that all modal properties are positive."""
        modal = calculate_modal_properties(m_total=2.0, span_length=100.0,
                                           tension=20000.0, damping_ratio=0.001)

        assert modal['M'] > 0
        assert modal['K'] > 0
        assert modal['C'] > 0
        assert modal['omega_n'] > 0
        assert modal['f_n'] > 0
        assert modal['zeta'] > 0

    def test_natural_frequency_units(self):
        """Test that natural frequency units are consistent."""
        modal = calculate_modal_properties(m_total=2.0, span_length=100.0,
                                           tension=20000.0)

        # omega_n should be 2*pi*f_n
        assert np.isclose(modal['omega_n'], 2 * np.pi * modal['f_n'], rtol=1e-10)

    def test_damping_coefficient(self):
        """Test damping coefficient calculation."""
        zeta = 0.005
        modal = calculate_modal_properties(m_total=2.0, span_length=100.0,
                                           tension=20000.0, damping_ratio=zeta)

        # C = 2*zeta*sqrt(K*M)
        C_expected = 2 * zeta * np.sqrt(modal['K'] * modal['M'])
        assert np.isclose(modal['C'], C_expected, rtol=1e-10)

    def test_frequency_increases_with_tension(self):
        """Test that frequency increases with tension."""
        modal_1 = calculate_modal_properties(2.0, 100.0, 15000.0)
        modal_2 = calculate_modal_properties(2.0, 100.0, 20000.0)

        assert modal_2['f_n'] > modal_1['f_n']

    def test_frequency_decreases_with_mass(self):
        """Test that frequency decreases with mass."""
        modal_1 = calculate_modal_properties(1.5, 100.0, 20000.0)
        modal_2 = calculate_modal_properties(2.0, 100.0, 20000.0)

        assert modal_2['f_n'] < modal_1['f_n']


class TestCalculateAerodynamicParameters:
    """Test aerodynamic parameter calculations."""

    def test_aerodynamic_parameters_structure(self):
        """Test that aerodynamic parameters have correct structure."""
        aero = calculate_aerodynamic_parameters(
            air_density=1.225,
            wind_speed=15.0,
            iced_diameter=0.04,
            C_eff=-0.15,
            span_length=100.0
        )

        assert 'F0' in aero
        assert 'alpha' in aero
        assert 'C_eff' in aero

    def test_F0_positive(self):
        """Test that F0 is positive."""
        aero = calculate_aerodynamic_parameters(1.225, 15.0, 0.04, -0.15, 100.0)
        assert aero['F0'] > 0

    def test_F0_increases_with_wind_speed(self):
        """Test that F0 increases with wind speed squared."""
        aero_1 = calculate_aerodynamic_parameters(1.225, 10.0, 0.04, -0.15, 100.0)
        aero_2 = calculate_aerodynamic_parameters(1.225, 20.0, 0.04, -0.15, 100.0)

        # F0 should scale with V^2
        ratio = aero_2['F0'] / aero_1['F0']
        assert np.isclose(ratio, 4.0, rtol=0.01)

    def test_alpha_value(self):
        """Test that alpha has expected value."""
        aero = calculate_aerodynamic_parameters(1.225, 15.0, 0.04, -0.15, 100.0)
        assert aero['alpha'] == 2.0


class TestCreateDeviceConfiguration:
    """Test device configuration creation."""

    def test_correct_number_of_devices(self):
        """Test that correct number of devices is created."""
        for n in [2, 4, 6]:
            devices = create_device_configuration(n, 100.0, 5.0, 0.15, 200, 15)
            assert len(devices) == n

    def test_device_properties(self):
        """Test that each device has required properties."""
        devices = create_device_configuration(4, 100.0, 5.0, 0.15, 200, 15)

        for device in devices:
            assert 'id' in device
            assert 'position' in device
            assert 'mass' in device
            assert 'snap_threshold' in device
            assert 'snap_force' in device
            assert 'snap_energy' in device
            assert 'state' in device
            assert 'last_position' in device
            assert 'snap_count' in device

    def test_uniform_placement(self):
        """Test uniform device placement."""
        L = 100.0
        devices = create_device_configuration(4, L, 5.0, 0.15, 200, 15, 'uniform')

        # Check devices are within span
        for device in devices:
            assert 0 < device['position'] < L

        # Check spacing is approximately uniform
        positions = sorted([d['position'] for d in devices])
        spacings = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
        avg_spacing = np.mean(spacings)

        for spacing in spacings:
            assert np.isclose(spacing, avg_spacing, rtol=0.01)

    def test_device_initial_state(self):
        """Test that devices start with initial state."""
        devices = create_device_configuration(4, 100.0, 5.0, 0.15, 200, 15)

        for device in devices:
            assert device['state'] in [-1, 1]
            assert device['snap_count'] == 0
            assert device['last_position'] == 0.0

    def test_quarter_placement_two_devices(self):
        """Test quarter point placement for 2 devices."""
        L = 100.0
        devices = create_device_configuration(2, L, 5.0, 0.15, 200, 15, 'quarter')

        positions = [d['position'] for d in devices]
        assert np.isclose(positions[0], L/4, rtol=0.01)
        assert np.isclose(positions[1], 3*L/4, rtol=0.01)

    def test_quarter_placement_four_devices(self):
        """Test quarter point placement for 4 devices."""
        L = 100.0
        devices = create_device_configuration(4, L, 5.0, 0.15, 200, 15, 'quarter')

        positions = sorted([d['position'] for d in devices])
        assert np.isclose(positions[0], L/4, rtol=0.01)
        assert np.isclose(positions[1], L/2, rtol=0.01)
        assert np.isclose(positions[2], 3*L/4, rtol=0.01)


class TestGetFullParameters:
    """Test full parameter generation."""

    def test_parameter_structure(self):
        """Test that full parameters have all required keys."""
        params = get_full_parameters(num_devices=4)

        required_keys = [
            'conductor_diameter', 'conductor_mass', 'tension', 'span_length',
            'ice_thickness', 'ice_mass', 'iced_diameter', 'm_total',
            'M', 'K', 'C', 'omega_n', 'f_n', 'zeta',
            'wind_speed', 'air_density', 'F0', 'alpha', 'C_eff',
            'devices', 'num_devices', 'dt', 'T_sim'
        ]

        for key in required_keys:
            assert key in params, f"Missing key: {key}"

    def test_parameter_consistency(self):
        """Test that parameters are internally consistent."""
        params = get_full_parameters(num_devices=4)

        # Check number of devices matches
        assert len(params['devices']) == params['num_devices']

        # Check total mass equals conductor + ice
        assert np.isclose(params['m_total'],
                         params['conductor_mass'] + params['ice_mass'],
                         rtol=1e-10)

    def test_custom_device_count(self):
        """Test custom device count."""
        for n in [2, 3, 4, 5, 6]:
            params = get_full_parameters(num_devices=n)
            assert params['num_devices'] == n
            assert len(params['devices']) == n

    def test_custom_snap_threshold(self):
        """Test custom snap threshold."""
        threshold = 0.20
        params = get_full_parameters(num_devices=4, snap_threshold=threshold)

        for device in params['devices']:
            assert device['snap_threshold'] == threshold

    def test_custom_snap_force(self):
        """Test custom snap force."""
        force = 250
        params = get_full_parameters(num_devices=4, snap_force=force)

        for device in params['devices']:
            assert device['snap_force'] == force

    def test_no_devices(self):
        """Test parameters with zero devices."""
        params = get_full_parameters(num_devices=0)

        assert params['num_devices'] == 0
        assert len(params['devices']) == 0


class TestPrintParameterSummary:
    """Test parameter summary printing."""

    def test_print_runs_without_error(self):
        """Test that print function runs without error."""
        params = get_full_parameters(num_devices=4)

        # Should not raise any exceptions
        try:
            print_parameter_summary(params)
        except Exception as e:
            pytest.fail(f"print_parameter_summary raised exception: {e}")

    def test_print_with_no_devices(self):
        """Test print with zero devices."""
        params = get_full_parameters(num_devices=0)

        try:
            print_parameter_summary(params)
        except Exception as e:
            pytest.fail(f"print_parameter_summary with no devices raised exception: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
