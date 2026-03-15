# import numpy as np

# def compute_growth_rate(ctt_curr: np.ndarray,
#                         ctt_prev: np.ndarray) -> np.ndarray:
#     """
#     Cloud-top cooling rate (°C per 10 min)

#     Positive → cooling → vertical growth
#     Negative → warming → decay
#     """

#     # Pixel-wise subtraction; NaNs in either array will result in a NaN in 'growth'
#     growth = ctt_prev - ctt_curr

#     # 🔥 FIX: Use nan-aware stats to ignore masked background/space
#     print("\n📈 Growth diagnostics:")
#     print("  Min:", np.nanmin(growth))
#     print("  Max:", np.nanmax(growth))
#     print("  Mean:", np.nanmean(growth))

#     # 🔥 FIX: Use np.nansum to calculate percentages correctly. 
#     # Standard np.sum would return 'nan' if any element is nan.
    
#     # Total count of valid (non-nan) pixels for accurate percentage calculation
#     valid_count = np.count_nonzero(~np.isnan(growth))
    
#     if valid_count > 0:
#         strong_cooling = np.nansum(growth > 2.0)
#         near_zero = np.nansum((growth > -1.0) & (growth < 1.0))
#         warming = np.nansum(growth < -1.0)

#         print(f"  % Strong cooling (> +2°C): {100 * strong_cooling / valid_count:.2f}%")
#         print(f"  % Near zero (-1 to +1°C): {100 * near_zero / valid_count:.2f}%")
#         print(f"  % Warming (< -1°C): {100 * warming / valid_count:.2f}%")
#     else:
#         print("  ⚠️ No valid pixels found for growth calculation.")

#     return growth
"""show sir"""
# import numpy as np

# def compute_growth_rate(ctt_curr: np.ndarray,
#                         ctt_prev: np.ndarray,
#                         time_interval_min: float = 10.0) -> np.ndarray:
#     """
#     Cloud-top cooling rate normalized to °C per 10 minutes.

#     Positive → cooling → vertical growth
#     Negative → warming → decay
#     """

#     # Raw temperature difference
#     delta_t = ctt_prev - ctt_curr

#     # Normalize to per 10 min rate
#     growth = delta_t * (10.0 / time_interval_min)

#     # Small fluctuation suppression (sensor noise)
#     growth[np.abs(growth) < 0.2] = 0

#     print("\n📈 Growth diagnostics:")
#     print("  Min:", np.nanmin(growth))
#     print("  Max:", np.nanmax(growth))
#     print("  Mean:", np.nanmean(growth))

#     valid_count = np.count_nonzero(~np.isnan(growth))

#     if valid_count > 0:
#         strong_cooling = np.nansum(growth > 2.0)
#         near_zero = np.nansum((growth > -1.0) & (growth < 1.0))
#         warming = np.nansum(growth < -1.0)

#         print(f"  % Strong cooling (> +2°C): {100 * strong_cooling / valid_count:.2f}%")
#         print(f"  % Near zero (-1 to +1°C): {100 * near_zero / valid_count:.2f}%")
#         print(f"  % Warming (< -1°C): {100 * warming / valid_count:.2f}%")
#     else:
#         print("  ⚠️ No valid pixels found for growth calculation.")

#     return growth

import numpy as np

def compute_growth_rate(ctt_curr: np.ndarray,
                        ctt_prev: np.ndarray,
                        time_interval_min: float = 10.0) -> np.ndarray:
    """
    Cloud-top cooling rate (°C / 10 min)

    Positive → cooling → vertical growth
    Negative → warming → decay

    Doc requirement:
    Strong growth ≈ IR cooling > 2°C / 10 min
    """

    # -------------------------------------------------
    # Temperature change
    # -------------------------------------------------
    delta_t = ctt_prev - ctt_curr

    # Normalize to 10-minute rate
    growth = delta_t * (10.0 / time_interval_min)

    # -------------------------------------------------
    # Remove tiny sensor noise (less aggressive)
    # -------------------------------------------------
    growth[np.abs(growth) < 0.5] = 0.0

    # -------------------------------------------------
    # Invalid pixels cleanup
    # -------------------------------------------------
    invalid = np.isnan(ctt_curr) | np.isnan(ctt_prev)
    growth[invalid] = np.nan

    # -------------------------------------------------
    # Diagnostics
    # -------------------------------------------------
    print("\n📈 Growth diagnostics:")

    if np.all(np.isnan(growth)):
        print("  ⚠️ No valid pixels.")
        return growth

    print("  Min:", np.nanmin(growth))
    print("  Max:", np.nanmax(growth))
    print("  Mean:", np.nanmean(growth))

    valid_count = np.count_nonzero(~np.isnan(growth))

    strong_cooling = np.nansum(growth > 2.0)
    near_zero = np.nansum((growth >= -1.0) & (growth <= 1.0))
    warming = np.nansum(growth < -1.0)

    print(f"  % Strong cooling (> +2°C): {100 * strong_cooling / valid_count:.2f}%")
    print(f"  % Near zero (-1 to +1°C): {100 * near_zero / valid_count:.2f}%")
    print(f"  % Warming (< -1°C): {100 * warming / valid_count:.2f}%")

    return growth
