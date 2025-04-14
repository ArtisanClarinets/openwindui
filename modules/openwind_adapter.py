import numpy as np
from openwind.continuous.instrument_physics import InstrumentPhysics
from openwind.continuous.pipe import AcousticPipe
from openwind.continuous.netlist import InstrumentGeometry
from openwind.frequential.frequential_solver import FrequentialSolver

def run_impedance_simulation(bore_df, temperature=25.0, material_props=None, freq_range=(100, 2000)):
    """
    Simulate impedance Z(f) for a bore geometry using OpenWind v0.11.3.

    Parameters:
        bore_df: DataFrame with 'position' and 'diameter' columns (meters).
        temperature: Ambient temperature in °C.
        material_props: (Optional) Placeholder for future use.
        freq_range: Tuple (f_min, f_max) in Hz.

    Returns:
        Dict with 'frequency', 'magnitude', and 'phase'.
    """
    if bore_df.empty or "position" not in bore_df.columns or "diameter" not in bore_df.columns:
        raise ValueError("Bore data must have 'position' and 'diameter' columns.")

    try:
        # Convert (x, diameter) to AcousticPipe list
        points = list(zip(bore_df["position"], bore_df["diameter"] / 2))  # radius = diameter / 2

        # Create main bore as sequence of acoustic pipes
        main_bore = [AcousticPipe(length=points[i+1][0] - points[i][0],
                                  radius_in=points[i][1],
                                  radius_out=points[i+1][1])
                     for i in range(len(points) - 1)]

        geometry = InstrumentGeometry(main_bore=main_bore)

        # Construct physics with optional player and loss model
        physics = InstrumentPhysics(geometry, temperature=temperature, player=None, losses=True)

        # Setup frequency range and solver
        freqs = np.linspace(freq_range[0], freq_range[1], 512)
        solver = FrequentialSolver(physics, freqs)

        Z = solver.evaluate_impedance_at(freqs)

        return {
            "frequency": freqs,
            "magnitude": np.abs(Z),
            "phase": np.angle(Z, deg=True)
        }

    except Exception as e:
        raise RuntimeError(f"Impedance simulation failed: {e}")
