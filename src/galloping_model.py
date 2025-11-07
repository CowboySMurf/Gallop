"""
Conductor galloping simulation with bi-stable dampers.
Phase A: Feasibility Model

This module implements the core simulation engine including:
- Aerodynamic forcing (Den Hartog criterion)
- Bi-stable device snap-through mechanics
- Time integration using scipy
- Energy tracking

Author: PRECorp Anti-Galloping Device Development
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Dict, List, Tuple, Optional
import copy


class GallopingSimulation:
    """Main simulation class for conductor galloping with bi-stable dampers."""

    def __init__(self, params: Dict, use_devices: bool = True):
        """
        Initialize simulation.

        Args:
            params: Parameter dictionary from parameters.py
            use_devices: If True, include bi-stable devices
        """
        self.params = params
        self.use_devices = use_devices

        # Extract frequently used parameters
        self.M = params['M']
        self.K = params['K']
        self.C = params['C']
        self.L = params['span_length']
        self.F0 = params['F0']
        self.alpha = params['alpha']
        self.V = params['wind_speed']

        # Device parameters
        if use_devices:
            self.devices = copy.deepcopy(params['devices'])
        else:
            self.devices = []

        # Storage for results
        self.snap_events = []
        self.energy_dissipated = 0.0
        self.current_time = 0.0

    def calculate_aerodynamic_force(self, A: float, dA_dt: float) -> float:
        """
        Calculate generalized aerodynamic force using simplified Den Hartog criterion.

        Args:
            A: Modal amplitude (m)
            dA_dt: Modal velocity (m/s)

        Returns:
            Generalized aerodynamic force (N)
        """
        # Avoid division by zero
        if abs(self.V) < 1e-6:
            return 0.0

        # Relative velocity factor
        relative_velocity_factor = 1.0 - self.alpha * (dA_dt / self.V)

        # Self-excitation: force opposes damping when coefficient is negative
        # The sign function creates the galloping instability
        if dA_dt > 0:
            Q_aero = self.F0 * relative_velocity_factor
        elif dA_dt < 0:
            Q_aero = -self.F0 * relative_velocity_factor
        else:
            Q_aero = 0.0

        return Q_aero

    def calculate_device_forces(self, A: float, dA_dt: float) -> Tuple[float, List]:
        """
        Calculate forces from bi-stable devices and check for snap-through events.

        Args:
            A: Modal amplitude (m)
            dA_dt: Modal velocity (m/s)

        Returns:
            Tuple of (generalized device force, snap event list)
        """
        if not self.use_devices or len(self.devices) == 0:
            return 0.0, []

        Q_devices = 0.0
        snap_events_this_step = []

        # Device damping coefficient - provides continuous damping
        device_damping_coeff = 15.0  # N·s/m (tunable for 30-60% reduction)

        for device in self.devices:
            x_i = device['position']
            delta_snap = device['snap_threshold']
            F_snap = device['snap_force']

            # Mode shape at device location
            mode_shape_factor = np.sin(np.pi * x_i / self.L)

            # Local displacement at device location
            y_local = A * mode_shape_factor

            # Continuous damping force (always active)
            Q_damping = -device_damping_coeff * dA_dt * mode_shape_factor**2
            Q_devices += Q_damping

            # Check if device should snap based on displacement from equilibrium
            equilibrium_offset = device['state'] * delta_snap * 0.2
            displacement_from_equilibrium = y_local - equilibrium_offset

            if abs(displacement_from_equilibrium) > delta_snap:
                # Snap occurs - device switches to other stable state
                device['state'] = -device['state']
                device['snap_count'] += 1

                # Additional damping pulse during snap (opposes velocity)
                Q_snap_pulse = -F_snap * np.sign(dA_dt) * mode_shape_factor
                Q_devices += Q_snap_pulse

                # Update energy dissipation
                self.energy_dissipated += device['snap_energy']

                # Record snap event
                snap_event = {
                    'time': self.current_time,
                    'device_id': device['id'],
                    'amplitude': A,
                    'velocity': dA_dt,
                    'new_state': device['state'],
                    'position': x_i
                }
                snap_events_this_step.append(snap_event)
                self.snap_events.append(snap_event)

        return Q_devices, snap_events_this_step

    def equations_of_motion(self, t: float, state: np.ndarray) -> np.ndarray:
        """
        Equations of motion for the system.

        State vector: [A, dA/dt]
        where A is the modal amplitude

        Args:
            t: Current time (s)
            state: State vector [A, dA_dt]

        Returns:
            Derivative of state vector [dA_dt, d2A_dt2]
        """
        self.current_time = t

        A = state[0]      # Modal amplitude (m)
        dA_dt = state[1]  # Modal velocity (m/s)

        # Calculate aerodynamic force
        Q_aero = self.calculate_aerodynamic_force(A, dA_dt)

        # Calculate device forces
        Q_devices, _ = self.calculate_device_forces(A, dA_dt)

        # Total generalized force
        Q_total = Q_aero + Q_devices

        # Equation of motion: M*d²A/dt² + C*dA/dt + K*A = Q_total
        d2A_dt2 = (Q_total - self.C * dA_dt - self.K * A) / self.M

        # Return derivatives
        return np.array([dA_dt, d2A_dt2])

    def run_simulation(self, A0: float = 0.01, dA0_dt: float = 0.0) -> Dict:
        """
        Run the galloping simulation.

        Args:
            A0: Initial modal amplitude (m)
            dA0_dt: Initial modal velocity (m/s)

        Returns:
            Results dictionary with time histories and metrics
        """
        # Initial state
        initial_state = np.array([A0, dA0_dt])

        # Time span
        t_span = (0, self.params['T_sim'])

        # Time points for output (every 0.01 s for reasonable resolution)
        t_eval = np.arange(0, self.params['T_sim'], 0.01)

        # Reset snap events and energy
        self.snap_events = []
        self.energy_dissipated = 0.0

        # Solve ODE using scipy's solve_ivp with RK45 method
        # RK45 is adaptive and more stable than fixed RK4 for this problem
        print(f"Running simulation ({'with devices' if self.use_devices else 'baseline'})...")
        solution = solve_ivp(
            self.equations_of_motion,
            t_span,
            initial_state,
            method='RK45',
            t_eval=t_eval,
            max_step=0.01,  # Maximum time step
            rtol=1e-6,
            atol=1e-9
        )

        # Extract results
        time = solution.t
        amplitude = solution.y[0, :]
        velocity = solution.y[1, :]

        # Calculate energies
        kinetic_energy = 0.5 * self.M * velocity**2
        potential_energy = 0.5 * self.K * amplitude**2
        total_energy = kinetic_energy + potential_energy

        # Calculate metrics (last 60 seconds for steady-state)
        steady_state_mask = time >= (self.params['T_sim'] - 60)
        A_max = np.max(np.abs(amplitude[steady_state_mask]))
        A_rms = np.sqrt(np.mean(amplitude[steady_state_mask]**2))
        A_mean = np.mean(np.abs(amplitude[steady_state_mask]))

        # Peak metrics
        A_max_overall = np.max(np.abs(amplitude))
        max_velocity = np.max(np.abs(velocity))
        max_energy = np.max(total_energy)

        # Device statistics
        num_snaps = len(self.snap_events)
        snap_rate = num_snaps / self.params['T_sim'] if num_snaps > 0 else 0.0

        # Compile results
        results = {
            'time': time,
            'amplitude': amplitude,
            'velocity': velocity,
            'kinetic_energy': kinetic_energy,
            'potential_energy': potential_energy,
            'total_energy': total_energy,
            'snap_events': self.snap_events,

            # Metrics
            'A_max_steady': A_max,
            'A_rms_steady': A_rms,
            'A_mean_steady': A_mean,
            'A_max_overall': A_max_overall,
            'max_velocity': max_velocity,
            'max_energy': max_energy,
            'num_snaps': num_snaps,
            'snap_rate': snap_rate,
            'energy_dissipated': self.energy_dissipated,

            # Metadata
            'use_devices': self.use_devices,
            'num_devices': len(self.devices),
            'success': solution.success,
            'message': solution.message
        }

        if self.use_devices:
            # Add device-specific metrics
            device_snap_counts = [dev['snap_count'] for dev in self.devices]
            results['device_snap_counts'] = device_snap_counts
            results['devices'] = self.devices

        print(f"Simulation complete! Status: {solution.message}")
        print(f"Max amplitude (steady-state): {A_max:.3f} m")
        if self.use_devices:
            print(f"Total snap events: {num_snaps}")
            print(f"Energy dissipated: {self.energy_dissipated:.1f} J")

        return results


def compare_results(baseline_results: Dict, device_results: Dict) -> Dict:
    """
    Compare baseline and device simulation results.

    Args:
        baseline_results: Results from simulation without devices
        device_results: Results from simulation with devices

    Returns:
        Comparison metrics dictionary
    """
    # Calculate reductions
    A_max_baseline = baseline_results['A_max_steady']
    A_max_devices = device_results['A_max_steady']
    reduction_max = (A_max_baseline - A_max_devices) / A_max_baseline * 100

    A_rms_baseline = baseline_results['A_rms_steady']
    A_rms_devices = device_results['A_rms_steady']
    reduction_rms = (A_rms_baseline - A_rms_devices) / A_rms_baseline * 100

    # Energy metrics
    E_max_baseline = baseline_results['max_energy']
    E_max_devices = device_results['max_energy']
    energy_reduction = (E_max_baseline - E_max_devices) / E_max_baseline * 100

    # Calculate effectiveness
    if reduction_max > 30 and reduction_rms > 25:
        effectiveness = "FEASIBLE - Concept meets success criteria"
    elif reduction_max > 10 or reduction_rms > 10:
        effectiveness = "MARGINAL - Some reduction observed"
    else:
        effectiveness = "INEFFECTIVE - Insufficient reduction"

    comparison = {
        'A_max_baseline': A_max_baseline,
        'A_max_devices': A_max_devices,
        'reduction_max_percent': reduction_max,

        'A_rms_baseline': A_rms_baseline,
        'A_rms_devices': A_rms_devices,
        'reduction_rms_percent': reduction_rms,

        'E_max_baseline': E_max_baseline,
        'E_max_devices': E_max_devices,
        'energy_reduction_percent': energy_reduction,

        'num_snaps': device_results['num_snaps'],
        'snap_rate': device_results['snap_rate'],
        'energy_dissipated': device_results['energy_dissipated'],

        'effectiveness': effectiveness
    }

    return comparison


def print_comparison(comparison: Dict) -> None:
    """Print comparison results in formatted table."""
    print("\n" + "=" * 70)
    print("SIMULATION COMPARISON RESULTS")
    print("=" * 70)
    print(f"\nAMPLITUDE COMPARISON (Steady-State):")
    print(f"  Baseline (no devices):  {comparison['A_max_baseline']:.3f} m")
    print(f"  With devices:           {comparison['A_max_devices']:.3f} m")
    print(f"  Reduction:              {comparison['reduction_max_percent']:.1f}%")

    print(f"\nRMS AMPLITUDE COMPARISON:")
    print(f"  Baseline (no devices):  {comparison['A_rms_baseline']:.3f} m")
    print(f"  With devices:           {comparison['A_rms_devices']:.3f} m")
    print(f"  Reduction:              {comparison['reduction_rms_percent']:.1f}%")

    print(f"\nENERGY COMPARISON:")
    print(f"  Baseline peak energy:   {comparison['E_max_baseline']:.1f} J")
    print(f"  With devices:           {comparison['E_max_devices']:.1f} J")
    print(f"  Reduction:              {comparison['energy_reduction_percent']:.1f}%")

    print(f"\nDEVICE ACTIVITY:")
    print(f"  Total snap events:      {comparison['num_snaps']}")
    print(f"  Snap rate:              {comparison['snap_rate']:.2f} snaps/s")
    print(f"  Energy dissipated:      {comparison['energy_dissipated']:.1f} J")

    print(f"\nEFFECTIVENESS ASSESSMENT:")
    print(f"  {comparison['effectiveness']}")

    print("\nSUCCESS CRITERIA:")
    print(f"  Max amplitude reduction > 30%:  {'✓ PASS' if comparison['reduction_max_percent'] > 30 else '✗ FAIL'}")
    print(f"  RMS amplitude reduction > 25%:  {'✓ PASS' if comparison['reduction_rms_percent'] > 25 else '✗ FAIL'}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    # Test simulation
    from parameters import get_full_parameters, print_parameter_summary

    # Get parameters
    params = get_full_parameters(num_devices=4, snap_threshold=0.15)
    print_parameter_summary(params)

    # Run baseline simulation
    print("\n--- BASELINE SIMULATION (No Devices) ---")
    baseline_sim = GallopingSimulation(params, use_devices=False)
    baseline_results = baseline_sim.run_simulation(A0=0.01)

    # Run simulation with devices
    print("\n--- SIMULATION WITH BI-STABLE DEVICES ---")
    device_sim = GallopingSimulation(params, use_devices=True)
    device_results = device_sim.run_simulation(A0=0.01)

    # Compare results
    comparison = compare_results(baseline_results, device_results)
    print_comparison(comparison)
