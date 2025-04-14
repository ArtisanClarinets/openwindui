
import numpy as np
from openwind.technical.instrument_geometry import geometry_from_points
from openwind.technical.presets import physics_from_geometry
from openwind.frequential.frequential_solver import FreqSolver

def run_impedance_simulation(bore_df, temperature, material_props, freq_range):
    if bore_df.empty or "position" not in bore_df.columns or "diameter" not in bore_df.columns:
        raise ValueError("Bore data must have 'position' and 'diameter' columns.")

    try:
        # Extract bore geometry from dataframe
        positions = bore_df["position"].tolist()
        diameters = bore_df["diameter"].tolist()
        bore_pts = list(zip(positions, diameters))

        # Build OpenWind geometry
        geometry = geometry_from_points(bore_pts)

        # Use built-in physics configuration
        physics = physics_from_geometry(geometry)

        # Build solver and compute impedance
        freqs = np.linspace(freq_range[0], freq_range[1], 512)
        solver = FreqSolver(instru_physics=physics, frequencies=freqs)

        # Evaluate impedance
        Z = solver.evaluate_impedance_at(freqs)

        return {
            "frequency": freqs,
            "magnitude": np.abs(Z),
            "phase": np.angle(Z, deg=True)
        }

    except Exception as e:
        raise RuntimeError(f"Simulation failed: {e}")
