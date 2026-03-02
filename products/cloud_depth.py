# import numpy as np

# def compute_cloud_depth_index(ctt_c):
#     """
#     Proxy cloud depth indicator.
#     Colder tops → deeper clouds.

#     Output: 0–1 (relative, unitless)
#     """
#     depth = (-ctt_c) / 40.0
#     return np.clip(depth, 0.0, 1.0)


"""3 bands and show sir"""

# import numpy as np

# def compute_cloud_depth(ctt_c, surface_temp_c=25.0):
#     """
#     Estimates cloud vertical depth in kilometers.
#     Green Requirement: > 2-3 km
#     Amber Requirement: 1-2 km
#     Gray Constraint: < 1 km (Very shallow clouds)
#     """
#     # temp_diff = (Surface Temp) - (Cloud Top Temp)
#     # At Gohana, the land surface temp (LST) is often high (e.g., 43C in your logs)
#     temp_diff = surface_temp_c - ctt_c
    
#     # Standard environmental lapse rate is roughly 6.5 degrees Celsius per km
#     depth_km = temp_diff / 6.5
    
#     # Clip to realistic tropospheric limits (0 to 15km)
#     depth_km = np.clip(depth_km, 0.0, 15.0)
    
#     print(f"\n📏 Cloud Depth Diagnostics:")
#     print(f"  Estimated Mean Depth: {np.nanmean(depth_km):.2f} km")
    
#     return depth_km

""" lets see"""

# import numpy as np


# def compute_cloud_depth(ctt_c: np.ndarray,
#                         freezing_level_c: float = 0.0):
#     """
#     Physically-aligned cloud depth estimation.

#     Uses distance below freezing level instead of surface temperature.

#     Interpretation:
#         Deep cold tops → deep convective clouds
#         Warm tops → shallow clouds
#     """

#     # -------------------------------------------------
#     # Temperature difference from freezing level
#     # -------------------------------------------------
#     temp_diff = freezing_level_c - ctt_c

#     # Environmental lapse rate (~6.5°C/km)
#     depth_km = temp_diff / 6.5

#     # -------------------------------------------------
#     # Physical limits
#     # -------------------------------------------------
#     depth_km = np.clip(depth_km, 0.0, 12.0)

#     # Remove non-cloud pixels safely
#     depth_km[np.isnan(ctt_c)] = np.nan

#     # -------------------------------------------------
#     # Diagnostics
#     # -------------------------------------------------
#     valid = ~np.isnan(depth_km)

#     print("\n📏 Cloud Depth Diagnostics:")
#     if np.count_nonzero(valid) > 0:
#         print(f"  Mean Depth : {np.nanmean(depth_km):.2f} km")
#         print(f"  Deep (>3km): {np.mean(depth_km > 3)*100:.2f}%")
#         print(f"  Shallow(<1km): {np.mean(depth_km < 1)*100:.2f}%")

#     return depth_km


import numpy as np


def compute_cloud_depth(ctt_c, surface_temp_c=25.0):
    """
    Estimates cloud vertical depth (km)
    using environmental lapse rate approximation.

    Depth ≈ (Surface Temp - Cloud Top Temp) / 6.5
    """

    # temperature difference
    temp_diff = surface_temp_c - ctt_c

    # standard lapse rate ≈ 6.5 °C / km
    depth_km = temp_diff / 6.5

    # physical limits
    depth_km = np.clip(depth_km, 0.0, 15.0)

    print("\n📏 Cloud Depth Diagnostics:")
    print(f"  Mean Depth : {np.nanmean(depth_km):.2f} km")
    print(f"  Deep (>3km): {100*np.nanmean(depth_km > 3):.2f}%")
    print(f"  Shallow(<1km): {100*np.nanmean(depth_km < 1):.2f}%")

    return depth_km
