#!/usr/bin/env python3
"""
Main analysis script for conductor galloping simulation.
Phase A: Bi-Stable Damper Feasibility Study

This script:
1. Runs baseline simulation (no devices)
2. Runs simulation with bi-stable devices
3. Performs parametric studies
4. Generates all required plots and analysis

Author: PRECorp Anti-Galloping Device Development
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.parameters import get_full_parameters, print_parameter_summary
from src.galloping_model import GallopingSimulation, compare_results, print_comparison
from src.visualization import (
    setup_plot_style,
    plot_time_history,
    plot_comparison_time_history,
    plot_phase_portrait,
    plot_energy_history,
    plot_parametric_study,
    plot_device_activity,
    create_summary_figure,
    save_results_to_file
)


def run_baseline_and_device_comparison(num_devices=4, snap_threshold=0.15,
                                       snap_force=200, save_results=True):
    """
    Run baseline and device simulations and compare.

    Args:
        num_devices: Number of bi-stable devices
        snap_threshold: Snap threshold displacement (m)
        snap_force: Force during snap (N)
        save_results: Whether to save plots and data

    Returns:
        Tuple of (baseline_results, device_results, comparison)
    """
    print("\n" + "="*70)
    print("RUNNING BASELINE AND DEVICE SIMULATIONS")
    print("="*70)

    # Get parameters
    params = get_full_parameters(num_devices=num_devices,
                                 snap_threshold=snap_threshold,
                                 snap_force=snap_force)
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

    # Save results
    if save_results:
        results_dir = 'results'
        os.makedirs(results_dir, exist_ok=True)

        # Time history plots
        plot_time_history(baseline_results, "Baseline Galloping (No Devices)",
                         save_path=f'{results_dir}/baseline_time_history.png')

        plot_time_history(device_results, f"With {num_devices} Bi-Stable Devices",
                         save_path=f'{results_dir}/device_time_history.png',
                         show_snaps=True)

        # Comparison plot
        plot_comparison_time_history(baseline_results, device_results,
                                    save_path=f'{results_dir}/comparison_time_history.png')

        # Phase portraits
        plot_phase_portrait(baseline_results, "Baseline Phase Portrait",
                           save_path=f'{results_dir}/baseline_phase_portrait.png')

        plot_phase_portrait(device_results, "With Devices Phase Portrait",
                           save_path=f'{results_dir}/device_phase_portrait.png')

        # Energy plots
        plot_energy_history(baseline_results, "Baseline Energy",
                           save_path=f'{results_dir}/baseline_energy.png')

        plot_energy_history(device_results, "Energy with Devices",
                           save_path=f'{results_dir}/device_energy.png')

        # Device activity
        plot_device_activity(device_results,
                            save_path=f'{results_dir}/device_activity.png')

        # Summary figure
        create_summary_figure(baseline_results, device_results, comparison,
                             save_path=f'{results_dir}/summary_figure.png')

        # Save numerical results
        save_results_to_file(comparison, baseline_results, device_results,
                            f'{results_dir}/results_summary.txt')

        print(f"\nAll plots saved to '{results_dir}/' directory")

    return baseline_results, device_results, comparison


def parametric_study_num_devices(max_devices=6, save_results=True):
    """
    Parametric study: vary number of devices.

    Args:
        max_devices: Maximum number of devices to test
        save_results: Whether to save plots

    Returns:
        Dictionary with parametric study results
    """
    print("\n" + "="*70)
    print("PARAMETRIC STUDY: NUMBER OF DEVICES")
    print("="*70)

    device_counts = list(range(2, max_devices + 1))
    reductions_max = []
    reductions_rms = []
    snap_rates = []

    # Run baseline once
    params_baseline = get_full_parameters(num_devices=0)
    baseline_sim = GallopingSimulation(params_baseline, use_devices=False)
    baseline_results = baseline_sim.run_simulation(A0=0.01)

    # Sweep device count
    for n in device_counts:
        print(f"\nTesting with {n} devices...")
        params = get_full_parameters(num_devices=n, snap_threshold=0.15)
        sim = GallopingSimulation(params, use_devices=True)
        results = sim.run_simulation(A0=0.01)

        # Calculate reduction
        reduction_max = (baseline_results['A_max_steady'] - results['A_max_steady']) / \
                        baseline_results['A_max_steady'] * 100
        reduction_rms = (baseline_results['A_rms_steady'] - results['A_rms_steady']) / \
                        baseline_results['A_rms_steady'] * 100

        reductions_max.append(reduction_max)
        reductions_rms.append(reduction_rms)
        snap_rates.append(results['snap_rate'])

        print(f"  Max reduction: {reduction_max:.1f}%, RMS reduction: {reduction_rms:.1f}%")

    # Plot results
    if save_results:
        plot_parametric_study(device_counts, reductions_max, reductions_rms,
                             'Number of Devices', 'devices',
                             save_path='results/parametric_num_devices.png')

    results = {
        'device_counts': device_counts,
        'reductions_max': reductions_max,
        'reductions_rms': reductions_rms,
        'snap_rates': snap_rates
    }

    return results


def parametric_study_snap_threshold(thresholds=None, save_results=True):
    """
    Parametric study: vary snap threshold.

    Args:
        thresholds: List of snap thresholds to test (m)
        save_results: Whether to save plots

    Returns:
        Dictionary with parametric study results
    """
    print("\n" + "="*70)
    print("PARAMETRIC STUDY: SNAP THRESHOLD")
    print("="*70)

    if thresholds is None:
        thresholds = [0.10, 0.12, 0.15, 0.18, 0.20, 0.25]

    reductions_max = []
    reductions_rms = []
    snap_rates = []

    # Run baseline once
    params_baseline = get_full_parameters(num_devices=0)
    baseline_sim = GallopingSimulation(params_baseline, use_devices=False)
    baseline_results = baseline_sim.run_simulation(A0=0.01)

    # Sweep snap threshold
    for threshold in thresholds:
        print(f"\nTesting snap threshold = {threshold:.3f} m ({threshold/0.0254:.1f} in)...")
        params = get_full_parameters(num_devices=4, snap_threshold=threshold)
        sim = GallopingSimulation(params, use_devices=True)
        results = sim.run_simulation(A0=0.01)

        # Calculate reduction
        reduction_max = (baseline_results['A_max_steady'] - results['A_max_steady']) / \
                        baseline_results['A_max_steady'] * 100
        reduction_rms = (baseline_results['A_rms_steady'] - results['A_rms_steady']) / \
                        baseline_results['A_rms_steady'] * 100

        reductions_max.append(reduction_max)
        reductions_rms.append(reduction_rms)
        snap_rates.append(results['snap_rate'])

        print(f"  Max reduction: {reduction_max:.1f}%, RMS reduction: {reduction_rms:.1f}%")
        print(f"  Snap rate: {results['snap_rate']:.2f} snaps/s")

    # Plot results
    if save_results:
        # Convert to inches for plotting
        thresholds_inches = [t / 0.0254 for t in thresholds]
        plot_parametric_study(thresholds_inches, reductions_max, reductions_rms,
                             'Snap Threshold', 'inches',
                             save_path='results/parametric_snap_threshold.png')

    results = {
        'thresholds': thresholds,
        'reductions_max': reductions_max,
        'reductions_rms': reductions_rms,
        'snap_rates': snap_rates
    }

    return results


def generate_final_report():
    """Generate final summary report with all key findings."""
    print("\n" + "="*70)
    print("GENERATING FINAL REPORT")
    print("="*70)

    report_file = 'results/PHASE_A_FINAL_REPORT.txt'

    with open(report_file, 'w') as f:
        f.write("="*70 + "\n")
        f.write("CONDUCTOR GALLOPING WITH BI-STABLE DAMPERS\n")
        f.write("PHASE A: FEASIBILITY STUDY - FINAL REPORT\n")
        f.write("="*70 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Project: PRECorp Distribution Feeder Anti-Galloping Device\n")
        f.write("="*70 + "\n\n")

        f.write("EXECUTIVE SUMMARY\n")
        f.write("-"*70 + "\n")
        f.write("This report presents the results of Phase A feasibility modeling for\n")
        f.write("bi-stable damping devices to mitigate conductor galloping on 336.4 kcmil\n")
        f.write("Merlin ACSR conductors.\n\n")

        f.write("OBJECTIVES:\n")
        f.write("  1. Simulate galloping oscillations on iced conductor\n")
        f.write("  2. Model bi-stable spring devices attached to conductor\n")
        f.write("  3. Determine if devices reduce amplitude by >30%\n")
        f.write("  4. Identify optimal device configuration\n\n")

        f.write("SUCCESS CRITERIA:\n")
        f.write("  - Max amplitude reduction > 30%\n")
        f.write("  - RMS amplitude reduction > 25%\n")
        f.write("  - Device snaps occur regularly (indicates active damping)\n")
        f.write("  - Energy dissipated by devices > 20% of total energy\n\n")

        f.write("="*70 + "\n")
        f.write("RESULTS SUMMARY\n")
        f.write("="*70 + "\n\n")

        f.write("See the following files for detailed results:\n")
        f.write("  - results_summary.txt: Numerical comparison\n")
        f.write("  - summary_figure.png: Comprehensive visual summary\n")
        f.write("  - comparison_time_history.png: Time domain comparison\n")
        f.write("  - parametric_num_devices.png: Device count optimization\n")
        f.write("  - parametric_snap_threshold.png: Threshold optimization\n\n")

        f.write("="*70 + "\n")
        f.write("RECOMMENDATIONS\n")
        f.write("="*70 + "\n\n")

        f.write("Based on simulation results:\n\n")

        f.write("IF results show >30% reduction:\n")
        f.write("  RECOMMENDATION: PROCEED to Phase B (Detailed FEA)\n")
        f.write("  NEXT STEPS:\n")
        f.write("    1. Document findings in technical memo\n")
        f.write("    2. Begin Phase B: Detailed beam mechanics FEA\n")
        f.write("    3. Initiate university collaboration discussions\n")
        f.write("    4. Consider provisional patent application\n")
        f.write("    5. Prepare Phase B budget proposal\n\n")

        f.write("IF results show 10-30% reduction:\n")
        f.write("  RECOMMENDATION: OPTIMIZE before Phase B\n")
        f.write("  NEXT STEPS:\n")
        f.write("    1. Explore parameter optimization in more detail\n")
        f.write("    2. Consider hybrid approaches\n")
        f.write("    3. Evaluate cost-benefit of marginal improvement\n")
        f.write("    4. Decision: Proceed with caution or pivot\n\n")

        f.write("IF results show <10% reduction:\n")
        f.write("  RECOMMENDATION: RECONSIDER CONCEPT\n")
        f.write("  NEXT STEPS:\n")
        f.write("    1. Analyze why concept didn't work\n")
        f.write("    2. Review assumptions (3D motion importance?)\n")
        f.write("    3. Explore alternative concepts\n")
        f.write("    4. Document lessons learned\n\n")

        f.write("="*70 + "\n")
        f.write("VALIDATION CHECKLIST\n")
        f.write("="*70 + "\n\n")

        f.write("[ ] Baseline model produces realistic galloping behavior\n")
        f.write("[ ] Model shows energy conservation (within 5%)\n")
        f.write("[ ] Device snap events occur at reasonable frequency\n")
        f.write("[ ] Results change smoothly with parameter variations\n")
        f.write("[ ] Predicted amplitudes are physically reasonable\n")
        f.write("[ ] Effectiveness scales logically with device count\n")
        f.write("[ ] Clear optimal parameter range identified\n")
        f.write("[ ] Sufficient confidence to invest in Phase B\n\n")

        f.write("="*70 + "\n")
        f.write("END OF REPORT\n")
        f.write("="*70 + "\n")

    print(f"\nFinal report generated: {report_file}")
    print("\nAll Phase A deliverables complete!")


def main():
    """Main execution function."""
    print("\n" + "="*70)
    print("CONDUCTOR GALLOPING SIMULATION - PHASE A")
    print("Bi-Stable Damper Feasibility Study")
    print("="*70)

    # Set up plotting
    setup_plot_style()

    # Ensure results directory exists
    os.makedirs('results', exist_ok=True)

    # 1. Run baseline and device comparison
    print("\n### STEP 1: BASELINE AND DEVICE COMPARISON ###")
    baseline_results, device_results, comparison = run_baseline_and_device_comparison(
        num_devices=4,
        snap_threshold=0.15,
        snap_force=200,
        save_results=True
    )

    # 2. Parametric study: number of devices
    print("\n### STEP 2: PARAMETRIC STUDY - NUMBER OF DEVICES ###")
    param_devices = parametric_study_num_devices(max_devices=6, save_results=True)

    # 3. Parametric study: snap threshold
    print("\n### STEP 3: PARAMETRIC STUDY - SNAP THRESHOLD ###")
    param_threshold = parametric_study_snap_threshold(
        thresholds=[0.10, 0.12, 0.15, 0.18, 0.20, 0.25],
        save_results=True
    )

    # 4. Generate final report
    print("\n### STEP 4: FINAL REPORT GENERATION ###")
    generate_final_report()

    # Final summary
    print("\n" + "="*70)
    print("PHASE A SIMULATION COMPLETE")
    print("="*70)
    print("\nKey Finding:")
    print(f"  Amplitude Reduction: {comparison['reduction_max_percent']:.1f}%")
    print(f"  Assessment: {comparison['effectiveness']}")
    print(f"\nAll results saved to 'results/' directory")
    print("\nNext Steps:")
    if comparison['reduction_max_percent'] > 30:
        print("  ✓ PROCEED to Phase B (Detailed FEA)")
        print("  ✓ Concept shows strong feasibility")
    elif comparison['reduction_max_percent'] > 10:
        print("  ⚠ OPTIMIZE parameters before Phase B")
        print("  ⚠ Concept shows marginal feasibility")
    else:
        print("  ✗ RECONSIDER concept")
        print("  ✗ Explore alternative approaches")

    print("="*70 + "\n")

    # Show key plot
    plt.show()


if __name__ == "__main__":
    main()
