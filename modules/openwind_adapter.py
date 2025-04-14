import numpy as np
from openwind.continuous.instrument_physics import InstrumentPhysics
from openwind.continuous.pipe import Pipe
from openwind.design.cone import Cone
from openwind.frequential.frequential_solver import FrequentialSolver
from openwind.technical.instrument_geometry import InstrumentGeometry

def run_impedance_simulation(bore_df, temperature=25.0, material_props=None, freq_range=(100, 2000)):
    if bore_df.empty or "position" not in bore_df.columns or "diameter" not in bore_df.columns:
        raise ValueError("Bore data must have 'position' and 'diameter' columns.")

    try:
        # Convert (position, diameter) → (position, radius)
        points = list(zip(bore_df["position"], bore_df["diameter"] / 2))
        pipes = []

        for i in range(len(points) - 1):
            x0, r0 = points[i]
            x1, r1 = points[i + 1]

            shape = Cone(x0, x1, r0, r1)  # ✅ corrected constructor

            pipe = Pipe(
                design_shape=shape,
                temperature=temperature,
                label=f"bore{i}",
                scaling="physical",
                losses=True
            )

            pipes.append(pipe)

        geometry = InstrumentGeometry()
        geometry.main_bore_shapes = pipes

        physics = InstrumentPhysics(
            geometry,
            temperature=temperature,
            player=None,
            losses=True
        )

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
