from openwind.temporal_simulation import simulate
from openwind.technical import Player
import numpy as np

def run_impedance_simulation(bore_df, temperature, material_props, freq_range):
    if bore_df.empty or "position" not in bore_df.columns or "diameter" not in bore_df.columns:
        raise ValueError("Bore data must have 'position' and 'diameter' columns.")
    
    try:
        main_bore = list(zip(bore_df["position"].tolist(), bore_df["diameter"].tolist()))

        player = Player(dict_key={
            "excitator_type": "Flow",
            "input_flow": lambda t: 1e-6 if np.isclose(t, 0.0, atol=1e-6) else 0.0
        })

        # Run simulation
        recording = simulate(
            player=player,
            main_bore=main_bore,
            duration=0.1
        )

        freq = np.array(recording.t_solver.freq)
        Zth = np.array(recording.t_solver.Zth)

        return {
            "frequency": freq,
            "magnitude": np.abs(Zth),
            "phase": np.angle(Zth, deg=True)
        }

    except Exception as e:
        raise RuntimeError(f"Simulation failed: {e}")
