"""
Physical parameter calculations for conductor galloping simulation.
Phase A: Bi-Stable Damper Feasibility Model

Author: PRECorp Anti-Galloping Device Development
"""

import numpy as np
from typing import Dict, List


class ConductorParameters:
    """336.4 kcmil Merlin ACSR conductor properties"""

    # Conductor properties
    diameter_inches = 0.721  # inches
    diameter = 0.721 * 0.0254  # meters
    mass_per_length_imperial = 0.644  # lb/ft
    mass_per_length = 0.644 * 1.48816  # kg/m
    rated_breaking_strength = 17300  # lbs
    tension_lbs = 4000  # lbs (typical 20% RBS)
    tension = 4000 * 4.44822  # N

    # Span
    span_length_ft = 300  # ft
    span_length = 300 * 0.3048  # m


class EnvironmentalParameters:
    """Ice and wind conditions"""

    # Ice properties
    ice_thickness_inches = 0.5  # inches
    ice_thickness = 0.5 * 0.0254  # m
    ice_density = 900  # kg/m³

    # Effective diameter with ice
    iced_diameter_inches = 0.721 + 2 * 0.5  # inches
    iced_diameter = iced_diameter_inches * 0.0254  # m

    # Wind
    wind_speed_mph = 30  # mph
    wind_speed = 30 * 0.44704  # m/s

    # Air
    air_density = 1.225  # kg/m³ (sea level, 15°C)

    # Aerodynamic coefficients (crescent ice)
    # For galloping, we need the Den Hartog coefficient: dC_L/dα + C_D < 0
    # Using an effective combined coefficient for galloping instability
    # Reduced value for more realistic galloping amplitudes (2-5m range)
    C_eff = -0.15  # Combined galloping coefficient (negative for instability)


class DeviceParameters:
    """Bi-stable device properties"""

    num_devices = 4
    device_mass = 5.0  # kg per unit
    snap_threshold = 0.15  # m (6 inches)
    snap_force = 200  # N
    snap_energy = 15  # J
    beam_frequency = 5  # Hz


def calculate_ice_mass(conductor_diameter: float, ice_thickness: float,
                       ice_density: float) -> float:
    """
    Calculate additional mass per unit length from ice accumulation.

    Args:
        conductor_diameter: Base conductor diameter (m)
        ice_thickness: Ice thickness (m)
        ice_density: Ice density (kg/m³)

    Returns:
        Ice mass per unit length (kg/m)
    """
    d = conductor_diameter
    t = ice_thickness

    # Cross-sectional area of ice (annulus)
    area_ice = np.pi * ((d/2 + t)**2 - (d/2)**2)

    # Mass per unit length
    m_ice = ice_density * area_ice

    return m_ice


def calculate_modal_properties(m_total: float, span_length: float,
                                tension: float, damping_ratio: float = 0.001) -> Dict:
    """
    Calculate modal properties for fundamental mode.

    Args:
        m_total: Total mass per unit length (kg/m)
        span_length: Span length (m)
        tension: Conductor tension (N)
        damping_ratio: Structural damping ratio (dimensionless)

    Returns:
        Dictionary with modal properties
    """
    L = span_length
    T = tension

    # Modal properties for fundamental mode (first mode)
    M = (m_total * L) / 2  # Modal mass (kg)
    K = (np.pi**2 / L**2) * T * (L / 2)  # Modal stiffness (N/m)

    omega_n = np.sqrt(K / M)  # Natural frequency (rad/s)
    f_n = omega_n / (2 * np.pi)  # Natural frequency (Hz)

    C = damping_ratio * 2 * np.sqrt(K * M)  # Damping coefficient (N·s/m)

    return {
        'M': M,           # Modal mass (kg)
        'K': K,           # Modal stiffness (N/m)
        'C': C,           # Modal damping (N·s/m)
        'omega_n': omega_n,  # Natural frequency (rad/s)
        'f_n': f_n,       # Natural frequency (Hz)
        'zeta': damping_ratio  # Damping ratio
    }


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
    L = span_length
    V = wind_speed
    D = iced_diameter
    rho = air_density

    # Generalized aerodynamic force amplitude
    # Note: C_eff is negative for galloping, use abs() for magnitude
    F0 = 0.5 * rho * V**2 * D * abs(C_eff) * (L / np.pi)

    # Aerodynamic coupling coefficient (typical for galloping)
    alpha = 2.0

    return {
        'F0': F0,      # Base aerodynamic force (N)
        'alpha': alpha,  # Coupling coefficient
        'C_eff': C_eff   # Combined aero coefficient
    }


def create_device_configuration(num_devices: int, span_length: float,
                                 device_mass: float, snap_threshold: float,
                                 snap_force: float, snap_energy: float,
                                 placement: str = 'uniform') -> List[Dict]:
    """
    Create configuration for bi-stable devices.

    Args:
        num_devices: Number of devices
        span_length: Span length (m)
        device_mass: Mass per device (kg)
        snap_threshold: Displacement threshold for snap (m)
        snap_force: Force during snap event (N)
        snap_energy: Energy dissipated per snap (J)
        placement: Placement strategy ('uniform', 'center', 'quarter')

    Returns:
        List of device dictionaries
    """
    devices = []
    L = span_length

    if placement == 'uniform':
        # Evenly spaced along span
        positions = [L * (i + 1) / (num_devices + 1) for i in range(num_devices)]
    elif placement == 'center':
        # Clustered near center
        positions = [L/2 + (i - num_devices/2) * L/20 for i in range(num_devices)]
    elif placement == 'quarter':
        # At quarter points
        if num_devices == 2:
            positions = [L/4, 3*L/4]
        elif num_devices == 4:
            positions = [L/4, L/2, 3*L/4, L]
        else:
            # Default to uniform
            positions = [L * (i + 1) / (num_devices + 1) for i in range(num_devices)]
    else:
        # Default to uniform
        positions = [L * (i + 1) / (num_devices + 1) for i in range(num_devices)]

    for i, x_i in enumerate(positions):
        devices.append({
            'id': i,
            'position': x_i,
            'mass': device_mass,
            'snap_threshold': snap_threshold,
            'snap_force': snap_force,
            'snap_energy': snap_energy,
            'state': 1,  # Initial state (+1 or -1)
            'last_position': 0.0,  # Last displacement at this location
            'snap_count': 0
        })

    return devices


def get_full_parameters(num_devices: int = 4, snap_threshold: float = 0.15,
                        snap_force: float = 200, device_placement: str = 'uniform') -> Dict:
    """
    Get complete parameter set for simulation.

    Args:
        num_devices: Number of bi-stable devices
        snap_threshold: Snap threshold displacement (m)
        snap_force: Force during snap (N)
        device_placement: Device placement strategy

    Returns:
        Complete parameter dictionary
    """
    # Initialize parameter classes
    conductor = ConductorParameters()
    environment = EnvironmentalParameters()
    device = DeviceParameters()

    # Calculate ice mass
    m_ice = calculate_ice_mass(conductor.diameter, environment.ice_thickness,
                                environment.ice_density)

    # Total mass per length
    m_total = conductor.mass_per_length + m_ice

    # Calculate modal properties
    # Using slightly higher damping ratio for more realistic galloping amplitudes
    modal = calculate_modal_properties(m_total, conductor.span_length,
                                        conductor.tension, damping_ratio=0.003)

    # Calculate aerodynamic parameters
    aero = calculate_aerodynamic_parameters(environment.air_density,
                                             environment.wind_speed,
                                             environment.iced_diameter,
                                             environment.C_eff,
                                             conductor.span_length)

    # Create device configuration
    devices = create_device_configuration(num_devices, conductor.span_length,
                                          device.device_mass, snap_threshold,
                                          snap_force, device.snap_energy,
                                          device_placement)

    # Compile all parameters
    params = {
        # Conductor
        'conductor_diameter': conductor.diameter,
        'conductor_mass': conductor.mass_per_length,
        'tension': conductor.tension,
        'span_length': conductor.span_length,

        # Ice
        'ice_thickness': environment.ice_thickness,
        'ice_mass': m_ice,
        'iced_diameter': environment.iced_diameter,

        # Total
        'm_total': m_total,

        # Modal properties
        'M': modal['M'],
        'K': modal['K'],
        'C': modal['C'],
        'omega_n': modal['omega_n'],
        'f_n': modal['f_n'],
        'zeta': modal['zeta'],

        # Aerodynamic
        'wind_speed': environment.wind_speed,
        'air_density': environment.air_density,
        'F0': aero['F0'],
        'alpha': aero['alpha'],
        'C_eff': aero['C_eff'],

        # Devices
        'devices': devices,
        'num_devices': num_devices,

        # Simulation
        'dt': 0.001,  # Time step (s)
        'T_sim': 60.0  # Simulation duration (s) - reduced for faster Phase A results
    }

    return params


def print_parameter_summary(params: Dict) -> None:
    """Print summary of simulation parameters."""
    print("=" * 70)
    print("CONDUCTOR GALLOPING SIMULATION - PARAMETER SUMMARY")
    print("=" * 70)
    print(f"\nCONDUCTOR PROPERTIES:")
    print(f"  Span Length: {params['span_length']:.2f} m ({params['span_length']/0.3048:.1f} ft)")
    print(f"  Tension: {params['tension']:.1f} N ({params['tension']/4.44822:.1f} lbs)")
    print(f"  Conductor Mass: {params['conductor_mass']:.3f} kg/m")
    print(f"  Ice Mass: {params['ice_mass']:.3f} kg/m")
    print(f"  Total Mass: {params['m_total']:.3f} kg/m")
    print(f"  Iced Diameter: {params['iced_diameter']*1000:.1f} mm ({params['iced_diameter']/0.0254:.2f} in)")

    print(f"\nMODAL PROPERTIES:")
    print(f"  Modal Mass (M): {params['M']:.1f} kg")
    print(f"  Modal Stiffness (K): {params['K']:.1f} N/m")
    print(f"  Damping Coefficient (C): {params['C']:.3f} N·s/m")
    print(f"  Natural Frequency: {params['f_n']:.3f} Hz")
    print(f"  Damping Ratio: {params['zeta']:.4f}")

    print(f"\nAERODYNAMIC CONDITIONS:")
    print(f"  Wind Speed: {params['wind_speed']:.2f} m/s ({params['wind_speed']/0.44704:.1f} mph)")
    print(f"  Air Density: {params['air_density']:.3f} kg/m³")
    print(f"  Aero Coefficient (C_eff): {params['C_eff']:.2f}")
    print(f"  Base Aero Force (F0): {params['F0']:.1f} N")

    print(f"\nBI-STABLE DEVICES:")
    print(f"  Number of Devices: {params['num_devices']}")
    if params['num_devices'] > 0:
        print(f"  Snap Threshold: {params['devices'][0]['snap_threshold']:.3f} m ({params['devices'][0]['snap_threshold']/0.0254:.1f} in)")
        print(f"  Snap Force: {params['devices'][0]['snap_force']:.1f} N")
        print(f"  Energy per Snap: {params['devices'][0]['snap_energy']:.1f} J")
        print(f"  Device Positions:")
        for dev in params['devices']:
            print(f"    Device {dev['id']}: {dev['position']:.2f} m ({dev['position']/params['span_length']*100:.1f}% of span)")

    print(f"\nSIMULATION SETTINGS:")
    print(f"  Time Step: {params['dt']*1000:.1f} ms")
    print(f"  Duration: {params['T_sim']:.1f} s")
    print(f"  Number of Steps: {int(params['T_sim']/params['dt'])}")
    print("=" * 70)
    print()


if __name__ == "__main__":
    # Test parameter calculation
    params = get_full_parameters(num_devices=4, snap_threshold=0.15)
    print_parameter_summary(params)
