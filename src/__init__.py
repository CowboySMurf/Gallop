"""
Conductor Galloping Simulation Package
Phase A: Bi-Stable Damper Feasibility Model

Author: PRECorp Anti-Galloping Device Development
"""

from .parameters import (
    get_full_parameters,
    print_parameter_summary,
    ConductorParameters,
    EnvironmentalParameters,
    DeviceParameters
)

from .galloping_model import (
    GallopingSimulation,
    compare_results,
    print_comparison
)

from .visualization import (
    plot_time_history,
    plot_comparison_time_history,
    plot_phase_portrait,
    plot_energy_history,
    plot_parametric_study,
    plot_device_activity,
    create_summary_figure,
    save_results_to_file,
    setup_plot_style
)

__version__ = "1.0.0"
__author__ = "PRECorp Anti-Galloping Device Development"
