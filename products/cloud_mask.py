
""" to show sir"""
# import numpy as np

# def compute_cloud_mask(ctt_c: np.ndarray) -> np.ndarray:
#     """
#     Deterministic Cloud Mask aligned with documentation.

#     Cloud defined as:
#     CTT <= -5°C
#     """

#     mask = np.full(ctt_c.shape, np.nan)

#     valid = ~np.isnan(ctt_c)
#     mask[valid] = (ctt_c[valid] <= -5.0).astype(float)

#     print("\n☁️ Cloud mask diagnostics (Doc-Aligned):")

#     total_valid = np.count_nonzero(valid)
#     if total_valid > 0:
#         cloud_pixels = np.sum(mask == 1.0)
#         print(f"  Threshold Applied: -5.0°C")
#         print(f"  % Cloud pixels detected: {100 * cloud_pixels / total_valid:.2f}%")

#     return mask

""" lets see"""

import numpy as np


def compute_cloud_mask(
    ctt_c: np.ndarray,
    lwp_score: np.ndarray | None = None
) -> np.ndarray:
    """
    Deterministic Cloud Mask (Physically + Doc aligned)

    Documentation base rule:
        Cloud if CTT <= -5°C

    Physical refinement (required for geostationary IR):
        Remove cold surface / dry atmosphere false clouds
        using liquid-water proxy (LWP).

    Returns:
        mask :
            1.0 → cloud
            0.0 → clear
            NaN → invalid pixel
    """

    # -------------------------------------------------
    # Initialize
    # -------------------------------------------------
    mask = np.full(ctt_c.shape, np.nan, dtype=np.float32)

    valid = ~np.isnan(ctt_c)

    # -------------------------------------------------
    # STEP 1 — DOC CONDITION
    # -------------------------------------------------
    cloud_cond = (ctt_c <= -5.0)

    # -------------------------------------------------
    # STEP 2 — PHYSICAL FILTER (VERY IMPORTANT)
    # Remove desert / cold ground false detections
    # -------------------------------------------------
    if lwp_score is not None:
        # weak liquid water → not real cloud
        cloud_cond = cloud_cond & (lwp_score > 0.2)

    # -------------------------------------------------
    # Apply mask
    # -------------------------------------------------
    mask[valid] = cloud_cond[valid].astype(np.float32)

    # -------------------------------------------------
    # Diagnostics
    # -------------------------------------------------
    print("\n☁️ Cloud mask diagnostics (Physically Aligned):")

    total_valid = np.count_nonzero(valid)

    if total_valid > 0:
        cloud_pixels = np.count_nonzero(mask == 1.0)
        clear_pixels = np.count_nonzero(mask == 0.0)

        print("  Base Threshold : CTT <= -5°C")
        if lwp_score is not None:
            print("  Liquid Filter  : LWP score > 0.2 enabled")

        print(f"  % Cloud pixels : {100 * cloud_pixels / total_valid:.2f}%")
        print(f"  % Clear pixels : {100 * clear_pixels / total_valid:.2f}%")

    return mask
