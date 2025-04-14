from openwind.temporal_simulation import simulate
from openwind.technical import Player
import numpy as np

# Fake bore geometry
main_bore = [(0.0, 0.014), (0.1, 0.013)]

# Minimal flow input
player = Player(dict_key={
    "excitator_type": "Flow",
    "input_flow": lambda t: 1e-6 if np.isclose(t, 0.0, atol=1e-6) else 0.0
})

# Run
recording = simulate(player=player, main_bore=main_bore, duration=0.1)

# Print all available attributes/methods
print("\n✅ RecordingDevice attributes:")
print(dir(recording))
print("\n🧪 Try accessing spectrum-related properties:")
for attr in ["Zth", "freq", "Z", "frequencies", "spectrum"]:
    if hasattr(recording, attr):
        print(f"✓ {attr} = {getattr(recording, attr)}")
