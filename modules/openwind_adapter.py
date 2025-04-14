from openwind.temporal_simulation import simulate
from openwind.technical import Player
import numpy as np

def run_impedance_simulation(bore_df, temperature, material_props, freq_range):
    if bore_df.empty or "position" not in bore_df.columns or "diameter" not in bore_df.columns:
        raise ValueError("Bore data must have 'position' and 'diameter' columns.")
    
    try:
        main_bore = list(zip(bore_df["position"].tolist(), bore_df["diameter"].tolist()))

        # Player controls ONLY excitation input
        player = Player(dict_key={
            "excitator_type": "Flow",
            "input_flow": lambda t: 1e-6 if np.isclose(t, 0.0, atol=1e-6) else 0.0
        })

        result = simulate(
            player=player,
            main_bore=main_bore,
            duration=0.1,
            fmin=freq_range[0],
            fmax=freq_range[1],
            T=temperature,
            **material_props
        )
        return result

    except Exception as e:
        raise RuntimeError(f"Simulation failed: {e}")
