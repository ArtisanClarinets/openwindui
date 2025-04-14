
import pandas as pd
import numpy as np
from openwind_adapter import run_impedance_simulation

def autotune_bore(bore_df: pd.DataFrame, target_freq: float, temperature: float, material_props: dict, freq_range: tuple):
    if len(bore_df) < 3:
        raise ValueError("Need at least 3 points for autotuning.")
    if target_freq <= 0:
        raise ValueError("Target frequency must be positive.")

    bore_df = bore_df.copy()
    original_entry = bore_df["diameter"].iloc[0]
    original_exit = bore_df["diameter"].iloc[-1]

    best_df = bore_df.copy()
    best_score = float("inf")
    best_result = None

    for scale in np.linspace(0.95, 1.05, 11):
        mod_df = bore_df.copy()
        mod_df["position"] *= scale
        result = run_impedance_simulation(mod_df, temperature, material_props, freq_range)

        peaks = np.array(result["frequency"])[np.argsort(result["magnitude"])[-3:]]
        closest = min(peaks, key=lambda f: abs(f - target_freq))
        score = abs(closest - target_freq)

        if score < best_score:
            best_score = score
            best_df = mod_df
            best_result = result

    return best_df, best_result
