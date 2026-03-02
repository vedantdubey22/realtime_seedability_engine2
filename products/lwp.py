# import numpy as np

# def compute_lwp_proxy(ctt_c, growth):
#     """
#     Proxy for supercooled liquid water presence.

#     Cold + cooling clouds favor SLW.
#     """
#     lwp = (-ctt_c / 20.0) * (growth > 0)
#     return np.clip(lwp, 0.0, 1.0)


"""3 bands and show sir"""

# import numpy as np

# def compute_lwp_proxy(bt08_crop, bt13_crop):
#     """
#     Refined SLW-rich cloud proxy (Targeting 20-35 dBZ reflectivity).
#     Uses the Brightness Temperature Difference (BTD) between B08 and B13.
#     """
#     # BTD (B08 - B13) is a standard indicator for mid-level moisture saturation.
#     # Closer to 0 indicates a deep, moisture-saturated (potentially liquid-rich) layer.
#     lwp_diff = bt08_crop - bt13_crop
    
#     # Per documentation: 20-35 dBZ is typical of SLW-rich clouds.
#     # We normalize this so that higher values (closer to -10K) represent 
#     # the 'Sweet Spot' for liquid water path.
#     lwp_score = np.clip((lwp_diff + 40) / 30, 0.0, 1.0)
    
#     # Mask out areas that are likely too dry for the 20dBZ threshold.
#     lwp_score[lwp_diff < -35.0] = 0.0
    
#     return lwp_score

import numpy as np


def compute_lwp_proxy(bt08_crop: np.ndarray,
                      bt13_crop: np.ndarray) -> np.ndarray:
    """
    Physically-aligned Liquid Water Path (LWP) proxy.

    Uses Brightness Temperature Difference:
        BTD = B08 - B13

    Physical interpretation:
        - Very negative  → dry atmosphere
        - Moderate diff  → moist deep cloud (SLW candidate)
        - Near zero      → saturated thick cloud

    Returns:
        lwp_score (0 → dry, 1 → liquid rich)
    """

    # -------------------------------------------------
    # Brightness Temperature Difference
    # -------------------------------------------------
    btd = bt08_crop - bt13_crop

    # -------------------------------------------------
    # SLW SWEET SPOT
    # Target ≈ -12K (empirical Himawari behavior)
    # -------------------------------------------------
    center = -12.0
    width = 10.0

    # Gaussian-like response
    lwp_score = np.exp(-((btd - center) ** 2) / (2 * width ** 2))

    # -------------------------------------------------
    # HARD PHYSICAL FILTERS
    # -------------------------------------------------

    # extremely dry atmosphere
    lwp_score[btd < -35.0] = 0.0

    # unrealistic warm noise
    lwp_score[btd > 5.0] = 0.0

    # normalize safety
    lwp_score = np.clip(lwp_score, 0.0, 1.0)

    # -------------------------------------------------
    # Diagnostics
    # -------------------------------------------------
    valid = ~np.isnan(lwp_score)

    if np.count_nonzero(valid) > 0:
        print("\n💧 LWP Proxy diagnostics:")
        print(f"  Mean score : {np.nanmean(lwp_score):.3f}")
        print(f"  High LWP (>0.7) : {np.mean(lwp_score > 0.7)*100:.2f}%")

    return lwp_score
