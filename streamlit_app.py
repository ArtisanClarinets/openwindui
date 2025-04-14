import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import zipfile
import time
import librosa
import sys
from pathlib import Path

# Local module imports
sys.path.append("modules")
from openwind_adapter import run_impedance_simulation
from bore_3d_exporter import generate_bore_model, export_model_as_stl, export_model_as_step
from autotune import autotune_bore
from session_manager import save_session, load_session

# Apply clarinet theme
with open("assets/clarinet_theme.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🎶 OpenWind Clarinet Designer")
st.markdown("A full-featured design and analysis suite for clarinet barrels.")

# Sidebar - Bore Input
st.sidebar.header("1. Bore Input")
bore_mode = st.sidebar.radio("Select Input Method", ["Upload CSV", "Draw Taper"])
if bore_mode == "Upload CSV":
    uploaded_file = st.sidebar.file_uploader("Upload bore CSV", type="csv")
    bore_df = pd.read_csv(uploaded_file) if uploaded_file else pd.read_csv("data/sample_bore.csv")
else:
    x = np.linspace(0, 0.2, 50)
    diam_range = st.sidebar.slider("Taper: Entry to Exit Diameter (mm)", 12.0, 15.0, (14.5, 13.0))
    y = np.linspace(diam_range[0], diam_range[1], len(x)) / 1000
    bore_df = pd.DataFrame({"position": x, "diameter": y})

st.subheader("📊 Bore Profile (2D)")
fig_bore, ax_bore = plt.subplots()
ax_bore.plot(bore_df["position"], bore_df["diameter"] * 1000)
ax_bore.set_xlabel("Bore Length (m)")
ax_bore.set_ylabel("Diameter (mm)")
st.pyplot(fig_bore)

# Sidebar - Environment & Material
st.sidebar.header("2. Environment & Material")
temp_unit = st.sidebar.radio("Temperature Unit", ["°C", "°F"], index=0)
if temp_unit == "°C":
    temperature = st.sidebar.slider("Temperature (°C)", 0, 40, 22)
else:
    temperature_f = st.sidebar.slider("Temperature (°F)", 32, 104, 72)
    temperature = (temperature_f - 32) * 5 / 9
st.sidebar.caption("🌡️\ufe0f Temperature affects tuning and resonance. Most clarinets are tested near 22°C (72°F).")

humidity = st.sidebar.slider("Humidity (%)", 0, 100, 50)
st.sidebar.caption("☕\ufe0f Humidity changes air resistance slightly, affecting impedance.")

material_type = st.sidebar.selectbox("Material", ["Grenadilla", "ABS Resin", "Custom"])
material_props = {}
if material_type == "Custom":
    material_props["density"] = st.sidebar.number_input("Density (kg/m\u00b3)", value=1200.0)
    material_props["viscosity"] = st.sidebar.number_input("Viscosity (Pa\u00b7s)", value=1.8e-5)
    material_props["speed_of_sound"] = st.sidebar.number_input("Speed of Sound (m/s)", value=343.0)

st.sidebar.header("3. Simulation")
freq_range = st.sidebar.slider("Frequency Range (Hz)", 100, 3000, (200, 2000))
st.sidebar.markdown("ℹ️\ufe0f Bb Clarinet range: ~147 Hz (D3) to ~1568 Hz (G6). Eb Clarinet plays slightly higher.")

# Run Simulation
if st.sidebar.button("▶️\ufe0f Run Simulation"):
    st.info("Running simulation...")
    bar = st.progress(0)
    for i in range(100):
        time.sleep(0.004)
        bar.progress(i + 1)
    result = run_impedance_simulation(bore_df, temperature, material_props, freq_range)
    f, mag, phase = result["frequency"], result["magnitude"], result["phase"]

    st.success("Simulation complete!")
    st.subheader("📊 Impedance Magnitude")
    st.caption("Shows resistance to air vibration at different frequencies. Peaks indicate resonant notes.")
    fig1, ax1 = plt.subplots()
    ax1.plot(f, mag)
    ax1.set_xlabel("Frequency (Hz)")
    ax1.set_ylabel("|Z| (Pa·s/m³)")
    st.pyplot(fig1)

    st.subheader("🔄 Impedance Phase")
    st.caption("Shows timing shifts in pressure waves — useful for tuning analysis.")
    fig2, ax2 = plt.subplots()
    ax2.plot(f, phase)
    ax2.set_xlabel("Frequency (Hz)")
    ax2.set_ylabel("Phase (°)")
    st.pyplot(fig2)

    st.subheader("📄 Export Results")
    impedance_df = pd.DataFrame({"Frequency (Hz)": f, "Magnitude": mag, "Phase": phase})
    csv_data = impedance_df.to_csv(index=False).encode("utf-8")
    img_buffer = io.BytesIO()
    fig1.savefig(img_buffer, format="png")
    img_buffer.seek(0)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("impedance_data.csv", csv_data)
        zf.writestr("impedance_plot.png", img_buffer.getvalue())
    zip_buffer.seek(0)
    st.download_button("Download CSV", csv_data, "impedance_data.csv")
    st.download_button("Download Plot", img_buffer, "impedance_plot.png")
    st.download_button("Download ZIP", zip_buffer, "impedance_package.zip")

    # Optimization and resonance summary will go here (next step)

st.markdown("---")
st.subheader("💾 Save / Load Session")
notes = st.text_input("Notes")
session_json = save_session(bore_df, temperature, humidity, material_props, notes)
st.download_button("Save Session", session_json, "session_export.json")

uploaded_session = st.file_uploader("Upload Saved Session (.json)", type="json")
if uploaded_session:
    session_str = uploaded_session.read().decode("utf-8")
    bore_df, temperature, humidity, material_props, notes = load_session(session_str)
    st.success("Session restored successfully.")
    if notes:
        st.info(f"Notes: {notes}")
