"""
Visualization and analysis functions for galloping simulation results.
Phase A: Bi-Stable Damper Feasibility Model

Author: PRECorp Anti-Galloping Device Development
"""

import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Optional
import os


def setup_plot_style():
    """Configure matplotlib for professional plots."""
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['axes.titlesize'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['grid.alpha'] = 0.3


def plot_time_history(results: Dict, title: str = "Amplitude vs Time",
                      save_path: Optional[str] = None, show_snaps: bool = True):
    """
    Plot amplitude time history.

    Args:
        results: Simulation results dictionary
        title: Plot title
        save_path: Path to save figure (if None, don't save)
        show_snaps: Show snap events as vertical lines
    """
    fig, ax = plt.subplots(figsize=(14, 6))

    time = results['time']
    amplitude = results['amplitude']

    # Plot amplitude
    ax.plot(time, amplitude, 'b-', linewidth=1.5, label='Amplitude')
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)

    # Mark snap events
    if show_snaps and results['use_devices'] and len(results['snap_events']) > 0:
        snap_times = [event['time'] for event in results['snap_events']]
        snap_amplitudes = [event['amplitude'] for event in results['snap_events']]
        ax.plot(snap_times, snap_amplitudes, 'r|', markersize=10,
                markeredgewidth=1.5, label=f"Snap Events (n={len(snap_times)})")

    # Formatting
    ax.set_xlabel('Time (s)', fontsize=12)
    ax.set_ylabel('Modal Amplitude (m)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    # Add annotations
    max_amp = np.max(np.abs(amplitude))
    ax.text(0.02, 0.98, f'Max Amplitude: {max_amp:.3f} m\nRMS: {results["A_rms_steady"]:.3f} m',
            transform=ax.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_comparison_time_history(baseline_results: Dict, device_results: Dict,
                                  save_path: Optional[str] = None):
    """
    Plot baseline vs device results on same axes.

    Args:
        baseline_results: Results from baseline simulation
        device_results: Results from simulation with devices
        save_path: Path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    # Full time history
    ax1.plot(baseline_results['time'], baseline_results['amplitude'],
             'b-', linewidth=1.5, label='Baseline (No Devices)', alpha=0.7)
    ax1.plot(device_results['time'], device_results['amplitude'],
             'r-', linewidth=1.5, label=f'With {device_results["num_devices"]} Devices', alpha=0.7)

    # Mark snap events
    if len(device_results['snap_events']) > 0:
        snap_times = [event['time'] for event in device_results['snap_events']]
        snap_amplitudes = [event['amplitude'] for event in device_results['snap_events']]
        ax1.plot(snap_times, snap_amplitudes, 'g|', markersize=8,
                markeredgewidth=1, alpha=0.5, label='Snap Events')

    ax1.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Modal Amplitude (m)', fontsize=12)
    ax1.set_title('Comparison: Baseline vs With Devices - Full Time History',
                  fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')

    # Zoomed steady-state comparison (last 30 seconds)
    t_start = baseline_results['time'][-1] - 30
    mask_baseline = baseline_results['time'] >= t_start
    mask_device = device_results['time'] >= t_start

    ax2.plot(baseline_results['time'][mask_baseline],
             baseline_results['amplitude'][mask_baseline],
             'b-', linewidth=1.5, label='Baseline (No Devices)', alpha=0.7)
    ax2.plot(device_results['time'][mask_device],
             device_results['amplitude'][mask_device],
             'r-', linewidth=1.5, label=f'With {device_results["num_devices"]} Devices', alpha=0.7)

    # Mark snap events in zoomed view
    if len(device_results['snap_events']) > 0:
        snap_times_zoomed = [event['time'] for event in device_results['snap_events']
                             if event['time'] >= t_start]
        snap_amps_zoomed = [event['amplitude'] for event in device_results['snap_events']
                           if event['time'] >= t_start]
        ax2.plot(snap_times_zoomed, snap_amps_zoomed, 'g|', markersize=8,
                markeredgewidth=1, alpha=0.5, label='Snap Events')

    ax2.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Modal Amplitude (m)', fontsize=12)
    ax2.set_title('Steady-State Comparison (Last 30 seconds)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best')

    # Add reduction percentage
    reduction = (baseline_results['A_max_steady'] - device_results['A_max_steady']) / \
                baseline_results['A_max_steady'] * 100
    ax2.text(0.02, 0.98, f'Amplitude Reduction: {reduction:.1f}%',
            transform=ax2.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='lightgreen' if reduction > 30 else 'wheat', alpha=0.7),
            fontsize=12, fontweight='bold')

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, (ax1, ax2)


def plot_phase_portrait(results: Dict, title: str = "Phase Portrait",
                        save_path: Optional[str] = None):
    """
    Plot phase portrait (amplitude vs velocity).

    Args:
        results: Simulation results dictionary
        title: Plot title
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    amplitude = results['amplitude']
    velocity = results['velocity']

    # Color by time (early = blue, late = red)
    time_normalized = results['time'] / results['time'][-1]
    scatter = ax.scatter(amplitude, velocity, c=time_normalized, cmap='viridis',
                        s=1, alpha=0.6)

    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Normalized Time', fontsize=11)

    # Formatting
    ax.set_xlabel('Modal Amplitude (m)', fontsize=12)
    ax.set_ylabel('Modal Velocity (m/s)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)
    ax.axvline(x=0, color='k', linestyle='--', linewidth=0.5, alpha=0.5)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_energy_history(results: Dict, title: str = "Energy vs Time",
                        save_path: Optional[str] = None):
    """
    Plot energy time history.

    Args:
        results: Simulation results dictionary
        title: Plot title
        save_path: Path to save figure
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    time = results['time']
    kinetic = results['kinetic_energy']
    potential = results['potential_energy']
    total = results['total_energy']

    # Energy components
    ax1.plot(time, kinetic, 'r-', linewidth=1.5, label='Kinetic Energy', alpha=0.7)
    ax1.plot(time, potential, 'b-', linewidth=1.5, label='Potential Energy', alpha=0.7)
    ax1.plot(time, total, 'k-', linewidth=2, label='Total Energy')

    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Energy (J)', fontsize=12)
    ax1.set_title('Energy Components', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='best')

    # Total energy with dissipation annotation
    ax2.plot(time, total, 'k-', linewidth=2, label='Total Mechanical Energy')

    if results['use_devices'] and results['energy_dissipated'] > 0:
        ax2.axhline(y=results['energy_dissipated'], color='r', linestyle='--',
                   linewidth=2, label=f'Energy Dissipated by Devices: {results["energy_dissipated"]:.1f} J')

    ax2.set_xlabel('Time (s)', fontsize=12)
    ax2.set_ylabel('Energy (J)', fontsize=12)
    ax2.set_title(title, fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    ax2.legend(loc='best')

    # Add max energy annotation
    max_energy = np.max(total)
    ax2.text(0.02, 0.98, f'Max Total Energy: {max_energy:.1f} J',
            transform=ax2.transAxes, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, (ax1, ax2)


def plot_parametric_study(param_values: List, reductions_max: List, reductions_rms: List,
                          param_name: str, param_unit: str,
                          save_path: Optional[str] = None):
    """
    Plot parametric study results.

    Args:
        param_values: List of parameter values
        reductions_max: List of max amplitude reductions (%)
        reductions_rms: List of RMS amplitude reductions (%)
        param_name: Parameter name for labeling
        param_unit: Parameter unit for labeling
        save_path: Path to save figure
    """
    fig, ax = plt.subplots(figsize=(12, 7))

    ax.plot(param_values, reductions_max, 'bo-', linewidth=2, markersize=10,
            label='Max Amplitude Reduction', markerfacecolor='white', markeredgewidth=2)
    ax.plot(param_values, reductions_rms, 'rs-', linewidth=2, markersize=10,
            label='RMS Amplitude Reduction', markerfacecolor='white', markeredgewidth=2)

    # Add success criteria lines
    ax.axhline(y=30, color='g', linestyle='--', linewidth=2, alpha=0.5,
              label='Success Criterion (30% max)')
    ax.axhline(y=25, color='orange', linestyle='--', linewidth=2, alpha=0.5,
              label='Success Criterion (25% RMS)')

    ax.set_xlabel(f'{param_name} ({param_unit})', fontsize=12)
    ax.set_ylabel('Amplitude Reduction (%)', fontsize=12)
    ax.set_title(f'Parametric Study: Effectiveness vs {param_name}',
                fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')

    # Add value labels on points
    for i, (pv, rm, rr) in enumerate(zip(param_values, reductions_max, reductions_rms)):
        ax.text(pv, rm + 1, f'{rm:.1f}%', ha='center', fontsize=9)
        ax.text(pv, rr - 2, f'{rr:.1f}%', ha='center', fontsize=9)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, ax


def plot_device_activity(results: Dict, save_path: Optional[str] = None):
    """
    Plot device snap activity.

    Args:
        results: Simulation results with devices
        save_path: Path to save figure
    """
    if not results['use_devices'] or len(results['snap_events']) == 0:
        print("No device activity to plot.")
        return None, None

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

    snap_events = results['snap_events']
    num_devices = results['num_devices']

    # Snap events over time
    for device_id in range(num_devices):
        device_snaps = [e for e in snap_events if e['device_id'] == device_id]
        snap_times = [e['time'] for e in device_snaps]
        snap_device_ids = [e['device_id'] for e in device_snaps]

        if len(snap_times) > 0:
            ax1.plot(snap_times, snap_device_ids, 'o', markersize=6,
                    label=f'Device {device_id}', alpha=0.7)

    ax1.set_xlabel('Time (s)', fontsize=12)
    ax1.set_ylabel('Device ID', fontsize=12)
    ax1.set_title('Snap Event Timeline by Device', fontsize=13, fontweight='bold')
    ax1.set_yticks(range(num_devices))
    ax1.grid(True, alpha=0.3, axis='x')
    ax1.legend(loc='best', ncol=2)

    # Snap count histogram
    device_snap_counts = results['device_snap_counts']
    device_ids = range(len(device_snap_counts))

    bars = ax2.bar(device_ids, device_snap_counts, color='steelblue',
                   alpha=0.7, edgecolor='black', linewidth=1.5)

    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, device_snap_counts)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax2.set_xlabel('Device ID', fontsize=12)
    ax2.set_ylabel('Number of Snap Events', fontsize=12)
    ax2.set_title('Total Snap Events per Device', fontsize=13, fontweight='bold')
    ax2.set_xticks(device_ids)
    ax2.grid(True, alpha=0.3, axis='y')

    # Add total
    total_snaps = sum(device_snap_counts)
    ax2.text(0.98, 0.98, f'Total Snaps: {total_snaps}\nSnap Rate: {results["snap_rate"]:.2f} /s',
            transform=ax2.transAxes, verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.7),
            fontsize=11)

    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig, (ax1, ax2)


def create_summary_figure(baseline_results: Dict, device_results: Dict,
                          comparison: Dict, save_path: Optional[str] = None):
    """
    Create comprehensive summary figure with all key results.

    Args:
        baseline_results: Baseline simulation results
        device_results: Device simulation results
        comparison: Comparison metrics
        save_path: Path to save figure
    """
    fig = plt.figure(figsize=(18, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

    # 1. Time history comparison
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(baseline_results['time'], baseline_results['amplitude'],
             'b-', linewidth=1.5, label='Baseline', alpha=0.7)
    ax1.plot(device_results['time'], device_results['amplitude'],
             'r-', linewidth=1.5, label='With Devices', alpha=0.7)
    if len(device_results['snap_events']) > 0:
        snap_times = [e['time'] for e in device_results['snap_events']]
        snap_amps = [e['amplitude'] for e in device_results['snap_events']]
        ax1.plot(snap_times, snap_amps, 'g|', markersize=6, markeredgewidth=0.8, alpha=0.4)
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude (m)')
    ax1.set_title('Amplitude Comparison', fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()

    # 2. Phase portraits
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.scatter(baseline_results['amplitude'], baseline_results['velocity'],
                c='blue', s=0.5, alpha=0.3)
    ax2.set_xlabel('Amplitude (m)')
    ax2.set_ylabel('Velocity (m/s)')
    ax2.set_title('Baseline Phase Portrait', fontweight='bold')
    ax2.grid(True, alpha=0.3)

    ax3 = fig.add_subplot(gs[1, 1])
    ax3.scatter(device_results['amplitude'], device_results['velocity'],
                c='red', s=0.5, alpha=0.3)
    ax3.set_xlabel('Amplitude (m)')
    ax3.set_ylabel('Velocity (m/s)')
    ax3.set_title('With Devices Phase Portrait', fontweight='bold')
    ax3.grid(True, alpha=0.3)

    # 3. Energy comparison
    ax4 = fig.add_subplot(gs[1, 2])
    ax4.plot(baseline_results['time'], baseline_results['total_energy'],
             'b-', linewidth=1.5, label='Baseline', alpha=0.7)
    ax4.plot(device_results['time'], device_results['total_energy'],
             'r-', linewidth=1.5, label='With Devices', alpha=0.7)
    ax4.set_xlabel('Time (s)')
    ax4.set_ylabel('Total Energy (J)')
    ax4.set_title('Energy Comparison', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    ax4.legend()

    # 4. Metrics bar chart
    ax5 = fig.add_subplot(gs[2, 0])
    metrics = ['Max Amp\n(m)', 'RMS Amp\n(m)']
    baseline_vals = [baseline_results['A_max_steady'], baseline_results['A_rms_steady']]
    device_vals = [device_results['A_max_steady'], device_results['A_rms_steady']]

    x = np.arange(len(metrics))
    width = 0.35

    bars1 = ax5.bar(x - width/2, baseline_vals, width, label='Baseline',
                    color='blue', alpha=0.7)
    bars2 = ax5.bar(x + width/2, device_vals, width, label='With Devices',
                    color='red', alpha=0.7)

    ax5.set_ylabel('Value')
    ax5.set_title('Metric Comparison', fontweight='bold')
    ax5.set_xticks(x)
    ax5.set_xticklabels(metrics)
    ax5.legend()
    ax5.grid(True, alpha=0.3, axis='y')

    # 5. Reduction percentages
    ax6 = fig.add_subplot(gs[2, 1])
    reductions = ['Max Amp\nReduction', 'RMS Amp\nReduction', 'Energy\nReduction']
    reduction_vals = [comparison['reduction_max_percent'],
                      comparison['reduction_rms_percent'],
                      comparison['energy_reduction_percent']]

    bars = ax6.bar(reductions, reduction_vals, color=['green' if v > 30 else 'orange'
                   for v in reduction_vals], alpha=0.7, edgecolor='black', linewidth=1.5)

    ax6.axhline(y=30, color='green', linestyle='--', linewidth=2, alpha=0.5, label='Target (30%)')
    ax6.set_ylabel('Reduction (%)')
    ax6.set_title('Effectiveness Metrics', fontweight='bold')
    ax6.grid(True, alpha=0.3, axis='y')
    ax6.legend()

    # Add value labels
    for bar, val in zip(bars, reduction_vals):
        height = bar.get_height()
        ax6.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:.1f}%', ha='center', va='bottom', fontweight='bold')

    # 6. Summary text
    ax7 = fig.add_subplot(gs[2, 2])
    ax7.axis('off')

    summary_text = f"""SUMMARY

Device Configuration:
  • Number: {device_results['num_devices']}
  • Snap Events: {device_results['num_snaps']}
  • Snap Rate: {device_results['snap_rate']:.2f} /s

Effectiveness:
  • Max Reduction: {comparison['reduction_max_percent']:.1f}%
  • RMS Reduction: {comparison['reduction_rms_percent']:.1f}%

Energy:
  • Dissipated: {device_results['energy_dissipated']:.1f} J
  • Energy Reduction: {comparison['energy_reduction_percent']:.1f}%

Assessment:
  {comparison['effectiveness']}
"""

    ax7.text(0.1, 0.9, summary_text, transform=ax7.transAxes,
            verticalalignment='top', fontsize=11, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))

    # Main title
    fig.suptitle('Conductor Galloping with Bi-Stable Dampers - Phase A Results',
                fontsize=16, fontweight='bold')

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {save_path}")

    return fig


def save_results_to_file(comparison: Dict, baseline_results: Dict,
                         device_results: Dict, filename: str):
    """
    Save numerical results to text file.

    Args:
        comparison: Comparison metrics
        baseline_results: Baseline simulation results
        device_results: Device simulation results
        filename: Output filename
    """
    with open(filename, 'w') as f:
        f.write("="*70 + "\n")
        f.write("CONDUCTOR GALLOPING SIMULATION - PHASE A RESULTS\n")
        f.write("Bi-Stable Damper Feasibility Study\n")
        f.write("="*70 + "\n\n")

        f.write("BASELINE RESULTS (No Devices):\n")
        f.write(f"  Max Amplitude (steady-state): {baseline_results['A_max_steady']:.3f} m\n")
        f.write(f"  RMS Amplitude: {baseline_results['A_rms_steady']:.3f} m\n")
        f.write(f"  Max Energy: {baseline_results['max_energy']:.1f} J\n")
        f.write(f"  Natural Frequency: {baseline_results.get('frequency', 'N/A')} Hz\n\n")

        f.write("WITH DEVICES RESULTS:\n")
        f.write(f"  Number of Devices: {device_results['num_devices']}\n")
        f.write(f"  Max Amplitude (steady-state): {device_results['A_max_steady']:.3f} m\n")
        f.write(f"  RMS Amplitude: {device_results['A_rms_steady']:.3f} m\n")
        f.write(f"  Max Energy: {device_results['max_energy']:.1f} J\n")
        f.write(f"  Total Snap Events: {device_results['num_snaps']}\n")
        f.write(f"  Snap Rate: {device_results['snap_rate']:.2f} snaps/second\n")
        f.write(f"  Energy Dissipated: {device_results['energy_dissipated']:.1f} J\n\n")

        f.write("EFFECTIVENESS METRICS:\n")
        f.write(f"  Max Amplitude Reduction: {comparison['reduction_max_percent']:.1f}%\n")
        f.write(f"  RMS Amplitude Reduction: {comparison['reduction_rms_percent']:.1f}%\n")
        f.write(f"  Energy Reduction: {comparison['energy_reduction_percent']:.1f}%\n\n")

        f.write("SUCCESS CRITERIA:\n")
        f.write(f"  Max Reduction > 30%: {'PASS ✓' if comparison['reduction_max_percent'] > 30 else 'FAIL ✗'}\n")
        f.write(f"  RMS Reduction > 25%: {'PASS ✓' if comparison['reduction_rms_percent'] > 25 else 'FAIL ✗'}\n\n")

        f.write("OVERALL ASSESSMENT:\n")
        f.write(f"  {comparison['effectiveness']}\n")
        f.write("="*70 + "\n")

    print(f"Results saved to: {filename}")


if __name__ == "__main__":
    print("Visualization module loaded successfully.")
    print("Use with simulation results to generate plots.")
