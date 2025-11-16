"""
Unit tests for visualization.py module.
Tests visualization setup and file saving functions.
Note: Plot generation is tested for execution without errors, not visual output.
"""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
import sys
import os
import tempfile

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

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


# Create mock simulation results for testing
def create_mock_baseline_results():
    """Create mock baseline simulation results."""
    time = np.linspace(0, 60, 6000)
    amplitude = 3.0 * np.sin(2 * np.pi * 0.5 * time) * (1 - np.exp(-time/10))
    velocity = np.gradient(amplitude, time)

    return {
        'time': time,
        'amplitude': amplitude,
        'velocity': velocity,
        'kinetic_energy': 0.5 * 100 * velocity**2,
        'potential_energy': 0.5 * 5000 * amplitude**2,
        'total_energy': 0.5 * 100 * velocity**2 + 0.5 * 5000 * amplitude**2,
        'snap_events': [],
        'A_max_steady': 2.8,
        'A_rms_steady': 2.0,
        'A_mean_steady': 1.8,
        'A_max_overall': 3.0,
        'max_velocity': 9.5,
        'max_energy': 5000.0,
        'num_snaps': 0,
        'snap_rate': 0.0,
        'energy_dissipated': 0.0,
        'use_devices': False,
        'num_devices': 0,
        'success': True,
        'message': 'Success'
    }


def create_mock_device_results():
    """Create mock device simulation results."""
    time = np.linspace(0, 60, 6000)
    amplitude = 1.8 * np.sin(2 * np.pi * 0.5 * time) * (1 - np.exp(-time/10))
    velocity = np.gradient(amplitude, time)

    snap_events = [
        {'time': 10.0, 'device_id': 0, 'amplitude': 1.5, 'velocity': 0.5,
         'new_state': -1, 'position': 20.0},
        {'time': 15.0, 'device_id': 1, 'amplitude': 1.7, 'velocity': 0.3,
         'new_state': 1, 'position': 40.0},
        {'time': 20.0, 'device_id': 2, 'amplitude': 1.6, 'velocity': -0.4,
         'new_state': -1, 'position': 60.0},
    ]

    return {
        'time': time,
        'amplitude': amplitude,
        'velocity': velocity,
        'kinetic_energy': 0.5 * 100 * velocity**2,
        'potential_energy': 0.5 * 5000 * amplitude**2,
        'total_energy': 0.5 * 100 * velocity**2 + 0.5 * 5000 * amplitude**2,
        'snap_events': snap_events,
        'A_max_steady': 1.7,
        'A_rms_steady': 1.2,
        'A_mean_steady': 1.0,
        'A_max_overall': 1.8,
        'max_velocity': 5.7,
        'max_energy': 2500.0,
        'num_snaps': 3,
        'snap_rate': 0.05,
        'energy_dissipated': 45.0,
        'use_devices': True,
        'num_devices': 4,
        'device_snap_counts': [15, 12, 18, 10],
        'success': True,
        'message': 'Success'
    }


def create_mock_comparison():
    """Create mock comparison results."""
    return {
        'A_max_baseline': 2.8,
        'A_max_devices': 1.7,
        'reduction_max_percent': 39.3,
        'A_rms_baseline': 2.0,
        'A_rms_devices': 1.2,
        'reduction_rms_percent': 40.0,
        'E_max_baseline': 5000.0,
        'E_max_devices': 2500.0,
        'energy_reduction_percent': 50.0,
        'num_snaps': 3,
        'snap_rate': 0.05,
        'energy_dissipated': 45.0,
        'effectiveness': 'FEASIBLE - Concept meets success criteria'
    }


class TestSetupPlotStyle:
    """Test plot style setup."""

    def test_setup_runs_without_error(self):
        """Test that setup runs without error."""
        try:
            setup_plot_style()
        except Exception as e:
            pytest.fail(f"setup_plot_style raised exception: {e}")

    def test_rcparams_modified(self):
        """Test that rcParams are set to expected values."""
        setup_plot_style()

        # Check that parameters are set to expected values
        # Convert to list for comparison since rcParams returns RcParams object
        assert list(plt.rcParams['figure.figsize']) == [12, 8]
        assert plt.rcParams['font.size'] == 11


class TestPlotTimeHistory:
    """Test time history plotting."""

    def test_plot_runs_without_error(self):
        """Test that plot generation runs without error."""
        results = create_mock_baseline_results()

        try:
            fig, ax = plot_time_history(results, "Test Plot")
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_time_history raised exception: {e}")

    def test_plot_with_snaps(self):
        """Test plot with snap events."""
        results = create_mock_device_results()

        try:
            fig, ax = plot_time_history(results, "Test Plot", show_snaps=True)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_time_history with snaps raised exception: {e}")

    def test_plot_save(self):
        """Test that plot can be saved."""
        results = create_mock_baseline_results()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_plot.png")
            fig, ax = plot_time_history(results, "Test Plot", save_path=save_path)
            plt.close(fig)

            assert os.path.exists(save_path)


class TestPlotComparisonTimeHistory:
    """Test comparison time history plotting."""

    def test_comparison_plot_runs(self):
        """Test that comparison plot runs without error."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()

        try:
            fig, axes = plot_comparison_time_history(baseline, device)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_comparison_time_history raised exception: {e}")

    def test_comparison_plot_save(self):
        """Test that comparison plot can be saved."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_comparison.png")
            fig, axes = plot_comparison_time_history(baseline, device, save_path)
            plt.close(fig)

            assert os.path.exists(save_path)


class TestPlotPhasePortrait:
    """Test phase portrait plotting."""

    def test_phase_portrait_runs(self):
        """Test that phase portrait runs without error."""
        results = create_mock_baseline_results()

        try:
            fig, ax = plot_phase_portrait(results, "Test Phase Portrait")
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_phase_portrait raised exception: {e}")

    def test_phase_portrait_save(self):
        """Test that phase portrait can be saved."""
        results = create_mock_baseline_results()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_phase.png")
            fig, ax = plot_phase_portrait(results, "Test", save_path)
            plt.close(fig)

            assert os.path.exists(save_path)


class TestPlotEnergyHistory:
    """Test energy history plotting."""

    def test_energy_plot_runs(self):
        """Test that energy plot runs without error."""
        results = create_mock_baseline_results()

        try:
            fig, axes = plot_energy_history(results, "Test Energy")
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_energy_history raised exception: {e}")

    def test_energy_plot_with_devices(self):
        """Test energy plot with device results."""
        results = create_mock_device_results()

        try:
            fig, axes = plot_energy_history(results, "Test Energy")
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_energy_history with devices raised exception: {e}")

    def test_energy_plot_save(self):
        """Test that energy plot can be saved."""
        results = create_mock_baseline_results()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_energy.png")
            fig, axes = plot_energy_history(results, "Test", save_path)
            plt.close(fig)

            assert os.path.exists(save_path)


class TestPlotParametricStudy:
    """Test parametric study plotting."""

    def test_parametric_plot_runs(self):
        """Test that parametric plot runs without error."""
        param_values = [2, 3, 4, 5, 6]
        reductions_max = [25, 35, 40, 42, 43]
        reductions_rms = [20, 30, 35, 37, 38]

        try:
            fig, ax = plot_parametric_study(param_values, reductions_max,
                                           reductions_rms, "Test Param", "units")
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_parametric_study raised exception: {e}")

    def test_parametric_plot_save(self):
        """Test that parametric plot can be saved."""
        param_values = [2, 3, 4, 5, 6]
        reductions_max = [25, 35, 40, 42, 43]
        reductions_rms = [20, 30, 35, 37, 38]

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_parametric.png")
            fig, ax = plot_parametric_study(param_values, reductions_max,
                                           reductions_rms, "Test", "units", save_path)
            plt.close(fig)

            assert os.path.exists(save_path)


class TestPlotDeviceActivity:
    """Test device activity plotting."""

    def test_device_activity_runs(self):
        """Test that device activity plot runs without error."""
        results = create_mock_device_results()

        try:
            fig, axes = plot_device_activity(results)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"plot_device_activity raised exception: {e}")

    def test_device_activity_no_devices(self):
        """Test device activity with no devices."""
        results = create_mock_baseline_results()

        result = plot_device_activity(results)
        # Should return None for no devices
        assert result[0] is None or result == (None, None)

    def test_device_activity_save(self):
        """Test that device activity plot can be saved."""
        results = create_mock_device_results()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_device_activity.png")
            fig, axes = plot_device_activity(results, save_path)

            if fig is not None:
                plt.close(fig)
                assert os.path.exists(save_path)


class TestCreateSummaryFigure:
    """Test summary figure creation."""

    def test_summary_figure_runs(self):
        """Test that summary figure runs without error."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()
        comparison = create_mock_comparison()

        try:
            fig = create_summary_figure(baseline, device, comparison)
            plt.close(fig)
        except Exception as e:
            pytest.fail(f"create_summary_figure raised exception: {e}")

    def test_summary_figure_save(self):
        """Test that summary figure can be saved."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()
        comparison = create_mock_comparison()

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = os.path.join(tmpdir, "test_summary.png")
            fig = create_summary_figure(baseline, device, comparison, save_path)
            plt.close(fig)

            assert os.path.exists(save_path)


class TestSaveResultsToFile:
    """Test saving results to file."""

    def test_save_results_creates_file(self):
        """Test that save_results_to_file creates a file."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()
        comparison = create_mock_comparison()

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_results.txt")
            save_results_to_file(comparison, baseline, device, filename)

            assert os.path.exists(filename)

    def test_save_results_content(self):
        """Test that saved results contain expected content."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()
        comparison = create_mock_comparison()

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_results.txt")
            save_results_to_file(comparison, baseline, device, filename)

            with open(filename, 'r') as f:
                content = f.read()

            # Check for key content
            assert "BASELINE RESULTS" in content
            assert "WITH DEVICES RESULTS" in content
            assert "EFFECTIVENESS METRICS" in content
            assert "SUCCESS CRITERIA" in content

    def test_save_results_metrics_present(self):
        """Test that all metrics are present in saved file."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()
        comparison = create_mock_comparison()

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_results.txt")
            save_results_to_file(comparison, baseline, device, filename)

            with open(filename, 'r') as f:
                content = f.read()

            # Check for specific metrics
            assert "Max Amplitude" in content
            assert "RMS Amplitude" in content
            assert "Energy Dissipated" in content
            assert "Snap Events" in content

    def test_save_results_pass_fail(self):
        """Test that PASS/FAIL indicators are present."""
        baseline = create_mock_baseline_results()
        device = create_mock_device_results()
        comparison = create_mock_comparison()

        with tempfile.TemporaryDirectory() as tmpdir:
            filename = os.path.join(tmpdir, "test_results.txt")
            save_results_to_file(comparison, baseline, device, filename)

            with open(filename, 'r') as f:
                content = f.read()

            # Should have PASS for 39% reduction
            assert "PASS" in content or "✓" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
