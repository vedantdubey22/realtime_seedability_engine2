# import numpy as np

# def decide_seedability(ctt_c, growth, depth, lwp, cloud_mask):
#     """
#     FORCE-COLOR VERSION: Ensures every detected cloud pixel is categorized.
#     """
#     # Initialize with -1 (Transparent/Clear Sky)
#     seed = np.full(ctt_c.shape, -1, dtype=np.int8)
    
#     # Create a boolean mask of where clouds actually are
#     is_cloud = (cloud_mask == 1.0)

#     # 1. 🟢 GREEN: The "Sweet Spot"
#     # Cold enough and growing significantly
#     green_mask = is_cloud & (ctt_c <= -8.0) & (growth > 1.2)
#     seed[green_mask] = 2

#     # 2. 🟠 AMBER: The "Watch Zone"
#     # Supercooled but growing slowly
#     amber_mask = is_cloud & (ctt_c <= -2.0) & (growth > 0.1) & (seed != 2)
#     seed[amber_mask] = 1

#     # 3. ⚪ GRAY: The "Unsuitable Cloud" (Catch-all)
#     # If it's a cloud but NOT Green or Amber, it MUST be Gray.
#     # This ensures your 3.19% cloud cover actually shows up.
#     gray_mask = is_cloud & (seed == -1)
#     seed[gray_mask] = 0

#     # --- Robust Diagnostics ---
#     valid_mask = ~np.isnan(ctt_c)
#     total_valid = np.count_nonzero(valid_mask)
    
#     print("\n📊 Final Seedability Breakdown:")
#     if total_valid > 0:
#         n_green = np.sum(seed == 2)
#         n_amber = np.sum(seed == 1)
#         n_gray  = np.sum(seed == 0)
#         n_none  = np.sum((seed == -1) & valid_mask)

#         print(f"  🟢 GREEN  : {100 * n_green / total_valid:.2f}%")
#         print(f"  🟠 AMBER  : {100 * n_amber / total_valid:.2f}%")
#         print(f"  ⚪ GRAY   : {100 * n_gray / total_valid:.2f}%")
#         print(f"  🟦 NONE   : {100 * n_none / total_valid:.2f}% (Clear Sky)")
#         print(f"  ☁️ Total Clouds Categorized: {n_green + n_amber + n_gray} pixels")
    
#     return seed

"""2 bands"""

# import numpy as np

# def decide_seedability(ctt_c, growth, swd, cloud_mask):
#     """
#     DUAL-BAND DECISION ENGINE
#     Uses B13-B14 Split Window Difference (SWD) to filter ice phase.
#     """
#     # Initialize with -1 (Transparent/Clear Sky)
#     seed = np.full(ctt_c.shape, -1, dtype=np.int8)
    
#     # Create a boolean mask of where clouds actually are
#     is_cloud = (cloud_mask == 1.0)

#     # 1. 🟢 GREEN: High Potential Seedable
#     # Requirements: Cold (<-10°C), Growing (>1.5°C cooling), and Liquid-Rich (SWD < 0.6)
#     green_mask = (
#         is_cloud & 
#         (ctt_c <= -10.0) & 
#         (growth > 1.5) & 
#         (swd < 0.6) # <--- B14 Ice/Haze Filter
#     )
#     seed[green_mask] = 2

#     # 2. 🟠 AMBER: Marginal/Watch Conditions
#     # Requirements: CTT between -5°C and -10°C per documentation
#     amber_mask = (
#         is_cloud & 
#         (ctt_c <= -5.0) & 
#         (growth > 0.5) & 
#         (seed != 2)
#     )
#     seed[amber_mask] = 1

#     # 3. ⚪ GRAY: Do Not Seed (Ineffective)
#     # Catch-all for ice-dominated clouds, shallow clouds, or collapsing tops
#     gray_mask = is_cloud & (seed == -1)
#     seed[gray_mask] = 0

#     # --- Robust Diagnostics ---
#     valid_mask = ~np.isnan(ctt_c)
#     total_valid = np.count_nonzero(valid_mask)
    
#     print("\n📊 Final Seedability Breakdown (Dual-Band):")
#     if total_valid > 0:
#         n_green = np.sum(seed == 2)
#         n_amber = np.sum(seed == 1)
#         n_gray  = np.sum(seed == 0)
#         n_none  = np.sum((seed == -1) & valid_mask)

#         print(f"  🟢 GREEN  : {100 * n_green / total_valid:.2f}%")
#         print(f"  🟠 AMBER  : {100 * n_amber / total_valid:.2f}%")
#         print(f"  ⚪ GRAY   : {100 * n_gray / total_valid:.2f}%")
#         print(f"  🟦 NONE   : {100 * n_none / total_valid:.2f}% (Clear Sky)")
#         print(f"  ☁️ Total Clouds Categorized: {n_green + n_amber + n_gray} pixels")
    
#     return seed

"""3 bands"""

# import numpy as np

# def decide_seedability(ctt_c, growth, swd, moisture_proxy, cloud_mask):
#     """
#     TRI-BAND DECISION ENGINE (B8, B13, B14)
#     B14 (SWD) filters out ice-phase clouds.
#     B08 (Moisture) ensures sufficient mid-level 'fuel' for seeding.
#     """
#     # Initialize with -1 (Transparent/Clear Sky)
#     seed = np.full(ctt_c.shape, -1, dtype=np.int8)
    
#     # Create a boolean mask of where clouds actually are
#     is_cloud = (cloud_mask == 1.0)

#     # 1. 🟢 GREEN: High Potential Seedable
#     # Requirements: 
#     # - Cold (<-10°C)
#     # - Growing (>1.5°C cooling)
#     # - Liquid-Rich (SWD < 0.6)
#     # - Mid-level Moisture (Moisture Proxy > -20K)
#     green_mask = (
#         is_cloud & 
#         (ctt_c <= -10.0) & 
#         (growth > 1.5) & 
#         (swd < 0.6) &
#         (moisture_proxy > -20.0) # <--- B08 Moisture Filter
#     )
#     seed[green_mask] = 2

#     # 2. 🟠 AMBER: Marginal/Watch Conditions
#     # Requirements: 
#     # - CTT between -5°C and -10°C
#     # - Sufficient mid-level moisture indicator
#     amber_mask = (
#         is_cloud & 
#         (ctt_c <= -5.0) & 
#         (growth > 0.5) & 
#         (moisture_proxy > -25.0) & # <--- B08 Watch Condition
#         (seed != 2)
#     )
#     seed[amber_mask] = 1

#     # 3. ⚪ GRAY: Do Not Seed (Ineffective)
#     # Catch-all for:
#     # - Ice-dominated clouds (>80% phase)
#     # - Too warm (>-5°C)
#     # - Dry clouds (Low moisture)
#     gray_mask = is_cloud & (seed == -1)
#     seed[gray_mask] = 0

#     # --- Robust Diagnostics ---
#     valid_mask = ~np.isnan(ctt_c)
#     total_valid = np.count_nonzero(valid_mask)
    
#     print("\n📊 Final Seedability Breakdown (Tri-Band):")
#     if total_valid > 0:
#         n_green = np.sum(seed == 2)
#         n_amber = np.sum(seed == 1)
#         n_gray  = np.sum(seed == 0)
#         n_none  = np.sum((seed == -1) & valid_mask)

#         print(f"  🟢 GREEN  : {100 * n_green / total_valid:.2f}%")
#         print(f"  🟠 AMBER  : {100 * n_amber / total_valid:.2f}%")
#         print(f"  ⚪ GRAY   : {100 * n_gray / total_valid:.2f}%")
#         print(f"  🟦 NONE   : {100 * n_none / total_valid:.2f}% (Clear Sky)")
#         print(f"  ☁️ Total Clouds Categorized: {n_green + n_amber + n_gray} pixels")
    
#     return seed
"""show sir"""
# import numpy as np


# def decide_seedability(ctt_c, growth, swd, depth_km, lwp_score, cloud_mask):
#     """
#     REAL-TIME PHYSICALLY ALIGNED SEEDABILITY DECISION ENGINE

#     Classification:
#         2  → GREEN  (High Potential)
#         1  → AMBER  (Marginal / Watch)
#         0  → GRAY   (Do Not Seed — STRICT DOC CONDITIONS ONLY)
#        -1 → NONE    (Transparent / Undetermined)
#     """

#     # -------------------------------------------------
#     # 0. Initialization
#     # -------------------------------------------------
#     seed = np.full(ctt_c.shape, -1, dtype=np.int8)

#     # -------------------------------------------------
#     # VALID PIXELS
#     # -------------------------------------------------
#     valid = ~np.isnan(ctt_c)

#     # -------------------------------------------------
#     # ROBUST CLOUD MASK VALIDATION
#     # (works for bool OR float masks)
#     # -------------------------------------------------
#     if cloud_mask.dtype == bool:
#         cloud_bool = cloud_mask
#     else:
#         # any positive value treated as cloud
#         cloud_bool = np.nan_to_num(cloud_mask) > 0.5

#     # FINAL CLOUD CONDITION
#     is_cloud = cloud_bool & valid

#     # growth > 0 → cooling
#     # growth < 0 → warming / collapse

#     # -------------------------------------------------
#     # 1. GREEN — HIGH POTENTIAL (DOC MATCH)
#     # -------------------------------------------------
#     green_mask = (
#         is_cloud &
#         (ctt_c <= -10.0) &
#         (growth >= 2.0) &
#         (depth_km >= 2.5) &
#         (lwp_score >= 0.7) &
#         (swd < 0.6)
#     )

#     seed[green_mask] = 2

#     # -------------------------------------------------
#     # 2. AMBER — MARGINAL (DOC MATCH)
#     # -------------------------------------------------
#     amber_mask = (
#         is_cloud &
#         (ctt_c > -10.0) & (ctt_c <= -5.0) &
#         (growth > 0.5) &
#         (depth_km >= 1.0) & (depth_km < 2.5) &
#         (lwp_score >= 0.3) &
#         (swd < 0.8) &
#         (seed == -1)
#     )

#     seed[amber_mask] = 1

#     # -------------------------------------------------
#     # 3. GRAY — STRICT DOCUMENT CONDITIONS ONLY
#     # (ONLY when doc explicitly says DO NOT SEED)
#     # -------------------------------------------------
#     gray_mask = (
#         is_cloud &
#         (
#             (ctt_c > -5.0) |
#             (
#                 (depth_km < 1.0) &
#                 (lwp_score < 0.3)
#             ) |
#             (
#                 (swd >= 0.8) &
#                 (growth <= 0)
#             )
#         )
#     )




#     seed[gray_mask] = 0

#     # -------------------------------------------------
#     # Remaining cloudy pixels stay NONE (-1)
#     # -------------------------------------------------

#     # -------------------------------------------------
#     # Diagnostics (CORRECT % CALCULATION)
#     # -------------------------------------------------
#     total_cloud = np.count_nonzero(is_cloud)

#     print("\n📊 Physically Aligned Seedability Breakdown:")

#     if total_cloud > 0:

#         n_green = np.count_nonzero((seed == 2) & is_cloud)
#         n_amber = np.count_nonzero((seed == 1) & is_cloud)
#         n_gray  = np.count_nonzero((seed == 0) & is_cloud)
#         n_none  = np.count_nonzero((seed == -1) & is_cloud)

#         print(f"  🟢 GREEN : {100*n_green/total_cloud:.2f}% (High Potential)")
#         print(f"  🟠 AMBER : {100*n_amber/total_cloud:.2f}% (Watch)")
#         print(f"  ⚪ GRAY  : {100*n_gray/total_cloud:.2f}% (Do Not Seed)")
#         print(f"  ⬜ NONE  : {100*n_none/total_cloud:.2f}% (Undetermined)")

#     return seed


"""lets see"""

import numpy as np


def decide_seedability(ctt_c, growth, swd, depth_km, lwp_score, cloud_mask):
    """
    REAL-TIME PHYSICALLY ALIGNED SEEDABILITY DECISION ENGINE

    Classification:
        2  → GREEN  (High Potential)
        1  → AMBER  (Marginal / Watch)
        0  → GRAY   (Do Not Seed — STRICT DOC CONDITIONS ONLY)
       -1 → NONE    (Transparent / Undetermined)
    """

    # -------------------------------------------------
    # 0. Initialization
    # -------------------------------------------------
    seed = np.full(ctt_c.shape, -1, dtype=np.int8)

    # -------------------------------------------------
    # VALID PIXELS
    # -------------------------------------------------
    valid = ~np.isnan(ctt_c)

    # -------------------------------------------------
    # ROBUST CLOUD MASK VALIDATION
    # -------------------------------------------------
    if cloud_mask.dtype == bool:
        cloud_bool = cloud_mask
    else:
        cloud_bool = np.nan_to_num(cloud_mask) > 0.5

    # FINAL CLOUD CONDITION
    is_cloud = cloud_bool & valid

    # -------------------------------------------------
    # 1. GREEN — HIGH POTENTIAL (DOC MATCH)
    # -------------------------------------------------
    green_mask = (
        is_cloud &
        (ctt_c <= -10.0) &
        (growth >= 2.0) &
        (depth_km >= 2.5) &
        (lwp_score >= 0.7) &
        (swd < 0.6)
    )

    seed[green_mask] = 2

    # -------------------------------------------------
    # 2. AMBER — MARGINAL (DOC MATCH)
    # -------------------------------------------------
    amber_mask = (
        is_cloud &
        (seed == -1) &   # only unclassified pixels
        (ctt_c > -10.0) & (ctt_c <= -5.0) &
        (growth > 0.5) &
        (depth_km >= 1.0) & (depth_km < 2.5) &
        (lwp_score >= 0.3) &
        (swd < 0.8)
    )

    seed[amber_mask] = 1

    # -------------------------------------------------
    # 3. GRAY — STRICT DOCUMENT CONDITIONS ONLY
    # (LOWEST PRIORITY — cannot overwrite GREEN/AMBER)
    # -------------------------------------------------
    gray_mask = (
        is_cloud &
        (seed == -1) &   # ⭐ CRITICAL FIX
        (
            (ctt_c > -5.0) |
            (
                (depth_km < 1.0) &
                (lwp_score < 0.3)
            ) |
            (
                (swd >= 0.8) &
                (growth <= 0)
            )
        )
    )

    seed[gray_mask] = 0

    # -------------------------------------------------
    # Diagnostics
    # -------------------------------------------------
    total_cloud = np.count_nonzero(is_cloud)

    print("\n📊 Physically Aligned Seedability Breakdown:")

    if total_cloud > 0:

        n_green = np.count_nonzero((seed == 2) & is_cloud)
        n_amber = np.count_nonzero((seed == 1) & is_cloud)
        n_gray  = np.count_nonzero((seed == 0) & is_cloud)
        n_none  = np.count_nonzero((seed == -1) & is_cloud)

        print(f"  🟢 GREEN : {100*n_green/total_cloud:.2f}% (High Potential)")
        print(f"  🟠 AMBER : {100*n_amber/total_cloud:.2f}% (Watch)")
        print(f"  ⚪ GRAY  : {100*n_gray/total_cloud:.2f}% (Do Not Seed)")
        print(f"  ⬜ NONE  : {100*n_none/total_cloud:.2f}% (Undetermined)")

    return seed
