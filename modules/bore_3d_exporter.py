
import cadquery as cq
import pandas as pd

def generate_bore_model(bore_df: pd.DataFrame, wall_thickness: float, length_scale: float = 1.0):
    # Validate input
    if len(bore_df) < 2:
        raise ValueError("Need at least 2 points to create a bore geometry.")
    if bore_df["diameter"].nunique() < 2:
        raise ValueError("Diameters must vary to form a shape.")

    # Rescale length if needed
    bore_df = bore_df.copy()
    bore_df["position"] *= length_scale

    # Define path and profile points
    path_pts = [(0, 0, z * 1000) for z in bore_df["position"]]
    radii = bore_df["diameter"] / 2.0

    try:
        # Build central spline path
        path = cq.Workplane("XY").spline(path_pts)
        # Profile circle at start
        profile = cq.Workplane("XY").circle(radii.iloc[0] * 1000 + wall_thickness)
        # Sweep shell along spline
        shell = path.sweep(profile)
        return shell
    except Exception as e:
        raise ValueError(f"3D model generation failed: {e}")

def export_model_as_stl(model):
    return model.val().exportStl(), "application/sla"

def export_model_as_step(model):
    return model.val().exportStep(), "application/step"
