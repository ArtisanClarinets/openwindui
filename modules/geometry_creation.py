
# Mock of openwind.geometry.creation
# Replace this if you later install the full openwind library with proper geometry support

def create_geometry_from_profile(positions, diameters):
    if len(positions) != len(diameters):
        raise ValueError("Position and diameter lists must be the same length.")
    if len(positions) < 2:
        raise ValueError("At least two points are required to define geometry.")
    return {
        "positions": positions,
        "diameters": diameters
    }
